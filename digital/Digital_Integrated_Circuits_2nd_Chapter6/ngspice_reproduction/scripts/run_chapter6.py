from __future__ import annotations

import argparse
import csv
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
MODEL_REL = "../models/chapter6_cmos.inc"
VDD = 2.5
LCH = 0.25e-6


def ensure_dirs() -> None:
    for p in (GENERATED, LOGS, RAW, RESULTS, PLOTS):
        p.mkdir(parents=True, exist_ok=True)


def fnum(x: float) -> str:
    return f"{x:.8g}"


def run_ngspice(ngspice: Path, name: str, netlist: str) -> Path:
    net = GENERATED / f"{name}.cir"
    log = LOGS / f"{name}.log"
    net.write_text(netlist, encoding="ascii")
    proc = subprocess.run([str(ngspice), "-b", "-o", str(log), net.name], cwd=GENERATED, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        tail = log.read_text(encoding="utf-8", errors="ignore").splitlines()[-40:]
        raise RuntimeError(f"ngspice failed for {name}\n" + "\n".join(tail))
    return RAW / f"{name}.dat"


def load_wrdata(path: Path) -> np.ndarray:
    data = np.loadtxt(path, skiprows=1)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[1] >= 2 and np.allclose(data[:, 0], data[:, 1]):
        data = data[:, 1:]
    return data


def crossing_time(t: np.ndarray, y: np.ndarray, level: float, edge: str, start: float = -1e99) -> float:
    for i in range(1, len(t)):
        if t[i] < start:
            continue
        y0, y1 = y[i - 1], y[i]
        hit = (y0 < level <= y1) if edge == "rise" else (y0 > level >= y1)
        if not hit:
            continue
        if y1 == y0:
            return float(t[i])
        k = (level - y0) / (y1 - y0)
        return float(t[i - 1] + k * (t[i] - t[i - 1]))
    return float("nan")


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for k in row.keys():
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def netlist_static_nand(name: str, mode: str) -> str:
    b_src = {
        "b0": "Vb b 0 0",
        "b1": f"Vb b 0 {fnum(VDD)}",
        "tied": "Vb b a 0",
    }[mode]
    return f"""* {name}: static CMOS NAND DC
.include {MODEL_REL}
Vdd vdd 0 {fnum(VDD)}
Va a 0 0
{b_src}
Mp1 out a vdd vdd PMOS W=2.75u L={fnum(LCH)}
Mp2 out b vdd vdd PMOS W=2.75u L={fnum(LCH)}
Mn1 out a n1 0 NMOS W=1u L={fnum(LCH)}
Mn2 n1 b 0 0 NMOS W=1u L={fnum(LCH)}
.control
set noaskquit
set wr_vecnames
set wr_singlescale
dc Va 0 {fnum(VDD)} 0.0025
wrdata ../raw/{name}.dat v(a) v(out) i(vdd)
quit
.endc
.end
"""


def netlist_static_nand_tran(name: str) -> str:
    return f"""* {name}: static CMOS NAND transient
.include {MODEL_REL}
Vdd vdd 0 {fnum(VDD)}
Va a 0 PULSE(0 {fnum(VDD)} 0.2n 20p 20p 0.6n 1.2n)
Vb b 0 {fnum(VDD)}
Mp1 out a vdd vdd PMOS W=2.75u L={fnum(LCH)}
Mp2 out b vdd vdd PMOS W=2.75u L={fnum(LCH)}
Mn1 out a n1 0 NMOS W=1u L={fnum(LCH)}
Mn2 n1 b 0 0 NMOS W=1u L={fnum(LCH)}
Cload out 0 30f
.control
set noaskquit
set wr_vecnames
set wr_singlescale
tran 1p 2.4n
wrdata ../raw/{name}.dat time v(a) v(out) i(vdd)
quit
.endc
.end
"""


def netlist_pseudo_nmos(name: str) -> str:
    return f"""* {name}: pseudo-NMOS NAND DC
.include {MODEL_REL}
Vdd vdd 0 {fnum(VDD)}
Va a 0 0
Vb b a 0
Mp out 0 vdd vdd PMOS W=1u L={fnum(LCH)}
Mn1 out a n1 0 NMOS W=1u L={fnum(LCH)}
Mn2 n1 b 0 0 NMOS W=1u L={fnum(LCH)}
.control
set noaskquit
set wr_vecnames
set wr_singlescale
dc Va 0 {fnum(VDD)} 0.0025
wrdata ../raw/{name}.dat v(a) v(out) i(vdd)
quit
.endc
.end
"""


def netlist_dynamic_nand(name: str) -> str:
    return f"""* {name}: dynamic NAND (precharge/evaluate) with output inverter
.include {MODEL_REL}
Vdd vdd 0 {fnum(VDD)}
Vclk clk 0 PULSE(0 {fnum(VDD)} 0 20p 20p 0.5n 1n)
Bclkb clkb 0 v={{ {fnum(VDD)} - v(clk) }}
Va a 0 PULSE(0 {fnum(VDD)} 0.1n 20p 20p 1.0n 2.0n)
Vb b 0 PULSE(0 {fnum(VDD)} 0.6n 20p 20p 1.0n 2.0n)
Mpchg x clkb vdd vdd PMOS W=2.5u L={fnum(LCH)}
Mn1 x a n1 0 NMOS W=1u L={fnum(LCH)}
Mn2 n1 b n2 0 NMOS W=1u L={fnum(LCH)}
Mneval n2 clk 0 0 NMOS W=1u L={fnum(LCH)}
Minvp y x vdd vdd PMOS W=2.5u L={fnum(LCH)}
Minvn y x 0 0 NMOS W=1u L={fnum(LCH)}
Cx x 0 8f
Cy y 0 20f
.control
set noaskquit
set wr_vecnames
set wr_singlescale
tran 1p 4n
wrdata ../raw/{name}.dat time v(clk) v(a) v(b) v(x) v(y)
quit
.endc
.end
"""


def plot_static_vtc(rows: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), dpi=160)
    labels = {"b0": "B=0", "b1": "B=VDD", "tied": "A=B"}
    for key, data in rows.items():
        axes[0].plot(data[:, 0], data[:, 1], linewidth=1.8, label=labels[key])
    axes[0].plot(rows["tied"][:, 0], rows["tied"][:, 0], "--", linewidth=1.0, color="#777")
    axes[0].set_title("Static CMOS NAND VTC")
    axes[0].set_xlabel("Input A (V)")
    axes[0].set_ylabel("Output (V)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(frameon=False)
    for key, data in rows.items():
        axes[1].plot(data[:, 0], -np.gradient(data[:, 1], data[:, 0]), linewidth=1.8, label=labels[key])
    axes[1].set_title("Voltage Gain")
    axes[1].set_xlabel("Input A (V)")
    axes[1].set_ylabel("-dVout/dVin")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig6_static_cmos_nand_vtc.png")
    plt.close(fig)


def plot_static_tran(data: np.ndarray, tphl_ps: float, tplh_ps: float) -> None:
    tns = data[:, 0] * 1e9
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 5.8), dpi=160, sharex=True)
    axes[0].plot(tns, data[:, 1], label="A", linewidth=1.6)
    axes[0].plot(tns, data[:, 2], label="OUT", linewidth=1.6)
    axes[0].axhline(0.5 * VDD, linestyle="--", linewidth=1, color="#777")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].set_title(f"Static NAND transient (tpHL={tphl_ps:.1f} ps, tpLH={tplh_ps:.1f} ps)")
    axes[0].legend(frameon=False)
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(tns, -data[:, 3] * 1e3, color="#b13f2d", linewidth=1.5)
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("I(VDD) (mA)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig6_static_cmos_nand_delay.png")
    plt.close(fig)


