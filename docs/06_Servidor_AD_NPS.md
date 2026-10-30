# 06 · Servidor SRV1-P4: Active Directory y NPS

**Servidor:** Windows Server 2019/2022 · **IP:** 10.7.84.66/26 · **Dominio:** `p4.redes.local`
**Scripts:** [`scripts/01_AD_Setup.ps1`](../scripts/01_AD_Setup.ps1) · [`scripts/02_NPS_Setup.ps1`](../scripts/02_NPS_Setup.ps1)

---

## 1. Preparación de la máquina virtual

| Recurso | Valor sugerido |
|---|---|
| vCPU / RAM / disco | 2 vCPU · 4 GB · 40 GB |
| Nombre del equipo | `SRV1-P4` |
| NIC | Conectada al puerto `Gi0/2` del SW1 (VLAN 20) |
| IP | 10.7.84.66 |
| Máscara | 255.255.255.192 (/26) |
| Gateway | 10.7.84.65 |
| DNS | 127.0.0.1 (tras promover el dominio) |

Configuración por PowerShell (ejecutar como administrador):

```powershell
Rename-Computer -NewName "SRV1-P4" -Restart
New-NetIPAddress -InterfaceAlias "Ethernet0" -IPAddress 10.7.84.66 -PrefixLength 26 -DefaultGateway 10.7.84.65
Set-DnsClientServerAddress -InterfaceAlias "Ethernet0" -ServerAddresses 127.0.0.1
```

> Antes de promover el dominio, el DNS debe apuntar a `127.0.0.1`. Si se deja un DNS externo, la
> promoción falla o el dominio queda mal registrado.

## 2. Instalación de Active Directory

```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName "p4.redes.local" -DomainNetbiosName "P4" `
    -InstallDns -Force -NoRebootOnCompletion:$false
