param(
    [string]$Ngspice = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Ngspice -eq "") {
    $Workspace = Split-Path -Parent (Split-Path -Parent $Root)
    $Ngspice = Join-Path $Workspace "Spice64\bin\ngspice_con.exe"
}

if (-not (Test-Path -LiteralPath $Ngspice)) {
    throw "ngspice executable not found: $Ngspice"
}

python (Join-Path $Root "scripts\run_chapter5.py") --ngspice $Ngspice
