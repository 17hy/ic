from __future__ import annotations

import argparse
import csv
import math
import subprocess
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated_netlists"
LOGS = ROOT / "logs"
RAW = ROOT / "raw"
RESULTS = ROOT / "results"
PLOTS = ROOT / "plots"
MODEL_REL = "../models/chapter7_cmos.inc"
VDD = 2.5
LCH = 0.25e-6


def ensure_dirs() -> None:
    for path in (GENERATED, LOGS, RAW, RESULTS, PLOTS):
        path.mkdir(parents=True, exist_ok=True)


def spice_num(value: float) -> str:
    return f"{value:.8g}"


def run_ngspice(ngspice: Path, name: str, netlist: str) -> Path:
    netlist_path = GENERATED / f"{name}.cir"
    log_path = LOGS / f"{name}.log"
    netlist_path.write_text(netlist, encoding="ascii")
    proc = subprocess.run(
        [str(ngspice), "-b", "-o", str(log_path), netlist_path.name],
        cwd=GENERATED,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        tail = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-40:]
        raise RuntimeError(f"ngspice failed for {name}\n" + "\n".join(tail))
    return RAW / f"{name}.dat"


def is_float(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def load_wrdata(path: Path) -> np.ndarray:
    lines = [line for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    first = lines[0].split()
    data = np.loadtxt(path, skiprows=0 if all(is_float(t) for t in first) else 1)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[1] >= 2 and np.allclose(data[:, 0], data[:, 1], rtol=1e-9, atol=1e-18):
        data = data[:, 1:]
    return data


def crossing_time(t: np.ndarray, y: np.ndarray, level: float, edge: str, start_after: float = -math.inf) -> float:
    for idx in range(1, len(t)):
        if t[idx] < start_after:
            continue
        y0, y1 = y[idx - 1], y[idx]
        hit = y0 < level <= y1 if edge == "rise" else y0 > level >= y1
        if not hit:
            continue
        if y1 == y0:
            return float(t[idx])
        frac = (level - y0) / (y1 - y0)
        return float(t[idx - 1] + frac * (t[idx] - t[idx - 1]))
    return float("nan")


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def bistable_netlist(name: str) -> str:
    return f"""* {name}: cross-coupled inverter regeneration
.include {MODEL_REL}
Vdd vdd 0 {spice_num(VDD)}
X1 q qb vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
X2 qb q vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
Cq q 0 20f
Cqb qb 0 20f
.ic v(q)=1.20 v(qb)=1.30
.control
set noaskquit
set wr_singlescale
set wr_vecnames
tran 0.5p 2n uic
wrdata ../raw/{name}.dat time v(q) v(qb)
quit
.endc
.end
"""


def tg_latch_netlist(name: str) -> str:
    return f"""* {name}: transmission-gate positive latch
.include {MODEL_REL}
.subckt tg in out clk clkb vdd
Mn out clk in 0 NMOS W=1.4u L={spice_num(LCH)}
Mp out clkb in vdd PMOS W=2.8u L={spice_num(LCH)}
.ends tg
Vdd vdd 0 {spice_num(VDD)}
Vclk clk 0 PULSE(0 {spice_num(VDD)} 0.1n 20p 20p 0.75n 1.5n)
Vclkb clkb 0 PULSE({spice_num(VDD)} 0 0.1n 20p 20p 0.75n 1.5n)
Vd d 0 PULSE(0 {spice_num(VDD)} 0.35n 20p 20p 1.1n 2.2n)
Xin d n clk clkb vdd tg
Xinv1 n q vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
Xinv2 q nf vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
Xfb nf n clkb clk vdd tg
Cn n 0 15f
Cq q 0 25f
.control
set noaskquit
set wr_singlescale
set wr_vecnames
tran 1p 5n
wrdata ../raw/{name}.dat time v(clk) v(d) v(n) v(q)
quit
.endc
.end
"""


def schmitt_netlist(name: str) -> str:
    return f"""* {name}: ngspice switch Schmitt trigger macro
Vdd vdd 0 {spice_num(VDD)}
Vin in 0 PWL(0 0 0.5u 0 2.5u {spice_num(VDD)} 3.2u {spice_num(VDD)} 5.2u 0 6u 0)
Rpu vdd out 2k
Sdn out 0 in 0 smod
Cout out 0 20f
.model smod SW(Ron=120 Roff=1e9 Vt=1.25 Vh=0.35)
.control
set noaskquit
set wr_singlescale
set wr_vecnames
tran 2n 6u
wrdata ../raw/{name}.dat time v(in) v(out)
quit
.endc
.end
"""


def ring_netlist(name: str) -> str:
    return f"""* {name}: five-stage CMOS ring oscillator
.include {MODEL_REL}
Vdd vdd 0 {spice_num(VDD)}
X1 n5 n1 vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
X2 n1 n2 vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
X3 n2 n3 vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
X4 n3 n4 vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
X5 n4 n5 vdd inv wnn=1u wpp=2.75u lch={spice_num(LCH)}
C1 n1 0 20f
C2 n2 0 20f
C3 n3 0 20f
C4 n4 0 20f
C5 n5 0 20f
.ic v(n1)=0 v(n2)=0 v(n3)=0 v(n4)=0 v(n5)={spice_num(VDD)}
.control
set noaskquit
set wr_singlescale
set wr_vecnames
tran 1p 20n uic
wrdata ../raw/{name}.dat time v(n1) v(n2) v(n3) v(n4) v(n5)
quit
.endc
.end
"""


def plot_bistable(data: np.ndarray) -> dict[str, float | str]:
    t_ns = data[:, 0] * 1e9
    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=160)
    ax.plot(t_ns, data[:, 1], label="Q", linewidth=1.8)
    ax.plot(t_ns, data[:, 2], label="QB", linewidth=1.8)
    ax.axhline(VDD / 2, color="#777777", linestyle="--", linewidth=1)
    ax.set_title("Cross-coupled inverter regeneration")
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig7_bistable_regeneration.png")
    plt.close(fig)
    final_state = "Q=1" if data[-1, 1] > data[-1, 2] else "Q=0"
    return {"experiment": "bistable_regeneration", "final_state": final_state, "q_final_v": float(data[-1, 1]), "qb_final_v": float(data[-1, 2])}


def plot_latch(data: np.ndarray) -> dict[str, float | str]:
    t_ns = data[:, 0] * 1e9
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 5.8), dpi=160, sharex=True)
    axes[0].plot(t_ns, data[:, 1], label="CLK", linewidth=1.6)
    axes[0].plot(t_ns, data[:, 2], label="D", linewidth=1.6)
    axes[0].set_ylabel("Inputs (V)")
    axes[0].set_title("Transmission-gate latch")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(frameon=False, ncol=2)
    axes[1].plot(t_ns, data[:, 3], label="internal N", linewidth=1.6)
    axes[1].plot(t_ns, data[:, 4], label="Q = inv(N)", linewidth=1.6)
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("State (V)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig7_tg_latch_waveforms.png")
    plt.close(fig)
    return {"experiment": "tg_latch", "q_min_v": float(np.min(data[:, 4])), "q_max_v": float(np.max(data[:, 4]))}