```

Tras el reinicio, verificar:

```powershell
Get-ADDomain | Select-Object DNSRoot, NetBIOSName, DistinguishedName
Get-Service NTDS, DNS | Format-Table Name, Status
```

## 3. Grupos y usuarios

Se crean **tres grupos de seguridad globales** y **tres usuarios**, uno por nivel.

| Grupo | Nivel IOS | Usuario | Contraseña (laboratorio) |
|---|---:|---|---|
| `GRP_NIVEL0` | 0 | `usr.nivel0` | `CAMBIAR_CLAVE` |
| `GRP_NIVEL5` | 5 | `usr.nivel5` | `CAMBIAR_CLAVE` |
| `GRP_NIVEL10` | 10 | `usr.nivel10` | `CAMBIAR_CLAVE` |

Ejecutar:

```powershell
cd C:\P4\scripts
.\01_AD_Setup.ps1 -DomainName p4.redes.local
```

El script crea la OU `P4` con las sub-OU `Usuarios` y `Grupos`, y marca cada usuario con
`msNPAllowDialin = TRUE` para que NPS no los rechace por la propiedad de marcado.

Verificación:

```powershell
Get-ADGroup -Filter "Name -like 'GRP_NIVEL*'" | Format-Table Name, GroupScope, GroupCategory
Get-ADGroupMember GRP_NIVEL10 | Select-Object SamAccountName, objectClass
Get-ADUser usr.nivel5 -Properties msNPAllowDialin | Select-Object SamAccountName, Enabled, msNPAllowDialin
```



## 4. Instalación de NPS

```powershell
Install-WindowsFeature NPAS -IncludeManagementTools
Import-Module NPS
Register-NPSInAD
Get-Service IAS | Format-Table Name, Status, StartType
Restart-Service IAS
```

Si `Register-NPSInAD` no está disponible, usar la consola gráfica: **NPS → botón derecho sobre
«NPS (Local)» → Registrar servidor en Active Directory**.

## 5. Clientes RADIUS

Los clientes son las **direcciones de origen** del tráfico RADIUS, no las interfaces del trunk.

| Cliente | IP | Secreto | Vendor |
|---|---|---|---|
| `P4-R1` | 10.7.84.129 | `CAMBIAR_CLAVE` | Cisco |
| `P4-SW1` | 10.7.84.130 | `CAMBIAR_CLAVE` | Cisco |

```powershell
.\02_NPS_Setup.ps1
Get-NpsRadiusClient | Format-Table Name, Address, AuthPort, AcctPort, Enabled
```

Configuración manual equivalente: **NPS → RADIUS (Local) → Clientes RADIUS y servidores → Clientes
RADIUS → Nuevo**:

1. Nombre descriptivo: `P4-R1`.
2. Dirección: `10.7.84.129`.
3. Secreto compartido: el mismo del IOS (manual, no generar).
4. Avanzado → Proveedor: **Cisco**.


## 6. Políticas de red (VSA `shell:priv-lvl`)

Se crean **tres políticas**, una por grupo. NPS evalúa las políticas en orden; como cada usuario
pertenece a un solo grupo, el orden no altera el resultado, pero se documenta de mayor a menor
privilegio.

### 6.1 Datos de cada política

| Política | Condición (Grupos de Windows) | VSA Cisco-AV-Pair |
|---|---|---|
| `P4-NIVEL10` | `P4\GRP_NIVEL10` | `shell:priv-lvl=10` |
| `P4-NIVEL05` | `P4\GRP_NIVEL5` | `shell:priv-lvl=5` |
| `P4-NIVEL00` | `P4\GRP_NIVEL0` | `shell:priv-lvl=0` |

Parámetros comunes:

- **Tipo de directiva:** Acceso concedido.
- **Método de autenticación:** PAP sin cifrar (PAP, SPAP). El login de IOS viaja como PAP dentro del
  túnel cifrado por el secreto RADIUS; sin PAP habilitado, NPS rechaza la petición.
- **Atributo estándar opcional:** `Service-Type = Login`.

### 6.2 Procedimiento en la consola NPS

1. **NPS → Directivas → Directivas de red → Nueva**.
2. Nombre: `P4-NIVEL10`.
3. Tipo de acceso: **Acceso concedido**.
4. **Condiciones → Agregar → Grupos de Windows**: escribir `P4\GRP_NIVEL10` y aceptar.
5. **Restricciones → Métodos de autenticación → Agregar**: `PAP sin cifrar (PAP, SPAP)`.
6. **Configuración → Atributos RADIUS → Atributos específicos del proveedor → Agregar**:
   - Proveedor: **Cisco**
   - Atributo: **Cisco-AV-Pair**
   - Valor: `shell:priv-lvl=10`
7. Aceptar y repetir para nivel 5 y nivel 0.
8. Reiniciar el servicio `IAS`.



> El atributo **debe** ser `Cisco-AV-Pair` (vendor 9, atributo 1). Si se escribe como atributo
> estándar, IOS lo ignora y el usuario queda en el nivel por defecto (1/15 según la plataforma).

## 7. Directiva de solicitud de conexión

NPS trae por defecto **«Usar autenticación de Windows para todas las solicitudes»**. Es suficiente
para este laboratorio porque NPS está en el DC y valida contra AD.

Si se crea una política propia (**Directivas → Directivas de solicitud de conexión → Nueva**):

- Condición: `Tipo de puerto NAS = Virtual (VPN)` no aplica; dejar sin condición o usar
  `Dirección IPv4 del NAS = 10.7.84.129` / `.130` en políticas separadas.
- **Configuración → Omitir las propiedades de marcado del usuario**: marcado. Evita que la propiedad
  «Denegar acceso» del usuario bloquee la autenticación.
- Proveedor de autenticación: **Seguridad de Windows**.

## 8. Contabilidad y auditoría

### 8.1 Log de contabilidad en archivo de texto

**NPS → Contabilidad → Configurar contabilidad de NPS**:

1. Seleccionar **Registrar en un archivo de texto**.
2. Carpeta: `C:\P4\NPS-Logs`.
3. Formato: **DTS** (compatible con Excel) o **ODBC**.
4. Marcar **Autenticación** y **Contabilidad**.

Cada `Accounting-Request` de IOS genera una línea con inicio/fin de sesión y los comandos de nivel 15.

### 8.2 Auditoría de eventos

```powershell
auditpol /set /subcategory:"Network Policy Server" /success:enable /failure:enable
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
```

> En un Windows en español las subcategorías se llaman **«Servidor de directivas de red»**,
> **«Inicio de sesión»** y **«Cierre de sesión»**. El script `02_NPS_Setup.ps1` intenta ambos nombres;
> también se pueden habilitar en `secpol.msc → Directivas locales → Directiva de auditoría`.

| Evento | Significado |
|---:|---|
| **6272** | Acceso concedido por NPS |
| **6273** | Acceso denegado por NPS |
| **6274** | Solicitud descartada (cliente desconocido, secreto incorrecto, etc.) |
| **4624** | Inicio de sesión correcto en Windows |
| **4625** | Error de inicio de sesión en Windows |

Consulta rápida:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=6272} -MaxEvents 10 |
    Select-Object TimeCreated, Id, @{n='Mensaje';e={($_.Message -split "`n")[0]}}
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=6273} -MaxEvents 10
```



## 9. Firewall y hora

```powershell
# Firewall: solo la red del laboratorio
New-NetFirewallRule -DisplayName "P4 RADIUS Auth UDP 1812" -Direction Inbound -Protocol UDP `
    -LocalPort 1812 -RemoteAddress 10.7.84.0/24 -Action Allow
New-NetFirewallRule -DisplayName "P4 RADIUS Acct UDP 1813" -Direction Inbound -Protocol UDP `
    -LocalPort 1813 -RemoteAddress 10.7.84.0/24 -Action Allow

