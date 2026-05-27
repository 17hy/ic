$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ng = Resolve-Path (Join-Path $root '..\..\Spice64\bin\ngspice.exe')
$circuits = @('roofline_balance', 'mix_precision_pe', 'sparsity_speedup', 'latency_hiding')
foreach ($c in $circuits) {
    Remove-Item -LiteralPath (Join-Path $root "$c.log") -ErrorAction SilentlyContinue
    & $ng -b -o (Join-Path $root "$c.log") (Join-Path $root "$c.cir") | Out-Null
}
python (Join-Path $root 'plot_results.py') | Tee-Object -FilePath (Join-Path $root 'plot_results.log')
