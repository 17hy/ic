# Chapter 7 ngspice Reproduction

Run:

```powershell
cd C:\Users\Guohu\Desktop\ngspice\digital\Digital_Integrated_Circuits_2nd_Chapter7\ngspice_reproduction
.\run_all.ps1
```

Outputs:

- `generated_netlists/`: auto-generated ngspice netlists
- `logs/`: ngspice batch logs
- `raw/`: raw `wrdata` outputs
- `results/summary_metrics.csv`: extracted timing/frequency metrics
- `plots/`: reproduced chapter-style PNG figures

Plots:

- `fig7_bistable_regeneration.png`
- `fig7_tg_latch_waveforms.png`
- `fig7_schmitt_hysteresis.png`
- `fig7_ring_oscillator.png`
