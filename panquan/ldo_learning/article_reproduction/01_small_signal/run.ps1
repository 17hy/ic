$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$results = Join-Path $here "results"
New-Item -ItemType Directory -Force $results | Out-Null

Push-Location $here
try {
    Get-ChildItem -Filter "*.cir" | Sort-Object Name | ForEach-Object {
        $log = Join-Path $results "$($_.BaseName).log"
        Write-Host "Running $($_.Name)"
        Start-Process -FilePath "ngspice" -ArgumentList @("-b", "-o", $log, $_.Name) -WindowStyle Hidden -Wait
        if (-not (Test-Path $log)) {
            throw "ngspice did not create $log"
        }
    }
    Select-String -Path (Join-Path $results "*.log") -Pattern "psr_|ldo_max|ldo_min|tx_max|tx_min|rx_max|rx_min|conv_max|conv_min|dual_max|dual_min|error|warning|failed|singular" -CaseSensitive:$false
}
finally {
    Pop-Location
}

