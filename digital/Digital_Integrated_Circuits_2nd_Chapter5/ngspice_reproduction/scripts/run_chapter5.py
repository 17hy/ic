from __future__ import annotations

import argparse
import csv
import math
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated_netlists"
LOGS = ROOT / "logs"
RAW = ROOT / "raw"
RESULTS = ROOT / "results"
PLOTS = ROOT / "plots"

VDD_NOM = 2.5
WN0 = 1e-6
WP0 = 2.75e-6
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
    lines = [
        line
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip()
    ]
    if not lines:
        raise ValueError(f"empty data file: {path}")
    first = lines[0].split()
    skiprows = 0 if all(is_float(token) for token in first) else 1
    data = np.loadtxt(path, skiprows=skiprows)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[1] >= 2 and np.allclose(data[:, 0], data[:, 1], rtol=1e-9, atol=1e-18):
        data = data[:, 1:]
    return data


def static_netlist(name: str, vdd: float, wp: float = WP0, wn: float = WN0) -> str:
    step = max(vdd / 600.0, 0.001)
    return f"""* {name}: CMOS inverter DC transfer curve
.include ../models/chapter5_cmos.inc
Vdd vdd 0 {spice_num(vdd)}
Vin in 0 0
Xinv in out vdd inv wnn={spice_num(wn)} wpp={spice_num(wp)} lch={spice_num(LCH)}

.control
set noaskquit
set wr_singlescale
set wr_vecnames
dc Vin 0 {spice_num(vdd)} {spice_num(step)}
wrdata ../raw/{name}.dat v(in) v(out) i(vdd)
quit
.endc
.end
"""


def transient_netlist(
    name: str,
    vdd: float = VDD_NOM,
    cload: float = 20e-15,
    trf: float = 20e-12,
    period: float = 2e-9,
    cycles: int = 4,
    wp: float = WP0,
    wn: float = WN0,
) -> str:
    high_time = 0.45 * period
    delay = 0.1 * period
    tstop = cycles * period + delay
    tstep = min(period / 2000.0, trf / 8.0)
    return f"""* {name}: CMOS inverter transient response
.include ../models/chapter5_cmos.inc
Vdd vdd 0 {spice_num(vdd)}
Vin in 0 PULSE(0 {spice_num(vdd)} {spice_num(delay)} {spice_num(trf)} {spice_num(trf)} {spice_num(high_time)} {spice_num(period)})
Xinv in out vdd inv wnn={spice_num(wn)} wpp={spice_num(wp)} lch={spice_num(LCH)}
Cload out 0 {spice_num(cload)}

.control
set noaskquit
set wr_singlescale
set wr_vecnames
tran {spice_num(tstep)} {spice_num(tstop)}
wrdata ../raw/{name}.dat time v(in) v(out) i(vdd)
quit
.endc
.end
"""


def chain_netlist(name: str, stages: int, cext: float, vdd: float = VDD_NOM) -> str:
    total_fanout = max(cext / 3e-15, 1.0)
    scale_step = total_fanout ** (1.0 / stages)
    lines = [
        f"* {name}: {stages}-stage inverter buffer chain",
        ".include ../models/chapter5_cmos.inc",
        f"Vdd vdd 0 {spice_num(vdd)}",
        f"Vin in 0 PULSE(0 {spice_num(vdd)} 0.2n 20p 20p 1n 2n)",
    ]
    for idx in range(stages):
        inp = "in" if idx == 0 else f"n{idx}"
        out = "out" if idx == stages - 1 else f"n{idx + 1}"
        scale = scale_step**idx
        lines.append(
            "X{idx} {inp} {out} vdd inv wnn={wn} wpp={wp} lch={lch}".format(
                idx=idx + 1,
                inp=inp,
                out=out,
                wn=spice_num(WN0 * scale),
                wp=spice_num(WP0 * scale),
                lch=spice_num(LCH),
            )
        )
    lines.extend(
        [
            f"Cload out 0 {spice_num(cext)}",
            "",
            ".control",
            "set noaskquit",
            "set wr_singlescale",
            "set wr_vecnames",
            "tran 1p 10n",
            f"wrdata ../raw/{name}.dat time v(in) v(out) i(vdd)",
            "quit",
            ".endc",
            ".end",
        ]
    )
    return "\n".join(lines) + "\n"


