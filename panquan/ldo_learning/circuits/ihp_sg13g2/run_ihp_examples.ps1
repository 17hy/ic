$ErrorActionPreference = "Stop"

if (-not $env:PDK_ROOT) {
    throw "PDK_ROOT is not set. Example: `$env:PDK_ROOT='C:\pdk\IHP-Open-PDK'"
}
if (-not $env:PDK) {
    $env:PDK = "ihp-sg13g2"
}

$modelDir = Join-Path $env:PDK_ROOT "$env:PDK\libs.tech\ngspice\models"
if (-not (Test-Path $modelDir)) {
    throw "Cannot find IHP ngspice model directory: $modelDir"
}

$spiceInit = Join-Path $env:PDK_ROOT "$env:PDK\libs.tech\ngspice\.spiceinit"
if (-not (Test-Path $spiceInit)) {
    throw "Cannot find IHP .spiceinit: $spiceInit"
}

Write-Host "Using PDK_ROOT=$env:PDK_ROOT"
Write-Host "Using PDK=$env:PDK"
Write-Host "If ngspice cannot find OSDI models, install IHP ngspice setup first."

$env:SPICE_USERINIT_DIR = Split-Path -Parent $spiceInit
Start-Process -FilePath "ngspice" -ArgumentList @("-b", "-o", "ihp_sg13g2_device_level_ldo.log", "ihp_sg13g2_device_level_ldo.cir") -WindowStyle Hidden -Wait

if (-not (Test-Path "ihp_sg13g2_device_level_ldo.log")) {
    throw "ngspice did not create ihp_sg13g2_device_level_ldo.log"
}

Get-Content "ihp_sg13g2_device_level_ldo.log" | Select-String -Pattern "psr_1meg|error|warning|failed|singular" -CaseSensitive:$false

