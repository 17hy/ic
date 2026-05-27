import math
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent

# Values mirrored from the ngspice behavioral netlists.
hbm_bw = 16384
ffn_demand = 4096 * 4
mha_demand = 1024 * 16
ddr_service = hbm_bw * 0.25
hbm_util = 29.25 / 38.5 * 100

sparsity_labels = ["Dense", "50%", "75%", "87.5%\none-hot", "87.5%\naddr"]
eff_bw = [4.125, 3.125, 1.875, 1.625, 1.125]
speedup = [1.0, 4.125/3.125, 4.125/1.875, 4.125/1.625, 4.125/1.125]

steps = 17
compute_us = 38.5
host_update_us = 8.0
no_hide = steps * (compute_us + host_update_us)
hide = compute_us + host_update_us + (steps - 1) * compute_us
saving = (1 - hide / no_hide) * 100

pe_labels = ["FFN\nFP16*INT4", "MHA\nFP16*FP16"]
pe_error = [0.0472, 0.0044]
pe_power = [40.34, 10.39]
area_save = [(107437-71664)/107437*100, (140677-71664)/140677*100]

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25})

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.bar(["HBM service", "FFN demand", "MHA demand", "DDR service"], [hbm_bw, ffn_demand, mha_demand, ddr_service], color=["#2f6f73", "#d95f02", "#7570b3", "#999999"])
ax.set_ylabel("bits/cycle")
ax.set_title(f"Roofline balance: HBM utilization example = {hbm_util:.2f}%")
ax.set_ylim(0, hbm_bw * 1.16)
for i, v in enumerate([hbm_bw, ffn_demand, mha_demand, ddr_service]):
    ax.text(i, v + 350, f"{v:.0f}", ha="center", va="bottom")
fig.tight_layout()
fig.savefig(ROOT / "roofline_balance.png", dpi=180)
plt.close(fig)

fig, ax1 = plt.subplots(figsize=(7.2, 4.2))
ax2 = ax1.twinx()
ax1.bar(sparsity_labels, eff_bw, color="#4c78a8", alpha=0.82, label="effective bit-width")
ax2.plot(sparsity_labels, speedup, marker="o", color="#f58518", linewidth=2.2, label="speedup")
ax1.set_ylabel("effective bit-width (bit)")
ax2.set_ylabel("ideal speedup (x)")
ax1.set_title("Log-scale sparsity packing efficiency")
for i, v in enumerate(speedup):
    ax2.text(i, v + 0.08, f"{v:.2f}x", ha="center", color="#8a4600")
fig.tight_layout()
fig.savefig(ROOT / "sparsity_speedup.png", dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.bar(["No hiding", "Latency hiding"], [no_hide, hide], color=["#b55d60", "#2f6f73"])
ax.set_ylabel("17-step latency (us)")
ax.set_title(f"Instruction update hiding saves {saving:.2f}%")
ax.set_ylim(0, no_hide * 1.12)
for i, v in enumerate([no_hide, hide]):
    ax.text(i, v + 10, f"{v:.1f} us", ha="center")
fig.tight_layout()
fig.savefig(ROOT / "latency_hiding.png", dpi=180)
plt.close(fig)

fig, ax1 = plt.subplots(figsize=(7.0, 4.0))
ax2 = ax1.twinx()
ax1.bar(pe_labels, pe_power, color="#72b7b2", alpha=0.82, label="power")
ax2.plot(pe_labels, pe_error, color="#e45756", marker="o", linewidth=2.2, label="error")
ax1.set_ylabel("power (mW)")
ax2.set_ylabel("computation error (%)")
ax2.set_ylim(0, max(pe_error) * 1.35)
ax1.set_title(f"Mixed-precision PE: area saving {area_save[0]:.1f}% / {area_save[1]:.1f}%")
for i, v in enumerate(pe_error):
    ax2.text(i, v + max(pe_error) * 0.05, f"{v:.4f}%", ha="center", color="#8b1e1e")
fig.tight_layout()
fig.savefig(ROOT / "mix_precision_pe.png", dpi=180)
plt.close(fig)

summary = f"""# EdgeLLM ngspice behavior simulation summary

These netlists are architecture-level behavioral models because the paper describes a CPU-FPGA accelerator, not transistor-level analog circuits.

## 1. Roofline / HBM balance

- HBM service capability: {hbm_bw:.0f} bit/cycle.
- FFN FP16*INT4 demand: 4096 * 4 = {ffn_demand:.0f} bit/cycle.
- MHA FP16*FP16 KV-cache demand: 1024 * 16 = {mha_demand:.0f} bit/cycle.
- Both hot paths match the effective HBM service capability.
- Paper HBM utilization example: 29.25 us / 38.5 us = {hbm_util:.2f}%.
- If only DDR-like 25% service is available, the behavioral backlog grows instead of staying balanced.

## 2. Mixed-precision PE

- Per-group FFN INT4 weight demand: 128 * 4 = 512 bit.
- Per-group MHA FP16 KV demand: 32 * 16 = 512 bit.
- The two modes have matched per-group memory demand after changing precision and parallelism.
- Computation error: FP16*INT4 = 0.0472%, FP16*FP16 = 0.0044%.
- Area saving vs FP16 adder-tree baseline: {area_save[0]:.2f}%.
- Area saving vs FP20 adder-tree baseline: {area_save[1]:.2f}%.

## 3. Log-scale sparsity

- Dense effective bit-width: 4.125 bit.
- 50% sparse: 3.125 bit, {speedup[1]:.2f}x ideal speedup.
- 75% sparse: 1.875 bit, {speedup[2]:.2f}x ideal speedup.
- 87.5% sparse with one-hot mask: 1.625 bit, {speedup[3]:.2f}x ideal speedup.
- 87.5% sparse with address-in-block: 1.125 bit, {speedup[4]:.2f}x ideal speedup.

## 4. Instruction latency hiding

- Assumed 17 hardware steps from the optimized GLM block graph.
- Per-step accelerator compute time uses the paper's 38.5 us HBM MatMUL example.
- Host instruction update time is modeled as 8 us.
- Without hiding: {no_hide:.1f} us.
- With hiding: {hide:.1f} us.
- Saved latency: {saving:.2f}%.

## Output figures

- roofline_balance.png
- mix_precision_pe.png
- sparsity_speedup.png
- latency_hiding.png
"""
(ROOT / "simulation_summary.md").write_text(summary, encoding="utf-8")
print(summary)
