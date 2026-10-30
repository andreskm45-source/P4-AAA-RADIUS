# 05 · Configuración del switch SW1-P4

**Archivo base (Catalyst 2960):** [`configs/SW1-P4_base.cfg`](../configs/SW1-P4_base.cfg)
**Variante IOU/IOL L2:** [`configs/variantes/SW1-P4_IOU_L2.cfg`](../configs/variantes/SW1-P4_IOU_L2.cfg)
**Running-config de referencia:** [`configs/SW1-P4_running-config.txt`](../configs/SW1-P4_running-config.txt)

---

## 1. Preparación y adaptación de interfaces

| Imagen | Trunk hacia R1 | Servidor | Puerto demo |
|---|---|---|---|
| Catalyst 2960 | `Gi0/1` | `Gi0/2` | `Gi0/3` |
| IOU/IOL L2 | `Et0/0` | `Et0/1` | `Et0/2` |

Antes de pegar el archivo, confirmar los nombres reales:

```text
show ip interface brief
show interfaces status
```

> En IOU/IOL no existe `line aux 0`. Omitir ese bloque: el requisito se cumple sobre la consola y se
> documenta la limitación de la plataforma.

## 2. Endurecimiento de Capa 2

### 2.1 VLANs

```text
vlan 10
 name USUARIOS
vlan 20
 name SERVIDORES
vlan 99
 name GESTION-AAA
vlan 999
 name NATIVA-PARKING
```

### 2.2 Trunk

```text
interface GigabitEthernet0/1
 description TRUNK-HACIA-R1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
 switchport nonegotiate
 no shutdown
```

| Medida | Riesgo que mitiga |
|---|---|
| VLAN nativa 999 sin hosts | *VLAN hopping* mediante tramas sin etiqueta |
| `allowed vlan` explícita | Propaga solo las VLAN necesarias |
| `nonegotiate` | Deshabilita DTP y la negociación de trunk |

### 2.3 Puertos de acceso

```text
interface GigabitEthernet0/2
 description SRV1-P4-AD-NPS-VLAN20
 switchport mode access
 switchport access vlan 20
 switchport nonegotiate
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 spanning-tree portfast
 spanning-tree bpduguard enable
 storm-control broadcast level 5.00
 no cdp enable
```

- **Port-security sticky**: aprende la MAC del servidor y la fija. Si el servidor cambia de NIC o de
  máquina virtual, hay que liberar la MAC (`clear port-security sticky interface Gi0/2`).
- **BPDU guard**: si alguien conecta un switch, el puerto entra en *err-disabled*.
- **Storm-control**: limita broadcast al 5 %.
- **`no cdp enable`**: no anuncia información del equipo al servidor.

### 2.4 Puertos no usados

```text
interface range GigabitEthernet0/4-24
 description PUERTO-NO-USADO
 switchport mode access
 switchport access vlan 999
 shutdown
```

### 2.5 DHCP snooping

```text
ip dhcp snooping
ip dhcp snooping vlan 10
no ip dhcp snooping information option
interface GigabitEthernet0/1
 ip dhcp snooping trust
```

El trunk se marca como confiable porque el servidor DHCP real es R1. La opción 82 se desactiva para
evitar que el router descarte solicitudes en un entorno de laboratorio.

## 3. Gestión y AAA

```text
interface Vlan99
 description GESTION-AAA
 ip address 10.7.84.130 255.255.255.192
 no shutdown
ip default-gateway 10.7.84.129
```

```text
radius server NPS-P4
 address ipv4 10.7.84.66 auth-port 1812 acct-port 1813
 key CAMBIAR_CLAVE
 timeout 5
 retransmit 2

aaa group server radius RAD-P4
 server name NPS-P4

aaa authentication login CON-RADIUS group RAD-P4 local
aaa authorization exec CON-RADIUS group RAD-P4 local
aaa accounting exec CON-RADIUS start-stop group RAD-P4
aaa accounting commands 15 CON-RADIUS start-stop group RAD-P4

ip radius source-interface Vlan99
```

> **Importante:** el switch es un equipo de Capa 2; su tráfico RADIUS sale por `Vlan99` y llega al
> servidor a través del router (`ip default-gateway 10.7.84.129`). Si falta el gateway por defecto,
> `show aaa servers` queda en estado `DEAD`.

> **Si el switch rechaza `radius server NPS-P4`** con `% Invalid input detected at '^' marker.`, la
> imagen de IOS es anterior a la sintaxis de objeto servidor (habitual en 2960 con 12.2(55)SE o
> 15.0(2)SE). En ese caso se reemplaza solo el bloque de definición del servidor y del grupo por la
> variante legacy de [`configs/legacy/radius-legacy.cfg`](../configs/legacy/radius-legacy.cfg), que usa
> `radius-server host` + `aaa group server radius` con `server 10.7.84.66`. Las listas de métodos, el
> `ip radius source-interface` y el resto de la configuración no cambian.

### Líneas

```text
line con 0
 login authentication CON-RADIUS
 authorization exec CON-RADIUS
 accounting exec CON-RADIUS
 accounting commands 15 CON-RADIUS
 exec-timeout 5 0
 logging synchronous
line aux 0
 ... (omitir si la plataforma no lo tiene)
line vty 0 4
 login local
 transport input ssh
 access-class SSH-ADMIN in
 exec-timeout 10 0
line vty 5 15
 login local
 transport input none
```

## 4. Verificación

```text
SW1-P4# show vlan brief
SW1-P4# show interfaces trunk
SW1-P4# show interfaces status
SW1-P4# show port-security
SW1-P4# show ip dhcp snooping
SW1-P4# show aaa servers
SW1-P4# show running-config | section line
SW1-P4# show privilege
```

Salidas esperadas (extracto):

```text
SW1-P4# show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      999

Port        Vlans allowed on trunk
Gi0/1       10,20,99

SW1-P4# show port-security
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
                (Count)       (Count)          (Count)
---------------------------------------------------------------------------
        Gi0/2              1            1                  0          Restrict
        Gi0/3              1            0                  0          Restrict

SW1-P4# show aaa servers
RADIUS: id 1, priority 1, host 10.7.84.66, auth-port 1812, acct-port 1813
     State: current UP, duration 415s, previous state: DOWN
```


## 5. Evidencias que debe capturar

| Archivo | Qué mostrar |
|---|---|
| `images/03_sw1_show_run_aaa.png` | `show running-config \| section aaa` y `section line` |
| `images/20_ping_validacion.png` | Ping desde SRV1 a R1 y SW1 por VLAN 99 |
| `images/09_telnet_denegado.png` | Intento de Telnet rechazado |
| `images/08_ssh_local_ok.png` | SSH con `admin.p4` al switch |

## 6. Diferencias y limitaciones

| Tema | Catalyst 2960 | IOU/IOL L2 |
|---|---|---|
| Puerto auxiliar | No existe en la mayoría de modelos | No existe |
| `line aux 0` | Puede no estar disponible | No disponible |
| DHCP snooping | Soportado en LAN Base | Puede no estar soportado |
| Port-security | Soportado | Soporte parcial |
| `crypto key generate rsa` | Soportado | Soportado (con `ip domain name`) |
| Objeto `radius server NPS-P4` | 15.0(2)SE o superior | Soportado |

Si un comando no existe en la imagen, el IOS lo rechaza sin abortar el resto del bloque. Documentar la
diferencia en el README y continuar: el requisito central (AAA en consola/auxiliar + SSH) se mantiene.

---

**Anterior:** [04 · Router](04_Configuracion_Router.md) · **Siguiente:** [06 · Servidor AD/NPS](06_Servidor_AD_NPS.md)
