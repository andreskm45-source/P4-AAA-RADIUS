#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Verifica el laboratorio P4 y genera un informe de evidencias.
.DESCRIPTION
    Comprueba conectividad, SSH, servicio NPS, clientes RADIUS, grupos de AD,
    eventos 6272/6273/6274 y el log de contabilidad. El resultado se guarda en
    ..\evidencias\verificacion_AAA_<fecha>.txt para adjuntarlo al repositorio.
.NOTES
    Autor : Rafael Andres Reyes De La Cruz - 2025-0784
    Uso   : .\03_Verificacion_AAA.ps1 -RouterIP 10.7.84.129 -SwitchIP 10.7.84.130
#>
[CmdletBinding()]
param(
    [string]$RouterIP  = "10.7.84.129",
    [string]$SwitchIP  = "10.7.84.130",
    [string]$ReportDir = (Join-Path $PSScriptRoot "..\evidencias")
)

$ErrorActionPreference = "Continue"
if (-not (Test-Path $ReportDir)) { New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null }
$report = Join-Path $ReportDir ("verificacion_AAA_{0:yyyyMMdd_HHmmss}.txt" -f (Get-Date))

function Section($t) {
    $line = "=" * 74
    Write-Output "`n$line`n $t`n$line"
}
function Try-Cmd($block) {
    try { & $block } catch { "ERROR: $($_.Exception.Message)" }
}

$out = @()
$out += "INFORME DE VERIFICACION - LABORATORIO P4 - AAA / RADIUS / NPS"
$out += "Autor      : Rafael Andres Reyes De La Cruz"
$out += "Matricula  : 2025-0784"
$out += "Red        : 10.7.84.0/24"
$out += "Equipo     : $env:COMPUTERNAME"
$out += "Fecha/hora : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
$out += "Router     : $RouterIP"
$out += "Switch     : $SwitchIP"

$out += (Section "1. CONECTIVIDAD ICMP")
foreach ($ip in @($RouterIP, $SwitchIP, "10.7.84.66")) {
    $ok = Test-Connection -ComputerName $ip -Count 2 -Quiet
    $out += ("{0,-14} {1}" -f $ip, $(if ($ok) { "OK" } else { "SIN RESPUESTA" }))
}

$out += (Section "2. SERVICIO SSH (TCP/22)")
foreach ($ip in @($RouterIP, $SwitchIP)) {
    $ok = Test-NetConnection -ComputerName $ip -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue
    $out += ("{0,-14} TCP/22 {1}" -f $ip, $(if ($ok) { "ABIERTO" } else { "CERRADO" }))
}

$out += (Section "3. SERVICIO NPS Y PUERTOS RADIUS")
$out += (Try-Cmd { Get-Service -Name IAS | Format-Table Name, Status, StartType -AutoSize | Out-String })
$udp = Get-NetUDPEndpoint -LocalPort 1812 -ErrorAction SilentlyContinue
$out += ("UDP/1812 en escucha: {0}" -f $(if ($udp) { "SI" } else { "NO" }))
$out += (Try-Cmd { Get-NpsRadiusClient | Select-Object Name, Address, AuthPort, AcctPort, Enabled | Format-Table -AutoSize | Out-String })

$out += (Section "4. GRUPOS Y USUARIOS DE ACTIVE DIRECTORY")
$out += (Try-Cmd {
    Get-ADGroup -Filter "Name -like 'GRP_NIVEL*'" | ForEach-Object {
        $members = (Get-ADGroupMember -Identity $_.Name | Select-Object -ExpandProperty SamAccountName) -join ", "
        "{0,-14} -> {1}" -f $_.Name, $members
    } | Out-String
})

$out += (Section "5. EVENTOS NPS (6272 acceso permitido / 6273 denegado / 6274 descartado)")
foreach ($id in 6272, 6273, 6274) {
    $out += "-- Evento $id (ultimos 5) --"
    $out += (Try-Cmd {
        Get-WinEvent -FilterHashtable @{ LogName = "Security"; Id = $id } -MaxEvents 5 -ErrorAction Stop |
            Select-Object TimeCreated, Id, @{ n = "Mensaje"; e = { ($_.Message -split "`r?`n")[0] } } |
            Format-Table -AutoSize | Out-String -Width 200
    })
}

$out += (Section "6. LOG DE CONTABILIDAD NPS (archivo de texto)")
$npsLog = Get-ChildItem "C:\P4\NPS-Logs\*.log" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($npsLog) {
    $out += "Archivo: $($npsLog.FullName)"
    $out += (Get-Content $npsLog.FullName -Tail 10 | Out-String)
} else {
    $out += "No se encontro log en C:\P4\NPS-Logs. Configure la contabilidad de NPS a archivo de texto."
}

$out += (Section "7. HORA DEL SERVIDOR (referencia para el video)")
$out += (Get-Date -Format "dddd, dd 'de' MMMM 'de' yyyy - HH:mm:ss")

$out | Tee-Object -FilePath $report
Write-Host "`n[OK] Informe guardado en: $report" -ForegroundColor Green
