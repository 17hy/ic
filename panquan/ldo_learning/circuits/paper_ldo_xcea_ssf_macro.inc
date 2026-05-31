* Full large-signal paper-inspired LDO macro.
*
* Purpose:
*   Reproduce the LDO architecture described in the paper Section II-B:
*   PMOS Mpass, 2-stage XCEA-like slow loop, SSF-like fast loop, and
*   200 pF output capacitor for S2D/D2S supply-noise suppression.
*
* This is a topology-faithful macro, not a silicon signoff netlist.
* It can run without any external PDK and is intended as the bridge
* between the earlier small-signal macro and an IHP SG13G2 device deck.
*
* Pins:
*   vin   - noisy 3.3 V supply
*   vout  - regulated output, nominally 3.1 V
*   vref  - reference input, nominally 1.2 V
*   fb    - feedback divider node
*   gate  - PMOS pass-gate node
*   xcea  - slow-loop internal output
*   ssf   - fast-loop assist node

.subckt paper_ldo_xcea_ssf_macro vin vout vref fb gate xcea ssf params: rtop=950k rbot=600k wpass=80000u lpass=0.5u cout=200p esr=80m cgate=3p gm_xcea=2m ro_xcea=40meg fp_xcea=120k av_fast=0.9 fz_fast=20meg fp_fast=5gig rg_slow=8k rg_fast=120
.param cxcea={1/(6.283185307179586*fp_xcea*ro_xcea)}
.param rhp=1k
.param chp={1/(6.283185307179586*fz_fast*rhp)}
.param rlp=1k
.param clp={1/(6.283185307179586*fp_fast*rlp)}

* PMOS pass element. Source/body are tied to VIN.
Mpass vout gate vin vin paper_pmos_pass W={wpass} L={lpass}

* Feedback divider. For 3.1 V output and 1.2 V reference:
* VOUT = VREF * (1 + 950k/600k) = 3.1 V.
Rtop vout fb {rtop}
Rbot fb 0 {rbot}

* XCEA-like slow loop. Positive error means VREF > FB, so the PMOS
* gate must be pulled down. The xcea node represents gate pull-down demand.
Gxcea 0 xcea vref fb {gm_xcea}
Rxcea xcea 0 {ro_xcea}
Cxcea xcea 0 {cxcea}

* Slow-loop gate command with rail clamp.
Bslow slow_gate 0 V={min(max(V(vin)-V(xcea),0),V(vin))}
Rslow_gate slow_gate gate {rg_slow}

* SSF-like fast loop. A high-pass sense path detects rapid VOUT motion.
* If VOUT drops quickly, hp is negative and the gate is pulled downward.
Rhpf vout hp_lp {rhp}
Chpf hp_lp 0 {chp}
Ehp hp 0 vout hp_lp 1
Rfast_lp hp ssf {rlp}
Cfast_lp ssf 0 {clp}
Bfast fast_gate 0 V={min(max(V(gate)+av_fast*V(ssf),0),V(vin))}
Rfast_gate fast_gate gate {rg_fast}

* Output capacitor and pass-gate capacitance.
Resr vout cout_node {esr}
Cout cout_node 0 {cout}
Cgate gate vin {cgate}
Rbleed vout 0 100meg

.model paper_pmos_pass pmos(level=1 vto=-0.55 kp=160u lambda=0.03 cgso=2n cgdo=2n)
.ends paper_ldo_xcea_ssf_macro