def plot_pseudo_nmos(data: np.ndarray) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), dpi=160)
    axes[0].plot(data[:, 0], data[:, 1], linewidth=1.8, color="#1f6f8b")
    axes[0].set_title("Pseudo-NMOS transfer")
    axes[0].set_xlabel("Input (A=B) (V)")
    axes[0].set_ylabel("Output (V)")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(data[:, 0], -data[:, 2] * 1e6, linewidth=1.8, color="#b13f2d")
    axes[1].set_title("Static current penalty")
    axes[1].set_xlabel("Input (A=B) (V)")
    axes[1].set_ylabel("I(VDD) (uA)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig6_ratioed_pseudo_nmos.png")
    plt.close(fig)


def plot_dynamic(data: np.ndarray) -> None:
    tns = data[:, 0] * 1e9
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.0), dpi=160, sharex=True)
    axes[0].plot(tns, data[:, 1], label="CLK", linewidth=1.6)
    axes[0].plot(tns, data[:, 2], label="A", linewidth=1.4)
    axes[0].plot(tns, data[:, 3], label="B", linewidth=1.4)
    axes[0].set_ylabel("Inputs (V)")
    axes[0].set_title("Dynamic NAND: precharge/evaluate timing")
    axes[0].legend(frameon=False, ncol=3)
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(tns, data[:, 4], label="X (dynamic node)", linewidth=1.6)
    axes[1].plot(tns, data[:, 5], label="Y (buffered output)", linewidth=1.6)
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("Node voltage (V)")
    axes[1].legend(frameon=False)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig6_dynamic_nand_waveforms.png")
    plt.close(fig)


