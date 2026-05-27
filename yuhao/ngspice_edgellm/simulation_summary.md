# EdgeLLM ngspice behavior simulation summary

These netlists are architecture-level behavioral models because the paper describes a CPU-FPGA accelerator, not transistor-level analog circuits.

## 1. Roofline / HBM balance

- HBM service capability: 16384 bit/cycle.
- FFN FP16*INT4 demand: 4096 * 4 = 16384 bit/cycle.
- MHA FP16*FP16 KV-cache demand: 1024 * 16 = 16384 bit/cycle.
- Both hot paths match the effective HBM service capability.
- Paper HBM utilization example: 29.25 us / 38.5 us = 75.97%.
- If only DDR-like 25% service is available, the behavioral backlog grows instead of staying balanced.

## 2. Mixed-precision PE

- Per-group FFN INT4 weight demand: 128 * 4 = 512 bit.
- Per-group MHA FP16 KV demand: 32 * 16 = 512 bit.
- The two modes have matched per-group memory demand after changing precision and parallelism.
- Computation error: FP16*INT4 = 0.0472%, FP16*FP16 = 0.0044%.
- Area saving vs FP16 adder-tree baseline: 33.30%.
- Area saving vs FP20 adder-tree baseline: 49.06%.

## 3. Log-scale sparsity

- Dense effective bit-width: 4.125 bit.
- 50% sparse: 3.125 bit, 1.32x ideal speedup.
- 75% sparse: 1.875 bit, 2.20x ideal speedup.
- 87.5% sparse with one-hot mask: 1.625 bit, 2.54x ideal speedup.
- 87.5% sparse with address-in-block: 1.125 bit, 3.67x ideal speedup.

## 4. Instruction latency hiding

- Assumed 17 hardware steps from the optimized GLM block graph.
- Per-step accelerator compute time uses the paper's 38.5 us HBM MatMUL example.
- Host instruction update time is modeled as 8 us.
- Without hiding: 790.5 us.
- With hiding: 662.5 us.
- Saved latency: 16.19%.

## Output figures

- roofline_balance.png
- mix_precision_pe.png
- sparsity_speedup.png
- latency_hiding.png
