<#
.SYNOPSIS
    Registra tareas programadas en Windows (Programador de Tareas) para que la Dell
    sincronice automaticamente desde GitHub al encender, cada 15 minutos y a la hora programada.
#>
param(
    [string]$RepoPath = "$env:USERPROFILE\legaltech-innovation-lab",
    [string]$MorningTime = "08:15",
    [int]$RepeatMinutes = 15
)

$ErrorActionPreference = "Stop"
$ScriptPath = Join-Path $RepoPath "ops\windows\sync_and_notify.ps1"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "No existe $ScriptPath"
    exit 1
}

$ActionArgs = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`" -RepoPath `"$RepoPath`""
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $ActionArgs

$LogonTrigger = New-ScheduledTaskTrigger -AtLogOn
$RepeatTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $RepeatMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 365)
$MorningTrigger = New-ScheduledTaskTrigger -Daily -At $MorningTime

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName "LegalTechLab-Dell-AutoSync" `
    -Action $Action `
    -Trigger @($LogonTrigger, $RepeatTrigger, $MorningTrigger) `
    -Settings $Settings `
    -Description "Sincroniza LegalTech Innovation Lab con GitHub y avisa cuando requiere revision humana." `
    -Force | Out-Null

Write-Output "Tarea programada 'LegalTechLab-Dell-AutoSync' registrada correctamente (al iniciar sesion, cada $RepeatMinutes min y diario $MorningTime)."
