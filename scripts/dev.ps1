# Dev launcher for smart_media
# NOTE: Uses separate windows so each service keeps running.

function Start-BackendMonitor {
    <#
    .SYNOPSIS
    Start backend monitor loop to keep uvicorn listening.

    .PARAMETER RepoRoot
    Absolute path to repository root.

    .OUTPUTS
    None. Starts a new PowerShell window running the monitor script.

    .SIDE EFFECTS
    Launches a new PowerShell process and may start uvicorn if not listening.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $monitorScript = Join-Path $RepoRoot 'scripts\monitor-backend.ps1'
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$monitorScript`""
}

function Test-PortListening {
    <#
    .SYNOPSIS
    Check whether a local TCP port is listening.

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

function Wait-BackendReady {
    <#
    .SYNOPSIS
    Wait for the backend port to become available before starting the frontend.

    .PARAMETER Port
    Port number to check.

    .PARAMETER TimeoutSeconds
    Max seconds to wait before giving up.

    .PARAMETER IntervalSeconds
    Polling interval in seconds.

    .OUTPUTS
    [bool] True if ready within timeout, otherwise false.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [int]$TimeoutSeconds = 30,
        [int]$IntervalSeconds = 1
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortListening -Port $Port) {
            return $true
        }

        Start-Sleep -Seconds $IntervalSeconds
    }

    return $false
}

function Start-FrontendDevServer {
    <#
    .SYNOPSIS
    Start Vite dev server for the frontend.

    .PARAMETER FrontendDir
    Absolute path to frontend directory.

    .OUTPUTS
    None. Starts a new PowerShell window running npm dev.

    .SIDE EFFECTS
    Launches a new PowerShell process running npm.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$FrontendDir
    )

    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location -LiteralPath '`"$FrontendDir`"'; npm run dev"
}

function Start-DevEnvironment {
    <#
    .SYNOPSIS
    Start backend monitor and frontend dev server.

    .PARAMETER RepoRoot
    Absolute path to repository root.

    .OUTPUTS
    None.

    .SIDE EFFECTS
    Launches multiple PowerShell windows.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $frontendDir = Join-Path $RepoRoot 'quark_strm\web'

    Start-BackendMonitor -RepoRoot $RepoRoot
    if (-not (Wait-BackendReady -Port 8000 -TimeoutSeconds 45 -IntervalSeconds 1)) {
        Write-Warning "Backend port 8000 not ready after 45s. Starting frontend anyway."
    }
    Start-FrontendDevServer -FrontendDir $frontendDir
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Start-DevEnvironment -RepoRoot $repoRoot
