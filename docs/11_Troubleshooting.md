# 11 · Troubleshooting (problemas frecuentes)

## 1. Consola: el usuario de AD no entra

| Síntoma | Causa probable | Solución |
|---|---|---|
| `% Authentication failed` inmediato | Secreto RADIUS distinto | Comparar `key` del IOS con el cliente en NPS (distingue mayúsculas) |
| Falla solo en un equipo | IP de origen distinta a la declarada | `show ip radius source-interface`; debe ser `.129` o `.130` |
| NPS no registra nada | El NAS no llega al servidor | `ping 10.7.84.66` desde el equipo; revisar gateway del switch |
| Evento **6274** | Cliente desconocido o secreto incorrecto | Revisar cliente RADIUS y firewall UDP 1812 |
| Evento **6273** | Política o grupo incorrecto | Verificar grupo del usuario y condición de la política |
| Falla solo con AD | Método de autenticación no permite PAP | Agregar «PAP sin cifrar (PAP, SPAP)» a la política |
| Falla un usuario nuevo | Propiedad de marcado en «Denegar acceso» | `msNPAllowDialin = TRUE` o marcar «Omitir propiedades de marcado» en la CRP |

> Un **rechazo** de NPS no activa el *fallback* local: solo lo hace la **falta de respuesta**. Si el
> usuario de AD está mal escrito, el login falla aunque `admin.p4` exista.

## 2. `show aaa servers` en `DEAD`

```text
R1-P4# show aaa servers
RADIUS: id 1, priority 1, host 10.7.84.66, auth-port 1812, acct-port 1813
     State: current DEAD, duration 320s, previous state: DEAD
```

1. Verificar alcance: `ping 10.7.84.66 source GigabitEthernet0/0.99`.
2. Verificar servicio en el servidor: `Get-Service IAS`.
3. Verificar reglas de firewall (UDP 1812/1813) y que el perfil de red sea el correcto.
4. Confirmar que el cliente RADIUS usa la IP de origen correcta.
5. Probar el secreto: en NPS, editar el cliente y reescribir el secreto; en IOS, reescribir la `key`.
6. `clear radius statistics` y reintentar.

## 3. El usuario entra pero con nivel incorrecto

| Síntoma | Causa | Solución |
|---|---|---|
| Nivel 1 o 15 en todos | VSA ausente o mal escrito | Debe ser `Cisco-AV-Pair` con valor `shell:priv-lvl=10` |
| Nivel 15 siempre | `aaa authorization exec` no está aplicado a la línea | Revisar `show run \| section line` |
| Nivel 0 en todos | `shell:priv-lvl=0` en la política equivocada | Revisar orden y condición de políticas |
| Cambio sin efecto | Servicio NPS con caché | `Restart-Service IAS` y volver a iniciar sesión |

Verificación en el equipo:

```text
show aaa method-lists
show running-config | include authorization
show privilege
```

## 4. SSH no funciona

| Mensaje / síntoma | Solución |
|---|---|
| `% Please create RSA keys` | `crypto key generate rsa modulus 2048` |
| `% SSH is not enabled` | `ip ssh version 2` + `hostname` + `ip domain name` |
| `Connection refused` | `transport input ssh` en `line vty 0 4` |
| `Connection timed out` | ACL `SSH-ADMIN`; agregar la subred del cliente |
| `Permission denied` con usuario AD | Correcto: la VTY usa `login local`; usar `admin.p4` |
| Telnet sigue funcionando | `transport input ssh` (no `all`) y `no telnet` en el cliente |

## 5. `login on-failure log` rechazado

```text
R1-P4(config)# login on-failure log
% Invalid input detected at '^' marker.
```

La versión de IOS no soporta el comando. Eliminarlo: la auditoría de autenticación sigue disponible en
NPS (6272/6273) y en el *accounting* de AAA. Documentar la limitación.

## 6. Puerto en `err-disabled`

```text
SW1-P4# show interfaces status
Gi0/3  err-disabled  10  ...
```

Causas: BPDU guard, port-security o storm-control.

