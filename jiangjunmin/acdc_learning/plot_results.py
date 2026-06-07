from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent


def read_wrdata(name, labels):
    data = np.loadtxt(ROOT / name)
    # ngspice wrdata writes each requested vector as a time/value pair.
    time = data[:, 0]
    values = {}
    for index, label in enumerate(labels, start=1):
        values[label] = data[:, 2 * index + 1]
    return time, values


def decimate(time, values, limit=6000):
    if len(time) <= limit:
        return time, values
    step = int(np.ceil(len(time) / limit))
    return time[::step], {key: value[::step] for key, value in values.items()}


def save_plot(filename, title, ylabel, series):
    plt.figure(figsize=(9, 4.8))
    for name, time, value in series:
        plt.plot(time, value, label=name, linewidth=1.2)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROOT / filename, dpi=160)
    plt.close()


def main():
    t, v = read_wrdata("01_isolated_flyback_acdc.csv", ["vbus", "vout", "vdrain"])
    t, v = decimate(t, v)
    save_plot(
        "01_isolated_flyback_acdc.png",
        "Isolated flyback average macro",
        "Voltage (V)",
        [("HV bus", t, v["vbus"]), ("12 V output", t, v["vout"]), ("switch stress estimate", t, v["vdrain"])],
    )

    t, v = read_wrdata("02_direct_rectifier_hv_buck.csv", ["vbus", "vsw", "vout", "il"])
    t, v = decimate(t, v)
    save_plot(
        "02_direct_rectifier_hv_buck.png",
        "Direct HV buck from 325 V bus",
        "Voltage (V)",
        [("HV bus", t, v["vbus"]), ("switch node", t, v["vsw"]), ("output", t, v["vout"])],
    )

    t, v = read_wrdata("03_cap_drop_rectifier.csv", ["vline", "vcx", "vrec"])
    t, v = decimate(t, v)
    save_plot(
        "03_cap_drop_rectifier.png",
        "Capacitor-drop rectifier front end",
        "Voltage (V)",
        [("mains", t, v["vline"]), ("X-cap voltage", t, v["vcx"]), ("VREC", t, v["vrec"])],
    )

    t, v = read_wrdata("04_cap_drop_fixed_ratio_sc_macro.csv", ["vrec_small", "vout_small", "vrec_large", "vout_large"])
    t, v = decimate(t, v)
    save_plot(
        "04_cap_drop_fixed_ratio_sc_macro.png",
        "Fixed-ratio SC macro: reservoir capacitor comparison",
        "Voltage (V)",
        [
            ("small CREC VREC", t, v["vrec_small"]),
            ("small CREC VOUT", t, v["vout_small"]),
            ("large CREC VREC", t, v["vrec_large"]),
            ("large CREC VOUT", t, v["vout_large"]),
        ],
    )

    t, v = read_wrdata(
        "05_isdb_dual_branch_converter.csv",
        ["sw1_5v", "sw2_5v", "out_5v", "il1_5v", "il2_5v", "sw1_12v", "sw2_12v", "out_12v", "il1_12v", "il2_12v"],
    )
    t, v = decimate(t, v)
    save_plot(
        "05_isdb_dual_branch_converter.png",
        "ISDB switched stage",
        "Voltage / Current",
        [
            ("5 V case VOUT", t, v["out_5v"]),
            ("5 V case IL1", t, v["il1_5v"]),
            ("5 V case IL2", t, v["il2_5v"]),
            ("12 V case VOUT", t, v["out_12v"]),
        ],
    )

    t, v = read_wrdata("06_isdb_balance_loop_macro.csv", ["vch", "vcl", "mismatch"])
    t, v = decimate(t, v)
    save_plot(
        "06_isdb_balance_loop_macro.png",
        "ISDB VCH/VCL balance macro",
        "Voltage (V)",
        [("VCH", t, v["vch"]), ("VCL", t, v["vcl"]), ("VCH - VCL", t, v["mismatch"])],
    )


if __name__ == "__main__":
    main()
