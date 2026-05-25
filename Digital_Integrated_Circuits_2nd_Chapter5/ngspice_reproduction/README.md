# Chapter 5 ngspice Reproduction

This folder rebuilds the main Chapter 5 CMOS inverter experiment figures with ngspice-generated data.

Run from PowerShell:

```powershell
cd C:\Users\Guohu\Desktop\ngspice\Digital_Integrated_Circuits_2nd_Chapter5\ngspice_reproduction
.\run_all.ps1
```

Outputs:
- `generated_netlists/`: netlists emitted by the Python runner.
- `logs/`: ngspice batch logs.
- `raw/`: direct `wrdata` outputs from ngspice.
- `results/`: extracted metrics as CSV.
- `plots/`: reproduced figures as PNG.

Experiments:
- `fig5_10_vtc_gain.png`: nominal inverter VTC, gain, switching threshold, and noise margins.
- `fig5_07_size_ratio.png`: PMOS/NMOS size ratio versus VTC and switching threshold.
- `fig5_12_vdd_vtc.png`: VTC change under different supply voltages.
- `fig5_16_transient_delay.png`: transient response and propagation delay.
- `fig5_17_delay_sweeps.png`: delay versus load capacitance, supply voltage, and input slew.
- `fig5_21_buffer_chain.png`: buffer-chain delay versus number of stages.
- `fig5_38_power.png`: dynamic power trends versus supply, load, and frequency.

The model in `models/chapter5_cmos.inc` is an educational Level-1 MOS model. It is intended to reproduce the qualitative curves and measurement flow in Chapter 5, not exact foundry numbers.
