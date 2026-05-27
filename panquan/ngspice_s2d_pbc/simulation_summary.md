# ngspice simulation summary

## Model scope

These simulations are topology/macromodel checks because the paper does not provide the 130-nm SiGe BiCMOS PDK, device models, layout parasitics, or exact bias currents. The PBC simulation targets the current-cancellation mechanism in Fig. 7/Fig. 8. The CTLE simulation is a small-signal macro model showing the effect of emitter degeneration and distributed/shunt peaking.

## S2D PBC transient result

- Input: 300 mVpp sine around 0.6 V common mode, 50 ohm dc-coupled termination.
- LDO output impedance is represented by an effective 0.833 ohm source impedance for the transient check.
- Without PBC: 4.918 mVpp supply bounce.
- With PBC: 1.191 mVpp supply bounce.
- Suppression: 75.78%.
- Paper reference: 5 mV -> 1.2 mV, 76% suppression.

## Cascaded CTLE AC macro result

- Normalization: gain relative to 1 GHz.
- With peaking, boost at 56 GHz: 22.29 dB.
- With peaking, boost at 75 GHz: 22.53 dB.
- With peaking, peak: 22.53 dB at 72.30 GHz.
- Without useful peaking, peak: 21.54 dB at 59.67 GHz.
- Paper reference: distributed peaking extends peaking from about 56 GHz to 75 GHz; measured RX tuning reaches 4-22 dB at 56 GHz.

## Files

- s2d_pbc_transient.cir: PBC transient ngspice deck.
- s2d_pbc_transient.csv: transient data exported by ngspice.
- s2d_pbc_transient.png: transient plot.
- ctle_ac_macro.cir: cascaded CTLE AC macro deck.
- ctle_ac.csv: AC data exported by ngspice.
- ctle_ac_macro.png: AC plot.
