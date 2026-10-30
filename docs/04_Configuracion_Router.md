# 04 · Configuración del router R1-P4

**Archivo base:** [`configs/R1-P4_base.cfg`](../configs/R1-P4_base.cfg)
**Running-config de referencia:** [`configs/R1-P4_running-config.txt`](../configs/R1-P4_running-config.txt)

---

## 1. Preparación

1. En PNetLab, iniciar R1 y abrir la consola.
2. Verificar que la interfaz hacia el switch esté conectada a `Gi0/1` del SW1.
3. Cargar el archivo base. Dos opciones:

**Opción A — pegar por consola** (recomendada para dejar evidencia):

```text
enable
configure terminal
! pegar el contenido de configs/R1-P4_base.cfg
end
write memory
```

**Opción B — transferencia por TFTP/SCP** si el laboratorio lo permite.

4. Generar la clave RSA (necesaria para SSH):

```text
configure terminal
crypto key generate rsa modulus 2048
end
```

5. Verificar que el servidor NPS esté levantado antes de probar la consola con usuarios de AD.

> **Precaución:** antes de cambiar métodos AAA, abrir una segunda sesión de consola y ejecutar
> `reload in 5`. Si algo falla, la sesión se recupera sin reiniciar el equipo.

## 2. Bloques de configuración

### 2.1 Endurecimiento base

```text
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service password-encryption
service sequence-numbers
service tcp-keepalives-in
service tcp-keepalives-out
no service pad
no ip domain lookup
ip domain name p4.redes.local
no ip http server
no ip http secure-server
no ip source-route
no ip finger
```

| Comando | Propósito |
|---|---|
| `service timestamps ... localtime` | Fechas legibles en logs y capturas |
| `service password-encryption` | Evita contraseñas en claro en el archivo de configuración |
| `no ip http server` | Elimina la interfaz web de administración |
| `no ip source-route` | Descarta paquetes con rutas de origen (evita *spoofing*) |
| `no service pad` | Deshabilita el servicio PAD (X.25), sin uso |

### 2.2 Credenciales

```text
enable secret CAMBIAR_CLAVE
username admin.p4 privilege 15 secret CAMBIAR_CLAVE
```

- `enable secret` protege el paso a nivel 15 (hash tipo 5).
- `admin.p4` es el **usuario local** exigido por la tarea. Se usa para SSH y como respaldo.

### 2.3 SSH

```text
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
ip ssh logging events
```

Requisitos: `hostname`, `ip domain name` y clave RSA generada. Sin ellos, SSH no arranca.

### 2.4 RADIUS como cliente

```text
radius server NPS-P4
 address ipv4 10.7.84.66 auth-port 1812 acct-port 1813
 key CAMBIAR_CLAVE
 timeout 5
 retransmit 2

aaa group server radius RAD-P4
 server name NPS-P4
```

| Parámetro | Valor | Motivo |
|---|---|---|
| `timeout 5` | 5 s | Detecta rápido la caída de NPS y activa el *fallback* |
| `retransmit 2` | 2 | Tolera pérdida puntual sin demorar el login |
| `key` | secreto compartido | Debe coincidir **exactamente** con el cliente en NPS |

### 2.5 Métodos AAA

```text
aaa new-model
aaa session-id common
aaa authorization console

aaa authentication login CON-RADIUS group RAD-P4 local
aaa authorization exec CON-RADIUS group RAD-P4 local
aaa accounting exec CON-RADIUS start-stop group RAD-P4
aaa accounting commands 15 CON-RADIUS start-stop group RAD-P4
```

- `aaa authorization console` habilita la autorización en la consola (necesario para que
  `authorization exec` se aplique en `line con 0`).
- La lista `CON-RADIUS` se usa **solo** en consola y auxiliar.
- `accounting commands 15` registra los comandos de nivel 15 ejecutados.
- No se habilita `authorization commands 15` en la configuración principal: el administrador local no
  existe en AD y NPS podría rechazar la autorización por comando, dejando el equipo sin administración.
  La variante segura está en [`configs/opcional/command-authorization.cfg`](../configs/opcional/command-authorization.cfg).

### 2.6 Origen RADIUS y NTP

```text
ip radius source-interface GigabitEthernet0/0.99
ntp server 10.7.84.66
ntp source GigabitEthernet0/0.99
```

El origen debe ser `10.7.84.129` (la IP del SVI/subinterfaz de gestión). Esa dirección es la que se
registra como cliente RADIUS en NPS.

### 2.7 Logs de autenticación y autorización

```text
login on-failure log
login on-success log
logging buffered 16384 informational
logging console warnings
logging monitor informational
```

| Comando | Qué registra |
|---|---|
| `login on-failure log` | Intentos fallidos de login (global, IOS 15.2+) |
| `login on-success log` | Logins exitosos |
| `logging buffered` | Buffer local consultable con `show logging` |
| `aaa accounting exec` | Inicio y fin de sesión enviados a NPS |
| `aaa accounting commands 15` | Comandos privilegiados enviados a NPS |

