param(
    [string]$Ngspice = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if ($Ngspice -eq "") {
    $Workspace = Split-Path -Parent $Root
    $Ngspice = Join-Path $Workspace "Spice64\bin\ngspice_con.exe"
}

if (-not (Test-Path -LiteralPath $Ngspice)) {
    throw "ngspice executable not found: $Ngspice"
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "results") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Root "logs") | Out-Null

$circuits = Get-ChildItem -LiteralPath (Join-Path $Root "circuits") -Recurse -Filter *.cir |
    Sort-Object FullName

$failed = @()
foreach ($circuit in $circuits) {
    $log = Join-Path $Root ("logs\" + $circuit.BaseName + ".log")
    Write-Host ("running " + $circuit.BaseName)
    Push-Location $circuit.DirectoryName
    & $Ngspice -b -o $log $circuit.Name
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) {
        $failed += $circuit.FullName
    }
}

if ($failed.Count -gt 0) {
    Write-Host "FAILED:"
    $failed | ForEach-Object { Write-Host $_ }
    exit 1
}

Write-Host ("completed " + $circuits.Count + " simulations")
