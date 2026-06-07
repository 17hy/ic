$ErrorActionPreference = "Stop"

$decks = @(
  "01_isolated_flyback_acdc.cir",
  "02_direct_rectifier_hv_buck.cir",
  "03_cap_drop_rectifier.cir",
  "04_cap_drop_fixed_ratio_sc_macro.cir",
  "05_isdb_dual_branch_converter.cir",
  "06_isdb_balance_loop_macro.cir"
)

foreach ($deck in $decks) {
  $log = [System.IO.Path]::ChangeExtension($deck, ".log")
  Write-Host "Running $deck"
  ngspice -b -o $log $deck
}

python .\plot_results.py