def crossing_time(
    t: np.ndarray,
    y: np.ndarray,
    level: float,
    edge: str,
    start_after: float = -math.inf,
    occurrence: int = 1,
) -> float:
    count = 0
    for idx in range(1, len(t)):
        if t[idx] < start_after:
            continue
        y0, y1 = y[idx - 1], y[idx]
        if edge == "rise":
            hit = y0 < level <= y1
        else:
            hit = y0 > level >= y1
        if not hit:
            continue
        count += 1
        if count == occurrence:
            if y1 == y0:
                return float(t[idx])
            frac = (level - y0) / (y1 - y0)
            return float(t[idx - 1] + frac * (t[idx] - t[idx - 1]))
    return float("nan")


def interpolate_x_for_y(x: np.ndarray, y: np.ndarray, target: float) -> float:
    diff = y - target
    hits = np.where(np.signbit(diff[:-1]) != np.signbit(diff[1:]))[0]
    if len(hits) == 0:
        return float(x[np.argmin(np.abs(diff))])
    idx = int(hits[0])
    return float(x[idx] + (target - y[idx]) * (x[idx + 1] - x[idx]) / (y[idx + 1] - y[idx]))


def vtc_metrics(vin: np.ndarray, vout: np.ndarray) -> dict[str, float]:
    gain = -np.gradient(vout, vin)
    vm = interpolate_x_for_y(vin, vout - vin, 0.0)
    active = gain - 1.0
    crossings = np.where(np.signbit(active[:-1]) != np.signbit(active[1:]))[0]
    if len(crossings) >= 2:
        vil = float(np.interp(1.0, [gain[crossings[0]], gain[crossings[0] + 1]], [vin[crossings[0]], vin[crossings[0] + 1]]))
        vih = float(np.interp(1.0, [gain[crossings[-1]], gain[crossings[-1] + 1]], [vin[crossings[-1]], vin[crossings[-1] + 1]]))
    else:
        vil = float("nan")
        vih = float("nan")
    vol = float(vout[-1])
    voh = float(vout[0])
    return {
        "vm_v": vm,
        "vil_v": vil,
        "vih_v": vih,
        "vol_v": vol,
        "voh_v": voh,
        "nml_v": vil - vol if not math.isnan(vil) else float("nan"),
        "nmh_v": voh - vih if not math.isnan(vih) else float("nan"),
        "gain_max": float(np.max(gain)),
    }


def delay_metrics(data: np.ndarray, vdd: float) -> dict[str, float]:
    t, vin, vout, ivdd = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    mid = 0.5 * vdd
    tin_rise = crossing_time(t, vin, mid, "rise")
    tout_fall = crossing_time(t, vout, mid, "fall", tin_rise)
    tin_fall = crossing_time(t, vin, mid, "fall", tin_rise)
    tout_rise = crossing_time(t, vout, mid, "rise", tin_fall)
    t10 = 0.1 * vdd
    t90 = 0.9 * vdd
    out_fall_90 = crossing_time(t, vout, t90, "fall", tin_rise)
    out_fall_10 = crossing_time(t, vout, t10, "fall", out_fall_90)
    out_rise_10 = crossing_time(t, vout, t10, "rise", tin_fall)
    out_rise_90 = crossing_time(t, vout, t90, "rise", out_rise_10)
    tphl = tout_fall - tin_rise
    tplh = tout_rise - tin_fall
    start_power = t[-1] * 0.35
    mask = t >= start_power
    pavg = -vdd * float(np.mean(ivdd[mask]))
    return {
        "tphl_s": tphl,
        "tplh_s": tplh,
        "tp_s": 0.5 * (tphl + tplh),
        "tfall_s": out_fall_10 - out_fall_90,
        "trise_s": out_rise_90 - out_rise_10,
        "pavg_w": pavg,
    }


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def plot_vtc_gain(vin: np.ndarray, vout: np.ndarray, metrics: dict[str, float]) -> None:
    gain = -np.gradient(vout, vin)
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.0), dpi=160, sharex=True)
    axes[0].plot(vin, vout, color="#1f6f8b", linewidth=2)
    axes[0].plot(vin, vin, color="#777777", linestyle="--", linewidth=1)
    axes[0].axvline(metrics["vm_v"], color="#b13f2d", linestyle=":", linewidth=1.5)
    axes[0].set_ylabel("Vout (V)")
    axes[0].set_title("Fig. 5.10-style VTC and voltage gain")
    axes[0].grid(True, alpha=0.28)
    axes[1].plot(vin, gain, color="#2b7a3d", linewidth=2)
    for key, label in (("vil_v", "VIL"), ("vih_v", "VIH"), ("vm_v", "VM")):
        value = metrics[key]
        if not math.isnan(value):
            axes[1].axvline(value, linestyle=":", linewidth=1.2, label=f"{label}={value:.3f} V")
    axes[1].axhline(1.0, color="#777777", linestyle="--", linewidth=1)
    axes[1].set_xlabel("Vin (V)")
    axes[1].set_ylabel("-dVout/dVin")
    axes[1].grid(True, alpha=0.28)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_10_vtc_gain.png")
    plt.close(fig)


