$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dirs = @(
    "01_small_signal",
    "02_large_signal",
    "03_pdk_direct"
)

foreach ($dir in $dirs) {
    $script = Join-Path $root "$dir\run.ps1"
    Write-Host "=== Running $dir ==="
    & $script
}