def run_all(ngspice: Path) -> None:
    ensure_dirs()
    metrics: list[dict[str, float | str]] = []

    static_cases: dict[str, np.ndarray] = {}
    for mode in ("b0", "b1", "tied"):
        name = f"static_nand_vtc_{mode}"
        static_cases[mode] = load_wrdata(run_ngspice(ngspice, name, netlist_static_nand(name, mode)))
    plot_static_vtc(static_cases)

    tran = load_wrdata(run_ngspice(ngspice, "static_nand_tran", netlist_static_nand_tran("static_nand_tran")))
    mid = 0.5 * VDD
    tin_r = crossing_time(tran[:, 0], tran[:, 1], mid, "rise")
    tout_f = crossing_time(tran[:, 0], tran[:, 2], mid, "fall", tin_r)
    tin_f = crossing_time(tran[:, 0], tran[:, 1], mid, "fall", tin_r)
    tout_r = crossing_time(tran[:, 0], tran[:, 2], mid, "rise", tin_f)
    tphl = (tout_f - tin_r) * 1e12
    tplh = (tout_r - tin_f) * 1e12
    metrics.append({"experiment": "static_nand_delay", "tphl_ps": tphl, "tplh_ps": tplh, "tp_avg_ps": 0.5 * (tphl + tplh)})
    plot_static_tran(tran, tphl, tplh)

    pseudo = load_wrdata(run_ngspice(ngspice, "pseudo_nmos_vtc", netlist_pseudo_nmos("pseudo_nmos_vtc")))
    i_low = float(-pseudo[0, 2] * 1e6)
    i_high = float(-pseudo[-1, 2] * 1e6)
    metrics.append({"experiment": "pseudo_nmos_static_current", "idd_in0_uA": i_low, "idd_in1_uA": i_high, "delta_uA": i_high - i_low})
    plot_pseudo_nmos(pseudo)

    dyn = load_wrdata(run_ngspice(ngspice, "dynamic_nand_tran", netlist_dynamic_nand("dynamic_nand_tran")))
    metrics.append({"experiment": "dynamic_nand", "x_min_v": float(np.min(dyn[:, 4])), "x_max_v": float(np.max(dyn[:, 4]))})
    plot_dynamic(dyn)

    write_csv(RESULTS / "summary_metrics.csv", metrics)
    print(f"plots: {PLOTS}")
    print(f"metrics: {RESULTS / 'summary_metrics.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ngspice", type=Path, default=ROOT.parents[2] / "Spice64" / "bin" / "ngspice_con.exe")
    args = parser.parse_args()
    run_all(args.ngspice)


if __name__ == "__main__":
    main()
