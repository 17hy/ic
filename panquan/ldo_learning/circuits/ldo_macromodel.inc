* Teaching-oriented PMOS LDO macro model.
* This model is for architecture learning, not for silicon signoff.
*
* Pins:
*   vin  - input supply
*   vout - regulated output
*   vref - reference voltage
*   fb   - feedback divider midpoint, exposed for probing
*   gate - PMOS gate, exposed for probing

.subckt ldo_pmos vin vout vref fb gate params: rtop=400k rbot=600k a0=4000 fp_ea=20k rea=10k cout=10u esr=50m wpass=30000u lpass=1u cgate=300p
.param cea={1/(6.283185307179586*fp_ea*rea)}

* PMOS pass device. Source and body are tied to VIN.
Mpass vout gate vin vin ppass W={wpass} L={lpass}

* Feedback network: VOUT = VREF * (1 + RTOP/RBOT).
Rtop vout fb {rtop}
Rbot fb 0 {rbot}

* One-pole error amplifier.
* The EA output is a "gate pull-down demand"; higher value means lower PMOS gate.
Eea_raw ea_raw 0 vref fb {a0}
Rea ea_raw ea {rea}
Cea ea 0 {cea}

* Gate drive with a simple rail clamp.
Bgate gate 0 V={min(max(V(vin)-V(ea),0),V(vin))}
Cgate gate vin {cgate}

* Output capacitor with ESR.
Resr vout cout_node {esr}
Cout cout_node 0 {cout}
Rbleed vout 0 100meg

.model ppass pmos(level=1 vto=-0.7 kp=200u lambda=0.02)
.ends ldo_pmos
