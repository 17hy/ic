# ngspice simulation summary

## Model scope

The paper does not provide process devices, gate-driver details, parasitics, or exact control-loop compensation values. These decks are topology-level models. The ISDB power-stage decks idealize S1-S5 and the flying capacitor network as two PWM switch-node waveforms from 0 to VREC/2 feeding two inductors in parallel. The balance-loop deck abstracts the VCH/VCL controller as a differential duty/power correction.

## Core reason this circuit was selected

The central contribution is the full-duty-cycle input-series dual-branch (ISDB) DC-DC converter. It splits VREC into +VREC/2 and -VREC/2, makes switch/capacitor stress roughly half of VREC, and gives the conversion relation VOUT ~= D * VREC / 2 while the two branch outputs are paralleled.

## Switched ISDB: 60 V to 5 V, 0.4 A

- Target paper condition: VREC = 60 V, VOUT = 5 V, IOUT = 0.4 A, CCM.
- Simulated average VOUT: 4.9905 V.
- Simulated VOUT ripple: 2.591 mVpp.
- Average IL1 / IL2: 0.1996 A / 0.1996 A.
- Current-sharing error: 0.0032 mA.
- Inductor ripple IL1 / IL2: 0.2093 A / 0.2094 A.

## Switched ISDB: 30 V to 12 V, 0.18 A

- Target paper condition: VREC = 30 V, VOUT = 12 V, IOUT = 0.18 A, D around 0.8, phase overlap.
- Simulated average VOUT: 12.0016 V.
- Simulated VOUT ripple: 1.407 mVpp.
- Average IL1 / IL2: 0.0900 A / 0.0900 A.

## VCH/VCL balance-loop macro

- Initial condition: VCH = 36 V, VCL = 24 V.
- Mismatch near start: 11.8478 V.
- Final VCH / VCL at 40 ms: 30.0363 V / 29.9637 V.
- Final mismatch: 0.0727 V.

## Files

- isdb_60v_to_5v.cir: switched power-stage deck for the 60 V to 5 V CCM case.
- isdb_30v_to_12v.cir: switched power-stage deck for the D>0.5 full-duty-cycle case.
- isdb_balance_loop.cir: VCH/VCL balance-loop principle deck.
- isdb_60v_5v_transient.png: 60 V to 5 V transient plot.
- isdb_30v_12v_overlap.png: 30 V to 12 V overlap transient plot.
- isdb_balance_loop.png: balance-loop plot.
