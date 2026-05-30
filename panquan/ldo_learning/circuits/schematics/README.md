# LDO textbook schematics

These diagrams are drawn from the SPICE macro-model netlists in `panquan/ldo_learning/circuits`.

- `ldo_pmos_textbook.svg` maps `ldo_macromodel.inc` into a textbook PMOS LDO schematic.
- `paper_dual_loop_textbook.svg` maps `paper_dual_loop_ldo.inc` into a small-signal dual-loop control schematic.

The `.cir` files in the parent directory are simulation benches. They add supplies, loads, sweeps, ripple injection, and transient disturbances around these two core subcircuits.