```text
SW1-P4(config)# interface Gi0/3
SW1-P4(config-if)# shutdown
SW1-P4(config-if)# no shutdown
SW1-P4# clear port-security sticky interface Gi0/3
SW1-P4# show interfaces status err-disabled
```

Si el servidor cambió de MAC (clonación de VM), liberar la MAC *sticky* antes de reconectar.

## 7. DHCP no entrega dirección

1. El trunk debe ser `ip dhcp snooping trust`.
2. `no ip dhcp snooping information option` (el router no reenvía la opción 82).
3. Verificar el pool: `show ip dhcp pool` y `show ip dhcp binding`.
4. El puerto del cliente debe estar en VLAN 10 y no apagado.

## 8. NPS no arranca o no registra en AD

- `Get-Service IAS` → si está detenido, revisar el Visor de eventos (origen `IAS`).
- El servidor debe ser miembro del dominio y tener conectividad con el DC.
- `Register-NPSInAD` requiere privilegios de administrador de dominio.
- Si el servidor no es DC, verificar que el grupo `RAS and IAS Servers` tenga el equipo.

## 9. Reloj desincronizado

```text
R1-P4# show ntp status
Clock is unsynchronized, stratum 16, no reference clock
```

- Verificar `ntp server 10.7.84.66` y UDP 123 en el firewall del servidor.
- Si no hay NTP, ajustar manualmente: `clock set HH:MM:SS DD MON YYYY` (modo exec privilegiado).
- Sin hora correcta, los eventos no se pueden correlacionar con el video.

## 10. Diferencias de plataforma

| Caso | Acción |
|---|---|
| `line aux 0` no existe (IOU/2960) | Omitir el bloque y documentarlo |
| Interfaces `Et0/x` en lugar de `Gi0/x` | Usar `configs/variantes/SW1-P4_IOU_L2.cfg` |
| Sin soporte de DHCP snooping | Omitir esa sección; el resto del laboratorio sigue vigente |
| `aaa authorization console` rechazado | Omitirlo; la autorización de línea sigue funcionando en la mayoría de versiones |
| `radius server NPS-P4` rechazado con `% Invalid input` | Usar [`configs/legacy/radius-legacy.cfg`](../configs/legacy/radius-legacy.cfg) (sintaxis `radius-server host`) |
| Sin soporte de `login on-success log` | Mantener `login on-failure log` y los `logging` de AAA |

### 10.1 Sintaxis legacy de RADIUS

Si el equipo no acepta el bloque `radius server NPS-P4 / address ipv4 ...`, aplicar el archivo
[`configs/legacy/radius-legacy.cfg`](../configs/legacy/radius-legacy.cfg). Contiene exactamente el
mismo servidor, la misma clave y el mismo grupo `RAD-P4`, pero con la sintaxis antigua:

```text
radius-server key CAMBIAR_CLAVE
radius-server host 10.7.84.66 auth-port 1812 acct-port 1813 key CAMBIAR_CLAVE
aaa group server radius RAD-P4
 server 10.7.84.66 auth-port 1812 acct-port 1813
```

Después de aplicarlo, comprobar con `show aaa servers` que el servidor aparece como `UP` y que la IP
de origen es la de `Vlan99` (o `Gi0/0.99` en el router). El resto de la configuración del switch no
se modifica.

## 11. Recuperación de un bloqueo

1. Mantener una segunda sesión de consola abierta antes de tocar AAA.
2. Programar `reload in 5` y cancelar con `reload cancel` si todo funciona.
3. Si se perdió el acceso, reiniciar el equipo: el usuario local `admin.p4` está en la configuración
   guardada y no depende de NPS.
4. Como último recurso, recuperación de contraseña por procedimiento de la plataforma (requiere acceso
   físico/consola y reinicio).

## 12. Diagnóstico avanzado

```text
debug aaa authentication
debug aaa authorization
debug radius
terminal monitor
```

> Usar `debug` solo en ventanas cortas y con `undebug all` al terminar. En el video no es necesario y
> puede saturar la consola.

---

**Anterior:** [10 · Checklist](10_Checklist_Entrega.md) · **Siguiente:** [12 · Referencias](12_Referencias.md)
