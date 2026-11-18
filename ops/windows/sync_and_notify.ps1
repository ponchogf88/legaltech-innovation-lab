<#
.SYNOPSIS
    Sincronizacion automatica para Windows (AntiGravity Dell Lab) contra GitHub.
    Jala cambios nuevos en segundo plano, valida estado y envia alerta cuando se requiere revision humana.
#>
param(
    [string]$RepoPath = "$env:USERPROFILE\legaltech-innovation-lab",
    [string]$Branch = "main",
    [switch]$SendTestAlert
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

if (-not (Test-Path $RepoPath)) {
    Write-Error "Repositorio no encontrado en $RepoPath. Clona primero con: git clone https://github.com/ponchogf88/legaltech-innovation-lab.git"
    exit 1
}

Push-Location $RepoPath
try {
    $PythonExe = Join-Path $RepoPath ".venv\Scripts\python.exe"
    if (-not (Test-Path $PythonExe)) {
        $PythonExe = "python"
    }

    $LogDir = Join-Path $RepoPath "logs"
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

    git fetch origin $Branch --prune
    $LocalSha = (git rev-parse HEAD).Trim()
    $RemoteSha = (git rev-parse "origin/$Branch").Trim()
    $HasUpdates = $LocalSha -ne $RemoteSha

    $Porcelain = (git status --porcelain)
    if ($HasUpdates) {
        if ([string]::IsNullOrWhiteSpace($Porcelain)) {
            git checkout $Branch
            git pull --ff-only origin $Branch
            $Updated = $true
        } else {
            & $PythonExe -m legal_engine.cli notify `
                --level ACTION_REQUIRED `
                --node DELL_WINDOWS_LAB `
                --title "Cambios locales pendientes en Dell impiden auto-pull" `
                --summary "GitHub tiene commit nuevo ($RemoteSha), pero la Dell tiene cambios sin confirmar." `
                --action "Revisar git status en Dell y confirmar o guardar cambios."
            exit 0
        }
    } else {
        $Updated = $false
    }

    $HandshakePath = Join-Path $RepoPath "MULTI_NODE_HANDSHAKE.json"
    $NeedsAttention = $false
    $AttentionSummary = "Sin cambios nuevos en GitHub."

    if (Test-Path $HandshakePath) {
        $Handshake = Get-Content $HandshakePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($Handshake.requires_owner_review -or $Handshake.next_assigned_node -eq "DELL_WINDOWS_LAB") {
            $NeedsAttention = $true
            $AttentionSummary = "Ping activo: $($Handshake.active_ping_id) | Instruccion: $($Handshake.latest_instruction)"
        }
    }

    if ($Updated -or $SendTestAlert -or $NeedsAttention) {
        if ($NeedsAttention -or $SendTestAlert) {
            & $PythonExe -m legal_engine.cli notify `
                --level URGENT_REVIEW `
                --node DELL_WINDOWS_LAB `
                --title "LegalTech Lab listo en Dell: atencion / revision requerida" `
                --summary $AttentionSummary `
                --action "Abrir AntiGravity (Argon Max) en Dell y revisar ORCHESTRATOR_INBOX.md."
        }

        try {
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $Notify = New-Object System.Windows.Forms.NotifyIcon
            $Notify.Icon = [System.Drawing.SystemIcons]::Information
            $Notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
            $Notify.BalloonTipTitle = "LegalTech Lab · Sincronizado en Dell"
            $Notify.BalloonTipText = $AttentionSummary.Substring(0, [Math]::Min(180, $AttentionSummary.Length))
            $Notify.Visible = $true
            $Notify.ShowBalloonTip(7000)
            Start-Sleep -Seconds 2
            $Notify.Dispose()
        } catch {
            Write-Output "Aviso de escritorio omitido en sesion sin UI."
        }
    }

    & $PythonExe -m legal_engine.cli clock | Out-Null
    & $PythonExe -m legal_engine.cli state | Out-File -FilePath (Join-Path $LogDir "dell_sync_status.json") -Encoding utf8
    Write-Output "Dell Sync OK | Branch=$Branch | Updated=$Updated | Attention=$NeedsAttention"
}
finally {
    Pop-Location
}