def plot_size_ratio(curves: dict[float, tuple[np.ndarray, np.ndarray]], rows: list[dict[str, float]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2), dpi=160)
    for ratio, (vin, vout) in curves.items():
        axes[0].plot(vin, vout, linewidth=1.6, label=f"Wp/Wn={ratio:g}")
    axes[0].set_xlabel("Vin (V)")
    axes[0].set_ylabel("Vout (V)")
    axes[0].set_title("VTC versus PMOS/NMOS size ratio")
    axes[0].grid(True, alpha=0.28)
    axes[0].legend(frameon=False, fontsize=7)
    ratios = [row["wp_wn_ratio"] for row in rows]
    vms = [row["vm_v"] for row in rows]
    axes[1].semilogx(ratios, vms, marker="o", color="#b13f2d", linewidth=1.8)
    axes[1].axhline(VDD_NOM / 2, color="#777777", linestyle="--", linewidth=1)
    axes[1].set_xlabel("Wp/Wn")
    axes[1].set_ylabel("VM (V)")
    axes[1].set_title("Switching threshold shift")
    axes[1].grid(True, alpha=0.28, which="both")
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_07_size_ratio.png")
    plt.close(fig)


def plot_vdd_vtc(curves: dict[float, tuple[np.ndarray, np.ndarray]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2), dpi=160)
    for vdd, (vin, vout) in curves.items():
        axes[0].plot(vin, vout, linewidth=1.6, label=f"VDD={vdd:g} V")
        axes[1].plot(vin / vdd, vout / vdd, linewidth=1.6, label=f"{vdd:g} V")
    axes[0].set_xlabel("Vin (V)")
    axes[0].set_ylabel("Vout (V)")
    axes[0].set_title("Supply-voltage VTC sweep")
    axes[1].set_xlabel("Vin/VDD")
    axes[1].set_ylabel("Vout/VDD")
    axes[1].set_title("Normalized VTC")
    for ax in axes:
        ax.grid(True, alpha=0.28)
        ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_12_vdd_vtc.png")
    plt.close(fig)


def plot_transient(data: np.ndarray, metrics: dict[str, float], vdd: float) -> None:
    t_ns = data[:, 0] * 1e9
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.2), dpi=160, sharex=True)
    axes[0].plot(t_ns, data[:, 1], label="Vin", linewidth=1.7)
    axes[0].plot(t_ns, data[:, 2], label="Vout", linewidth=1.7)
    axes[0].axhline(vdd / 2, color="#777777", linestyle="--", linewidth=1)
    axes[0].set_ylabel("Voltage (V)")
    axes[0].set_title(
        f"Fig. 5.16-style transient, tpHL={metrics['tphl_s']*1e12:.1f} ps, "
        f"tpLH={metrics['tplh_s']*1e12:.1f} ps"
    )
    axes[0].grid(True, alpha=0.28)
    axes[0].legend(frameon=False)
    axes[1].plot(t_ns, -data[:, 3] * 1e3, color="#b13f2d", linewidth=1.4)
    axes[1].set_xlabel("Time (ns)")
    axes[1].set_ylabel("Supply current (mA)")
    axes[1].grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_16_transient_delay.png")
    plt.close(fig)


def plot_delay_sweeps(cl_rows: list[dict[str, float]], vdd_rows: list[dict[str, float]], slew_rows: list[dict[str, float]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), dpi=160)
    axes[0].plot([r["cload_fF"] for r in cl_rows], [r["tp_ps"] for r in cl_rows], marker="o")
    axes[0].set_xlabel("CL (fF)")
    axes[0].set_ylabel("tp (ps)")
    axes[0].set_title("Delay vs load")
    axes[1].plot([r["vdd_v"] for r in vdd_rows], [r["tp_ps"] for r in vdd_rows], marker="o", color="#b13f2d")
    axes[1].set_xlabel("VDD (V)")
    axes[1].set_ylabel("tp (ps)")
    axes[1].set_title("Delay vs VDD")
    axes[2].plot([r["input_slew_ps"] for r in slew_rows], [r["tp_ps"] for r in slew_rows], marker="o", color="#2b7a3d")
    axes[2].set_xlabel("Input rise/fall (ps)")
    axes[2].set_ylabel("tp (ps)")
    axes[2].set_title("Delay vs input slope")
    for ax in axes:
        ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_17_delay_sweeps.png")
    plt.close(fig)