def plot_schmitt(data: np.ndarray) -> dict[str, float | str]:
    t_us = data[:, 0] * 1e6
    vin, vout = data[:, 1], data[:, 2]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), dpi=160)
    axes[0].plot(t_us, vin, label="Vin", linewidth=1.6)
    axes[0].plot(t_us, vout, label="Vout", linewidth=1.6)
    axes[0].set_title("Slow input cleanup")
    axes[0].set_xlabel("Time (us)")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(frameon=False)
    axes[1].plot(vin, vout, linewidth=1.6, color="#b13f2d")
    axes[1].set_title("Schmitt hysteresis")
    axes[1].set_xlabel("Vin (V)")
    axes[1].set_ylabel("Vout (V)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig7_schmitt_hysteresis.png")
    plt.close(fig)
    mid = VDD / 2
    rise_trip_t = crossing_time(data[:, 0], vout, mid, "fall")
    fall_trip_t = crossing_time(data[:, 0], vout, mid, "rise", rise_trip_t)
    rise_trip_v = float(np.interp(rise_trip_t, data[:, 0], vin))
    fall_trip_v = float(np.interp(fall_trip_t, data[:, 0], vin))
    return {"experiment": "schmitt_trigger", "vth_rise_v": rise_trip_v, "vth_fall_v": fall_trip_v, "hysteresis_v": rise_trip_v - fall_trip_v}


def plot_ring(data: np.ndarray) -> dict[str, float | str]:
    t_ns = data[:, 0] * 1e9
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=160)
    for idx, label in enumerate(("n1", "n2", "n3")):
        ax.plot(t_ns, data[:, idx + 1], label=label, linewidth=1.4)
    ax.set_title("Five-stage CMOS ring oscillator")
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig7_ring_oscillator.png")
    plt.close(fig)
    t = data[:, 0]
    n1 = data[:, 1]
    crossings: list[float] = []
    start = t[0]
    while True:
        c = crossing_time(t, n1, VDD / 2, "rise", start)
        if math.isnan(c):
            break
        crossings.append(c)
        start = c + 1e-12
    usable = [c for c in crossings if c > 5e-9]
    if len(usable) >= 2:
        periods = np.diff(usable)
        period = float(np.mean(periods))
        freq = 1.0 / period
    else:
        period = float("nan")
        freq = float("nan")
    return {"experiment": "ring_oscillator", "period_ns": period * 1e9, "frequency_mhz": freq / 1e6}


def run_all(ngspice: Path) -> None:
    ensure_dirs()
    rows: list[dict[str, float | str]] = []
    rows.append(plot_bistable(load_wrdata(run_ngspice(ngspice, "bistable_regeneration", bistable_netlist("bistable_regeneration")))))
    rows.append(plot_latch(load_wrdata(run_ngspice(ngspice, "tg_latch", tg_latch_netlist("tg_latch")))))
    rows.append(plot_schmitt(load_wrdata(run_ngspice(ngspice, "schmitt_hysteresis", schmitt_netlist("schmitt_hysteresis")))))
    rows.append(plot_ring(load_wrdata(run_ngspice(ngspice, "ring_oscillator", ring_netlist("ring_oscillator")))))
    write_csv(RESULTS / "summary_metrics.csv", rows)
    print(f"plots: {PLOTS}")
    print(f"metrics: {RESULTS / 'summary_metrics.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ngspice", type=Path, default=ROOT.parents[2] / "Spice64" / "bin" / "ngspice_con.exe")
    args = parser.parse_args()
    run_all(args.ngspice)


if __name__ == "__main__":
    main()
