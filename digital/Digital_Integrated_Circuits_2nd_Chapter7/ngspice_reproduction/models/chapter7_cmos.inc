* Educational CMOS model for Digital Integrated Circuits, Chapter 5 reproductions.
* The parameters are deliberately compact Level-1 values. They are tuned for
* qualitative inverter metrics, not for a foundry process match.
.param LMIN=0.25u
.param WN0=1u
.param WP0=2.75u

.model NMOS NMOS (
+ LEVEL=1 VTO=0.43 KP=220u GAMMA=0.45 PHI=0.6 LAMBDA=0.06
+ TOX=5n CGSO=0.35n CGDO=0.35n CGBO=0.05n CJ=1m CJSW=0.2n
+ PB=0.8 MJ=0.5 MJSW=0.33)

.model PMOS PMOS (
+ LEVEL=1 VTO=-0.43 KP=80u GAMMA=0.45 PHI=0.6 LAMBDA=0.06
+ TOX=5n CGSO=0.35n CGDO=0.35n CGBO=0.05n CJ=1m CJSW=0.2n
+ PB=0.8 MJ=0.5 MJSW=0.33)

.subckt inv in out vdd wnn=1u wpp=2.75u lch=0.25u
Mp out in vdd vdd PMOS W={wpp} L={lch}
Mn out in 0 0 NMOS W={wnn} L={lch}
.ends inv

.subckt tg in out clk clkb vdd wnn=1u wpp=2.75u lch=0.25u
Mn out clk  in 0   NMOS W={wnn} L={lch}
Mp out clkb in vdd PMOS W={wpp} L={lch}
.ends tg
