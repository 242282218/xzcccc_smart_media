# Backend monitor for smart_media

function Test-BackendListening {
    <#
    .SYNOPSIS
    Check whether the backend port is listening.

    .PARAMETER Port
    Port number to check.

    .OUTPUTS
    [bool] True if listening, otherwise false.

    .SIDE EFFECTS
    None.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1
        return $null -ne $conn
    } catch {
        return $false
    }
}

function Start-Backend {
    <#
    .SYNOPSIS
    Start the uvicorn backend server.

    .PARAMETER BackendDir
    Absolute path to backend directory.

    .OUTPUTS
    None.

    .SIDE EFFECTS
    Launches uvicorn as a child process in the current window.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$BackendDir
    )

    Set-Location -LiteralPath $BackendDir
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
}

function Monitor-Backend {
    <#
    .SYNOPSIS
    Monitor backend port and start uvicorn if not listening.

    .PARAMETER BackendDir
    Absolute path to backend directory.

    .PARAMETER Port
    Port number to monitor.

    .PARAMETER IntervalSeconds
    Polling interval in seconds.

    .OUTPUTS
    None.

    .SIDE EFFECTS
    Starts uvicorn when the port is not listening.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$BackendDir,
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [int]$IntervalSeconds
    )

    while ($true) {
        if (-not (Test-BackendListening -Port $Port)) {
            Start-Backend -BackendDir $BackendDir
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot 'quark_strm'
Monitor-Backend -BackendDir $backendDir -Port 8000 -IntervalSeconds 5