> Si la plataforma no soporta `login on-failure log`, el IOS lo rechaza con `% Invalid input`; el resto
> de la auditoría (accounting + NPS) sigue funcionando. Ver
> [11 · Troubleshooting](11_Troubleshooting.md).

### 2.8 Niveles de privilegio

Por defecto IOS ya separa nivel 1 (usuario) de nivel 15 (privilegiado). Para que el nivel 10 sea útil:

```text
privilege exec level 10 show running-config
privilege exec level 10 show startup-config
privilege exec level 10 configure
privilege exec level 10 write
```

Resultado:

| Nivel | Puede | No puede |
|---:|---|---|
| 0 | `enable`, `disable`, `help`, `exit`, `logout` | `show`, `ping`, configuración |
| 5 | `show`, `ping`, `traceroute`, `show logging` | `show running-config`, `configure` |
| 10 | Lo anterior + `show running-config`, `configure terminal`, `write` | Comandos de nivel 15 dentro de config (p. ej. `aaa`, `username`) |
| 15 | Todo | — |

### 2.9 Interfaces

```text
interface GigabitEthernet0/0
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.7.84.1 255.255.255.192
 ip access-group ACL-USUARIOS-IN in
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.7.84.65 255.255.255.192
!
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99
 ip address 10.7.84.129 255.255.255.192
!
interface GigabitEthernet0/0.999
 encapsulation dot1Q 999 native
 no ip address
 shutdown
```

La subinterfaz nativa se deja **sin IP y apagada**: no debe transportar tráfico de gestión.

### 2.10 Líneas

```text
line con 0
 login authentication CON-RADIUS
 authorization exec CON-RADIUS
 accounting exec CON-RADIUS
 accounting commands 15 CON-RADIUS
 exec-timeout 5 0
 logging synchronous
line aux 0
 login authentication CON-RADIUS
 authorization exec CON-RADIUS
 accounting exec CON-RADIUS
 accounting commands 15 CON-RADIUS
 exec-timeout 5 0
 logging synchronous
line vty 0 4
 login local
 transport input ssh
 access-class SSH-ADMIN in
 exec-timeout 10 0
line vty 5 15
 login local
 transport input none
```

Esta es la evidencia textual del requisito **«solo consola y auxiliar»**: las VTY no tienen ninguna
directiva AAA y usan `login local`.

## 3. Verificación

```text
R1-P4# show aaa servers
RADIUS: id 1, priority 1, host 10.7.84.66, auth-port 1812, acct-port 1813
     State: current UP, duration 842s, previous state: DOWN
     Requests: 14, Retransmits: 0, Timeouts: 0

R1-P4# show running-config | section line
line con 0
 login authentication CON-RADIUS
 authorization exec CON-RADIUS
 accounting exec CON-RADIUS
 accounting commands 15 CON-RADIUS
 exec-timeout 5 0
 logging synchronous
line aux 0
 ...
line vty 0 4
 access-class SSH-ADMIN in
 login local
 transport input ssh
line vty 5 15
 login local
 transport input none

R1-P4# show ip ssh
SSH Enabled - version 2.0
Authentication timeout: 60 secs; Authentication retries: 3

R1-P4# show privilege
Current privilege level is 15
```

Prueba rápida de autenticación (no sustituye la prueba por consola):

```text
R1-P4# test aaa group RAD-P4 usr.nivel5 CAMBIAR_CLAVE legacy
Attempting authentication via legacy method
User successfully authenticated
```


## 4. Evidencias que debe capturar

| Archivo | Qué mostrar |
|---|---|
| `images/02_r1_show_run_aaa.png` | `show running-config \| section aaa` y `section line` |
| `images/15_show_aaa_servers.png` | `show aaa servers` en estado UP |
| `images/16_show_logging.png` | `show logging` con eventos de login/AAA |
| `images/04_consola_nivel0.png` | Prompt `>` con `show privilege` → 0 |
| `images/05_consola_nivel5.png` | `show privilege` → 5 y `show version` funcionando |
| `images/06_consola_nivel10.png` | `show privilege` → 10 y `show running-config` funcionando |
| `images/07_consola_admin_fallback.png` | NPS detenido + login con `admin.p4` |

## 5. Respaldo y restauración

```text
copy running-config startup-config
copy running-config tftp:
show archive
```

Guardar una copia en el repositorio (`configs/R1-P4_running-config.txt`) después de cada cambio
validado. Si se pierde el acceso, reiniciar y entrar por consola: el usuario local sigue disponible
con NPS caído.

---

**Anterior:** [03 · Direccionamiento](03_Direccionamiento_IP.md) · **Siguiente:** [05 · Switch](05_Configuracion_Switch.md)