# NTP para que R1/SW1 registren la misma hora
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer" -Name Enabled -Value 1
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\Config" -Name AnnounceFlags -Value 5
w32tm /config /reliable:yes /update
Restart-Service w32time
```

Verificar en el router: `show ntp status` debe indicar `synchronized`. Si no sincroniza, ajustar la hora
manualmente en cada equipo (`clock set`) antes de grabar el video.

## 10. Endurecimiento del servidor

| Medida | Comando / acción |
|---|---|
| Firewall activo en todos los perfiles | `Set-NetFirewallProfile -All -Enabled True` |
| SMBv1 deshabilitado | `Disable-WindowsOptionalFeature -Online -FeatureName smb1protocol` |
| RDP solo desde la red del laboratorio | Regla de firewall TCP 3389 con `-RemoteAddress 10.7.84.0/24` |
| Cuentas locales mínimas | Solo el administrador integrado, con contraseña fuerte |
| Registro de auditoría protegido | Permisos de escritura solo para SYSTEM/Administradores |
| Actualizaciones | `Install-WindowsUpdate` o WSUS en producción |
| NPS registrado en AD | `Register-NPSInAD` |
| Copia de configuración de NPS | `netsh nps export filename="C:\P4\nps-backup.xml" exportPSK=YES` |

> `exportPSK=YES` incluye los secretos compartidos en el XML: guardar el respaldo fuera del repositorio
> público.

## 11. Verificación integral

```powershell
.\03_Verificacion_AAA.ps1 -RouterIP 10.7.84.129 -SwitchIP 10.7.84.130
```

El script genera `evidencias/verificacion_AAA_<fecha>.txt` con: conectividad, SSH, servicio NPS,
clientes RADIUS, grupos de AD, eventos 6272/6273/6274, log de contabilidad y hora del servidor.

---

**Anterior:** [05 · Switch](05_Configuracion_Switch.md) · **Siguiente:** [07 · Pruebas y evidencias](07_Pruebas_Evidencias.md)
