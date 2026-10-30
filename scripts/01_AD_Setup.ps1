#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Crea la estructura de Active Directory del laboratorio P4 (OU, grupos y usuarios).
.DESCRIPTION
    - OU P4 > Usuarios / Grupos
    - Grupos de seguridad: GRP_NIVEL0, GRP_NIVEL5, GRP_NIVEL10
    - Usuarios usr.nivel0, usr.nivel5, usr.nivel10 (habilitados para NPS)
    - Habilita el servidor NTP (w32time) para que R1/SW1 sincronicen la hora
    Script idempotente: se puede ejecutar varias veces sin duplicar objetos.
.NOTES
    Autor : Rafael Andres Reyes De La Cruz - 2025-0784
    Equipo: SRV1-P4 (Windows Server 2019/2022, controlador de dominio)
    Uso   : .\01_AD_Setup.ps1 -DomainName p4.redes.local
#>
[CmdletBinding()]
param(
    [string]$DomainName = "p4.redes.local",
    [string]$LogDir     = "C:\P4\logs"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
Start-Transcript -Path (Join-Path $LogDir ("01_AD_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))) -Force | Out-Null

try {
    Import-Module ActiveDirectory -ErrorAction Stop
    $domain = Get-ADDomain -Identity $DomainName
    $baseDN = $domain.DistinguishedName
    Write-Host "[i] Dominio: $DomainName ($baseDN)" -ForegroundColor Cyan

    function Ensure-OU {
        param([string]$Name, [string]$ParentDN)
        $dn = "OU=$Name,$ParentDN"
        try {
            Get-ADOrganizationalUnit -Identity $dn -ErrorAction Stop | Out-Null
            Write-Host "    [=] OU existente: $dn"
        } catch {
            New-ADOrganizationalUnit -Name $Name -Path $ParentDN -ProtectedFromAccidentalDeletion $true
            Write-Host "    [+] OU creada: $dn" -ForegroundColor Green
        }
        return $dn
    }

    $ouRoot   = Ensure-OU -Name "P4"       -ParentDN $baseDN
    $ouUsers  = Ensure-OU -Name "Usuarios" -ParentDN $ouRoot
    $ouGroups = Ensure-OU -Name "Grupos"   -ParentDN $ouRoot

    # --- Grupos de seguridad -------------------------------------------------
    $groups = @(
        @{ Name = "GRP_NIVEL0";  Desc = "P4 - Privilegio IOS 0 (solo consulta minima)" },
        @{ Name = "GRP_NIVEL5";  Desc = "P4 - Privilegio IOS 5 (monitoreo)" },
        @{ Name = "GRP_NIVEL10"; Desc = "P4 - Privilegio IOS 10 (operador)" }
    )

    foreach ($g in $groups) {
        try {
            Get-ADGroup -Identity $g.Name -ErrorAction Stop | Out-Null
            Write-Host "    [=] Grupo existente: $($g.Name)"
        } catch {
            New-ADGroup -Name $g.Name -SamAccountName $g.Name -GroupScope Global `
                -GroupCategory Security -Path $ouGroups -Description $g.Desc
            Write-Host "    [+] Grupo creado: $($g.Name)" -ForegroundColor Green
        }
    }

    # --- Usuarios ------------------------------------------------------------
    $users = @(
        @{ Sam = "usr.nivel0";  Nombre = "Usuario Nivel 0";  Pass = "CAMBIAR_CLAVE";  Grupo = "GRP_NIVEL0"  },
        @{ Sam = "usr.nivel5";  Nombre = "Usuario Nivel 5";  Pass = "CAMBIAR_CLAVE";  Grupo = "GRP_NIVEL5"  },
        @{ Sam = "usr.nivel10"; Nombre = "Usuario Nivel 10"; Pass = "CAMBIAR_CLAVE"; Grupo = "GRP_NIVEL10" }
    )

    foreach ($u in $users) {
        $upn = "$($u.Sam)@$DomainName"
        try {
            Get-ADUser -Identity $u.Sam -ErrorAction Stop | Out-Null
            Write-Host "    [=] Usuario existente: $($u.Sam)"
        } catch {
            New-ADUser -Name $u.Nombre -DisplayName $u.Nombre -SamAccountName $u.Sam `
                -UserPrincipalName $upn -Path $ouUsers -Enabled $true `
                -AccountPassword (ConvertTo-SecureString $u.Pass -AsPlainText -Force) `
                -PasswordNeverExpires $true -ChangePasswordAtLogon $false
            Write-Host "    [+] Usuario creado: $($u.Sam)" -ForegroundColor Green
        }

        # Permite la autenticacion RADIUS/NPS sin depender de la propiedad de marcado
        Set-ADUser -Identity $u.Sam -Replace @{ msNPAllowDialin = $true }

        $member = Get-ADGroupMember -Identity $u.Grupo | Where-Object { $_.SamAccountName -eq $u.Sam }
        if (-not $member) {
            Add-ADGroupMember -Identity $u.Grupo -Members $u.Sam
            Write-Host "    [+] $($u.Sam) agregado a $($u.Grupo)" -ForegroundColor Green
        }
    }

    # --- NTP: el DC entrega hora a R1 y SW1 ----------------------------------
    Write-Host "[i] Habilitando servidor NTP (w32time)..." -ForegroundColor Cyan
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer" -Name Enabled -Value 1
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\Config" -Name AnnounceFlags -Value 5
    & w32tm /config /reliable:yes /update | Out-Null
    Restart-Service w32time -Force
    if (-not (Get-NetFirewallRule -DisplayName "P4 NTP UDP 123" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -DisplayName "P4 NTP UDP 123" -Direction Inbound -Protocol UDP `
            -LocalPort 123 -Action Allow | Out-Null
    }

    # --- Resumen -------------------------------------------------------------
    Write-Host "`n=== Resumen ===" -ForegroundColor Cyan
    Get-ADGroup -Filter "Name -like 'GRP_NIVEL*'" | ForEach-Object {
        $n = ($_ | Get-ADGroupMember).Count
        "{0,-14} miembros: {1}" -f $_.Name, $n
    }
    Get-ADUser -Filter "SamAccountName -like 'usr.*'" -Properties msNPAllowDialin |
        Select-Object SamAccountName, Enabled, msNPAllowDialin | Format-Table -AutoSize
    Write-Host "[OK] Estructura de AD lista." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript | Out-Null
}
