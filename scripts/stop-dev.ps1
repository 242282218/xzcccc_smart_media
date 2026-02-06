# Stop all dev services for smart_media

function Stop-ListeningPortProcess {
    <#
    .SYNOPSIS
    Stop the process listening on a given TCP port.

    .PARAMETER Port
    Port number to stop.

    .OUTPUTS
    None.

    .SIDE EFFECTS
    Terminates the process listening on the specified port.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        try {
            $pid = $conn.OwningProcess
            if ($pid -and $pid -ne 0) {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        } catch {
            # Ignore errors to keep script safe.
        }
    }
}

function Stop-DevEnvironment {
    <#
    .SYNOPSIS
    Stop frontend and backend dev services.

    .PARAMETER FrontendPort
    Frontend port to stop.

    .PARAMETER BackendPort
    Backend port to stop.

    .OUTPUTS
    None.

    .SIDE EFFECTS
    Terminates processes listening on the specified ports.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int]$FrontendPort,
        [Parameter(Mandatory = $true)]
        [int]$BackendPort
    )

    Stop-ListeningPortProcess -Port $FrontendPort
    Stop-ListeningPortProcess -Port $BackendPort
}

Stop-DevEnvironment -FrontendPort 3000 -BackendPort 8000
