# ngspice simulation summary

## Scope

The paper does not provide 45nm CMOS SOI transistor models, optical compact models, layout parasitics, or digital controller RTL. These ngspice decks are topology/behavior-level macro models that reproduce the operating mechanisms of the core circuit figures.

## Simulated core figures

- Fig. 23.3.2: low-noise TIA plus cascaded Q-tamed CTLE.
- Fig. 23.3.3: MRM PAM-4 driver with R+L output peaking and MRM capacitive load.
- Fig. 23.3.4: IL-adjustable WLL circuit with MPD gain adjust, bang-bang tracking, PWM/thermal tuning abstraction.

## WLL two innovation points

1. Adjustable-IL wavelength locking: the loop first performs sweep/gain adjustment to map the MPD peak to Vmax, then locks to VIL, so Desired IL = 1 - VIL/Vmax. This allows 6 dB, 3 dB, 1.5 dB, or near-peak operating points rather than a fixed lock point.

2. Low-overhead multi-channel implementation: 6b MPD gain control, a 1b bang-bang ADC, and a 14b-equivalent PWM thermal DAC handle MPD/channel mismatch and thermal drift without a SAR ADC or large delta-sigma thermal DAC. The same scheme applies to TX MRM and RX CRR.

## TIA / Q-tamed CTLE macro

- TIS-only 1 GHz transimpedance: 62.00 dB-ohm, close to the paper's 62 dB-ohm TIA target.
- Q-tamed path 1 GHz gain: 63.55 dB-ohm equivalent.
- Q-tamed normalized peak: 4.89 dB at 28.57 GHz.
- Q-tamed normalized gain at 20 GHz / 41 GHz: 3.88 dB / 2.63 dB.
- Coincident high-Q comparison normalized peak: 6.31 dB at 31.82 GHz.
- Interpretation: the macro shows the intended trade-off: lower-Q, broader response versus an undamped coincident peaking path. It is not a transistor-level reproduction of the 12.4 dB measured CTLE peaking.

## MRM driver macro

- No-peaking -3 dB bandwidth: 20.38 GHz.
- R+L peaking -3 dB bandwidth: 28.74 GHz.
- Bandwidth extension: 41.0%.
- PAM-4 output range into MRM macro load: 0.258 V to 1.535 V, swing 1.277 V.

## WLL macro

- MPD gain correction after setup: 1.613x, compensating the modeled MPD scale mismatch.
- Lock error before thermal disturbance: -4.008e-14 V.
- Lock error after thermal disturbance and re-tracking: -2.601e-13 V.
- Interpretation: the loop returns the MPD amplifier output to the desired IL reference after the modeled thermal disturbance.

## Files

- tia_qtamed_ctle_ac.cir / tia_qtamed_ctle_ac.png
- mrm_driver_pam4.cir / mrm_driver_ac.png / mrm_driver_pam4.png
- wll_locking_macro.cir / wll_locking_macro.png