def plot_chain(rows: list[dict[str, float]]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    ax.plot([r["stages"] for r in rows], [r["delay_ps"] for r in rows], marker="o", linewidth=1.8)
    ax.set_xlabel("Number of inverter stages")
    ax.set_ylabel("Input-to-output delay (ps)")
    ax.set_title("Fig. 5.21-style buffer-chain optimization")
    ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_21_buffer_chain.png")
    plt.close(fig)


def plot_power(vdd_rows: list[dict[str, float]], cl_rows: list[dict[str, float]], freq_rows: list[dict[str, float]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), dpi=160)
    axes[0].plot([r["vdd_v"] for r in vdd_rows], [r["pavg_uW"] for r in vdd_rows], marker="o")
    axes[0].set_xlabel("VDD (V)")
    axes[0].set_ylabel("Pavg (uW)")
    axes[0].set_title("Power vs VDD")
    axes[1].plot([r["cload_fF"] for r in cl_rows], [r["pavg_uW"] for r in cl_rows], marker="o", color="#b13f2d")
    axes[1].set_xlabel("CL (fF)")
    axes[1].set_ylabel("Pavg (uW)")
    axes[1].set_title("Power vs load")
    axes[2].plot([r["freq_MHz"] for r in freq_rows], [r["pavg_uW"] for r in freq_rows], marker="o", color="#2b7a3d")
    axes[2].set_xlabel("Frequency (MHz)")
    axes[2].set_ylabel("Pavg (uW)")
    axes[2].set_title("Power vs frequency")
    for ax in axes:
        ax.grid(True, alpha=0.28)
    fig.tight_layout()
    fig.savefig(PLOTS / "fig5_38_power.png")
    plt.close(fig)


def run_all(ngspice: Path) -> None:
    ensure_dirs()
    summary_rows: list[dict[str, float | str]] = []

    raw = run_ngspice(ngspice, "nominal_vtc", static_netlist("nominal_vtc", VDD_NOM))
    nominal = load_wrdata(raw)
    vin, vout = nominal[:, 0], nominal[:, 1]
    nominal_metrics = vtc_metrics(vin, vout)
    summary_rows.append({"experiment": "nominal_vtc", **nominal_metrics})
    plot_vtc_gain(vin, vout, nominal_metrics)

    ratio_curves: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    ratio_rows: list[dict[str, float]] = []
    for ratio in (1.0, 1.5, 2.0, 2.75, 4.0, 6.0, 8.0):
        name = f"vtc_ratio_{str(ratio).replace('.', 'p')}"
        raw = run_ngspice(ngspice, name, static_netlist(name, VDD_NOM, wp=ratio * WN0))
        data = load_wrdata(raw)
        metrics = vtc_metrics(data[:, 0], data[:, 1])
        ratio_curves[ratio] = (data[:, 0], data[:, 1])
        ratio_rows.append({"wp_wn_ratio": ratio, **metrics})
    write_csv(RESULTS / "size_ratio_metrics.csv", ratio_rows)
    plot_size_ratio(ratio_curves, ratio_rows)

    vdd_curves: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    vdd_vtc_rows: list[dict[str, float]] = []
    for vdd in (0.8, 1.0, 1.2, 1.5, 1.8, 2.5):
        name = f"vtc_vdd_{str(vdd).replace('.', 'p')}"
        raw = run_ngspice(ngspice, name, static_netlist(name, vdd))
        data = load_wrdata(raw)
        metrics = vtc_metrics(data[:, 0], data[:, 1])
        vdd_curves[vdd] = (data[:, 0], data[:, 1])
        vdd_vtc_rows.append({"vdd_v": vdd, **metrics})
    write_csv(RESULTS / "vdd_vtc_metrics.csv", vdd_vtc_rows)
    plot_vdd_vtc(vdd_curves)

    raw = run_ngspice(ngspice, "nominal_transient", transient_netlist("nominal_transient"))
    tran = load_wrdata(raw)
    tran_metrics = delay_metrics(tran, VDD_NOM)
    summary_rows.append({"experiment": "nominal_transient", **tran_metrics})
    plot_transient(tran, tran_metrics, VDD_NOM)

    cl_rows: list[dict[str, float]] = []
    for cload in (5e-15, 10e-15, 20e-15, 50e-15, 100e-15, 200e-15):
        name = f"delay_cl_{int(cload * 1e15)}f"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, cload=cload)))
        metrics = delay_metrics(data, VDD_NOM)
        cl_rows.append({"cload_fF": cload * 1e15, "tp_ps": metrics["tp_s"] * 1e12, "tphl_ps": metrics["tphl_s"] * 1e12, "tplh_ps": metrics["tplh_s"] * 1e12})

    vdd_delay_rows: list[dict[str, float]] = []
    for vdd in (0.9, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0):
        name = f"delay_vdd_{str(vdd).replace('.', 'p')}"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, vdd=vdd)))
        metrics = delay_metrics(data, vdd)
        vdd_delay_rows.append({"vdd_v": vdd, "tp_ps": metrics["tp_s"] * 1e12, "tphl_ps": metrics["tphl_s"] * 1e12, "tplh_ps": metrics["tplh_s"] * 1e12})

    slew_rows: list[dict[str, float]] = []
    for trf in (5e-12, 20e-12, 50e-12, 100e-12, 200e-12, 500e-12):
        name = f"delay_slew_{int(trf * 1e12)}p"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, trf=trf)))
        metrics = delay_metrics(data, VDD_NOM)
        slew_rows.append({"input_slew_ps": trf * 1e12, "tp_ps": metrics["tp_s"] * 1e12, "tphl_ps": metrics["tphl_s"] * 1e12, "tplh_ps": metrics["tplh_s"] * 1e12})

    write_csv(RESULTS / "delay_vs_load.csv", cl_rows)
    write_csv(RESULTS / "delay_vs_vdd.csv", vdd_delay_rows)
    write_csv(RESULTS / "delay_vs_input_slew.csv", slew_rows)
    plot_delay_sweeps(cl_rows, vdd_delay_rows, slew_rows)

    chain_rows: list[dict[str, float]] = []
    for stages in range(1, 8):
        name = f"chain_{stages}_stage"
        data = load_wrdata(run_ngspice(ngspice, name, chain_netlist(name, stages=stages, cext=1e-12)))
        t, vin, vout = data[:, 0], data[:, 1], data[:, 2]
        tin_rise = crossing_time(t, vin, VDD_NOM / 2, "rise")
        out_edge = "fall" if stages % 2 else "rise"
        tout = crossing_time(t, vout, VDD_NOM / 2, out_edge, tin_rise)
        chain_rows.append({"stages": stages, "delay_ps": (tout - tin_rise) * 1e12})
    write_csv(RESULTS / "buffer_chain_delay.csv", chain_rows)
    plot_chain(chain_rows)

    power_vdd_rows: list[dict[str, float]] = []
    for vdd in (1.0, 1.2, 1.5, 1.8, 2.0, 2.5):
        name = f"power_vdd_{str(vdd).replace('.', 'p')}"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, vdd=vdd, cload=100e-15, cycles=8)))
        metrics = delay_metrics(data, vdd)
        power_vdd_rows.append({"vdd_v": vdd, "pavg_uW": metrics["pavg_w"] * 1e6})

    power_cl_rows: list[dict[str, float]] = []
    for cload in (10e-15, 20e-15, 50e-15, 100e-15, 200e-15, 500e-15):
        name = f"power_cl_{int(cload * 1e15)}f"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, cload=cload, cycles=8)))
        metrics = delay_metrics(data, VDD_NOM)
        power_cl_rows.append({"cload_fF": cload * 1e15, "pavg_uW": metrics["pavg_w"] * 1e6})

    power_freq_rows: list[dict[str, float]] = []
    for freq in (100e6, 250e6, 500e6, 750e6, 1000e6):
        period = 1.0 / freq
        name = f"power_freq_{int(freq / 1e6)}m"
        data = load_wrdata(run_ngspice(ngspice, name, transient_netlist(name, cload=100e-15, period=period, trf=20e-12, cycles=10)))
        metrics = delay_metrics(data, VDD_NOM)
        power_freq_rows.append({"freq_MHz": freq / 1e6, "pavg_uW": metrics["pavg_w"] * 1e6})

    write_csv(RESULTS / "power_vs_vdd.csv", power_vdd_rows)
    write_csv(RESULTS / "power_vs_load.csv", power_cl_rows)
    write_csv(RESULTS / "power_vs_frequency.csv", power_freq_rows)
    plot_power(power_vdd_rows, power_cl_rows, power_freq_rows)

    write_csv(RESULTS / "summary_metrics.csv", summary_rows)
    print(f"wrote plots to {PLOTS}")
    print(f"wrote metrics to {RESULTS}")


def main() -> None:
    parser = argparse.ArgumentParser()
    default_ngspice = ROOT.parents[1] / "Spice64" / "bin" / "ngspice_con.exe"
    parser.add_argument("--ngspice", type=Path, default=default_ngspice)
    args = parser.parse_args()
    run_all(args.ngspice)


if __name__ == "__main__":
    main()
