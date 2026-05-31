$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $here "..\..\..")
$results = Join-Path $here "results"
New-Item -ItemType Directory -Force $results | Out-Null

if ($env:PDK_ROOT -and (Test-Path (Join-Path $env:PDK_ROOT "ihp-sg13g2\libs.tech\ngspice\models"))) {
    $pdkRoot = $env:PDK_ROOT
}
else {
    $cacheRoot = Join-Path $here "_pdk_cache"
    $pdkRoot = Join-Path $cacheRoot "IHP-Open-PDK"
    if (-not (Test-Path $pdkRoot)) {
        New-Item -ItemType Directory -Force $cacheRoot | Out-Null
        git clone --depth 1 --filter=blob:none --sparse https://github.com/IHP-GmbH/IHP-Open-PDK.git $pdkRoot
        Push-Location $pdkRoot
        try {
            git sparse-checkout set ihp-sg13g2/libs.tech/ngspice
        }
        finally {
            Pop-Location
        }
    }
}

$env:PDK = "ihp-sg13g2"
$modelDir = Join-Path $pdkRoot "ihp-sg13g2\libs.tech\ngspice\models"
if (-not (Test-Path $modelDir)) {
    throw "Cannot find IHP model directory: $modelDir"
}

$ngspicePath = (Get-Command ngspice).Source
$ngRoot = Split-Path (Split-Path $ngspicePath -Parent) -Parent
$osdiDir = if ($env:NGSPICE_OSDI_DIR) { $env:NGSPICE_OSDI_DIR } else { Join-Path $ngRoot "lib\ngspice" }

foreach ($file in @("psp103.osdi", "psp103_nqs.osdi", "r3_cmc.osdi", "mosvar.osdi")) {
    if (-not (Test-Path (Join-Path $osdiDir $file))) {
        throw "Missing OSDI model $file in $osdiDir"
    }
}

$spiceInit = Join-Path $here ".spiceinit"
@(
    "setcs sourcepath = ( `$sourcepath $modelDir )",
    "osdi '$osdiDir\psp103.osdi'",
    "osdi '$osdiDir\psp103_nqs.osdi'",
    "osdi '$osdiDir\r3_cmc.osdi'",
    "osdi '$osdiDir\mosvar.osdi'"
) | Set-Content $spiceInit -Encoding ASCII

Push-Location $here
try {
    Get-Item "pdk_direct_sg13g2_psr.cir" | ForEach-Object {
        $log = Join-Path $results "$($_.BaseName).log"
        Write-Host "Running $($_.Name)"
        Start-Process -FilePath "ngspice" -ArgumentList @("-b", "-o", $log, $_.Name) -WindowStyle Hidden -Wait
        if (-not (Test-Path $log)) {
            throw "ngspice did not create $log"
        }
    }
    Select-String -Path (Join-Path $results "*.log") -Pattern 'v\(|psr_|error|warning|failed|singular|temperature limiting' -CaseSensitive:$false
}
finally {
    Pop-Location
}
