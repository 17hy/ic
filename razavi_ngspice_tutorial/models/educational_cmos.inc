* Educational CMOS model card for Razavi ch. 1-5 ngspice labs.
* This is a compact long-channel model for topology-level learning.
.param VDD=1.8
.model NMOS NMOS (
+ LEVEL=1 VTO=0.45 KP=220u GAMMA=0.45 PHI=0.6 LAMBDA=0.08
+ TOX=4n CGSO=0.35n CGDO=0.35n CGBO=0.05n CJ=1m CJSW=0.2n
+ PB=0.8 MJ=0.5 MJSW=0.33)
.model PMOS PMOS (
+ LEVEL=1 VTO=-0.45 KP=80u GAMMA=0.45 PHI=0.6 LAMBDA=0.08
+ TOX=4n CGSO=0.35n CGDO=0.35n CGBO=0.05n CJ=1m CJSW=0.2n
+ PB=0.8 MJ=0.5 MJSW=0.33)
