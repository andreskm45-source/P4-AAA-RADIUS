#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Instala y prepara NPS (RADIUS) para el laboratorio P4: registro en AD,
    clientes RADIUS, auditoria y reglas de firewall.
.DESCRIPTION
    - Instala la caracteristica NPAS (Network Policy Server) si falta.
    - Registra el servidor NPS en Active Directory.
    - Crea los clientes RADIUS P4-R1 (10.7.84.129) y P4-SW1 (10.7.84.130).
    - Habilita auditoria de NPS y de inicio de sesion.
    - Abre UDP 1812/1813 solo para la red 10.7.84.0/24.
    Las politicas de red (VSA shell:priv-lvl) se crean por GUI: ver
    docs/06_Servidor_AD_NPS.md (NPS no expone esas propiedades por PowerShell).
.NOTES
    Autor : Rafael Andres Reyes De La Cruz - 2025-0784
    Uso   : .\02_NPS_Setup.ps1
#>
[CmdletBinding()]
param(
    [string]$DomainName   = "p4.redes.local",
    [string]$ClientsCsv   = (Join-Path $PSScriptRoot "..\configs\nps\radius_clients.csv"),
    [string]$LogDir       = "C:\P4\logs",
    [string]$NpsLogDir    = "C:\P4\NPS-Logs"
)

$ErrorActionPreference = "Stop"
foreach ($d in @($LogDir, $NpsLogDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
Start-Transcript -Path (Join-Path $LogDir ("02_NPS_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))) -Force | Out-Null

try {
    # --- 1. Caracteristica NPS ----------------------------------------------
    $feature = Get-WindowsFeature -Name NPAS
    if (-not $feature.Installed) {
        Write-Host "[i] Instalando Network Policy Server (NPAS)..." -ForegroundColor Cyan
        Install-WindowsFeature -Name NPAS -IncludeManagementTools | Out-Null
    } else {
        Write-Host "[=] NPS ya esta instalado."
    }
    Import-Module NPS -ErrorAction Stop
    Import-Module ActiveDirectory -ErrorAction Stop

    # --- 2. Registro en Active Directory ------------------------------------
    try {
        Register-NPSInAD -ErrorAction Stop | Out-Null
        Write-Host "[+] NPS registrado en AD." -ForegroundColor Green
    } catch {
        Write-Warning "Register-NPSInAD: $($_.Exception.Message). Verifique que el equipo sea miembro del dominio."
    }

    # --- 3. Clientes RADIUS --------------------------------------------------
    if (-not (Test-Path $ClientsCsv)) { throw "No se encontro el CSV: $ClientsCsv" }
    $clients = Import-Csv -Path $ClientsCsv
    foreach ($c in $clients) {
        if (Get-NpsRadiusClient -Name $c.nombre -ErrorAction SilentlyContinue) {
            Remove-NpsRadiusClient -Name $c.nombre
        }
        try {
            New-NpsRadiusClient -Name $c.nombre -Address $c.ip -SharedSecret $c.secreto_compartido `
                -VendorName "Cisco" -AuthPort 1812 -AcctPort 1813 -Enabled $true | Out-Null
        } catch {
            Write-Warning "No se pudo asignar VendorName Cisco a $($c.nombre): $($_.Exception.Message)"
            New-NpsRadiusClient -Name $c.nombre -Address $c.ip -SharedSecret $c.secreto_compartido `
                -AuthPort 1812 -AcctPort 1813 -Enabled $true | Out-Null
        }
        Write-Host "[+] Cliente RADIUS: $($c.nombre) -> $($c.ip)" -ForegroundColor Green
    }

    # --- 4. Auditoria --------------------------------------------------------
    # Los nombres de subcategoria de auditpol estan localizados: se intentan
    # el nombre en ingles y el nombre en espanol.
    $auditTargets = @(
        @{ En = "Network Policy Server"; Es = "Servidor de directivas de red" },
        @{ En = "Logon";                Es = "Inicio de sesion" },
        @{ En = "Logoff";               Es = "Cierre de sesion" }
    )
    foreach ($t in $auditTargets) {
        $ok = $false
        foreach ($name in @($t.En, $t.Es)) {
            & auditpol /set /subcategory:"$name" /success:enable /failure:enable *> $null
            if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        }
        if ($ok) { Write-Host "[+] Auditoria habilitada: $($t.En)" -ForegroundColor Green }
        else { Write-Warning "No se pudo habilitar la auditoria '$($t.En)'. Use secpol.msc > Directivas locales > Directiva de auditoria." }
    }

    # --- 5. Firewall ---------------------------------------------------------
    $rules = @(
        @{ Name = "P4 RADIUS Auth UDP 1812"; Port = 1812 },
        @{ Name = "P4 RADIUS Acct UDP 1813"; Port = 1813 }
    )
    foreach ($r in $rules) {
        if (-not (Get-NetFirewallRule -DisplayName $r.Name -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -DisplayName $r.Name -Direction Inbound -Protocol UDP `
                -LocalPort $r.Port -RemoteAddress 10.7.84.0/24 -Action Allow | Out-Null
        }
    }
    Write-Host "[+] Firewall: UDP 1812/1813 permitido desde 10.7.84.0/24." -ForegroundColor Green

    # --- 6. Servicio ---------------------------------------------------------
    Set-Service -Name IAS -StartupType Automatic
    Start-Service -Name IAS
    Get-Service -Name IAS | Format-Table Name, Status, StartType -AutoSize

    # --- 7. Resumen y pasos manuales ----------------------------------------
    Write-Host "`n=== Clientes RADIUS configurados ===" -ForegroundColor Cyan
    Get-NpsRadiusClient | Select-Object Name, Address, AuthPort, AcctPort, Enabled | Format-Table -AutoSize

    Write-Host @"

=== PASOS MANUALES EN LA CONSOLA NPS (obligatorio) ===
1) NPS > Directivas > Directivas de red: crear las 3 politicas
   P4-NIVEL00 / P4-NIVEL05 / P4-NIVEL10 con condicion
   "Grupos de Windows" = P4\GRP_NIVELxx y atributo VSA Cisco
   Cisco-AV-Pair = shell:priv-lvl=0 | 5 | 10.
2) NPS > Contabilidad > Configurar contabilidad de NPS > Archivo de texto:
   carpeta $NpsLogDir  (formato DTS/ODBC, registrar autenticacion y contabilidad).
3) Reiniciar el servicio IAS despues de crear las politicas.
Detalle con capturas: docs/06_Servidor_AD_NPS.md
"@ -ForegroundColor Yellow
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript | Out-Null
}
