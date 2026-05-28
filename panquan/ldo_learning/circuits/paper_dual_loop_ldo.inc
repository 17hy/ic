* Paper-inspired dual-loop LDO small-signal macro model.
* It is based on the behavior described in the paper's Section II-B:
* XCEA slow loop + SSF fast loop, 200 pF output capacitor, high PSR.
*
* This is not a transistor-level reproduction. It is a compact linear
* model for PSR, output impedance, and power-bounce learning.
*
* Pins:
*   vin_ripple - small-signal input supply ripple
*   out_ripple - small-signal regulated output ripple

.subckt paper_dual_loop_ldo vin_ripple out_ripple params: rload=31 cout=200p esr=50m gfeed=50m gm_slow=45 fp_slow=120k gm_fast=0 fz_fast=20meg fp_fast=5gig
.param rctl=1k
.param cslow={1/(6.283185307179586*fp_slow*rctl)}
.param chp_fast={1/(6.283185307179586*fz_fast*rctl)}
.param clp_fast={1/(6.283185307179586*fp_fast*rctl)}

* Passive output network around the regulated operating point.
Rload out_ripple 0 {rload}
Resr out_ripple cap_node {esr}
Cout cap_node 0 {cout}

* Supply feedthrough path: input ripple current injected into VOUT.
Gfeed 0 out_ripple vin_ripple 0 {gfeed}

* The loops sense output ripple. A positive output ripple causes the
* loops to draw correction current from the output node.
Eerr err 0 out_ripple 0 1

* Slow XCEA-like loop.
Rslow err slow {rctl}
Cslow slow 0 {cslow}
Gslow out_ripple 0 slow 0 {gm_slow}

* Fast SSF-like loop. It is modeled as a lead/high-pass assist path:
* it has little effect at low frequency, but strongly lowers dynamic
* output impedance for fast load-current changes and sharp ripple edges.
* Setting gm_fast=0 reduces the model to a single slow-loop LDO.
Cfast_hp err fast_hp {chp_fast}
Rfast_hp fast_hp 0 {rctl}
Rfast_lp fast_hp fast {rctl}
Cfast_lp fast 0 {clp_fast}
Gfast out_ripple 0 fast 0 {gm_fast}

Rleak_out out_ripple 0 1g
.ends paper_dual_loop_ldo
