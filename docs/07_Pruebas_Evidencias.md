# 07 · Pruebas, resultados y evidencias

**Equipo de pruebas:** SRV1-P4 (cliente SSH), consolas de PNetLab (R1 y SW1)
**Herramientas:** consola serie de PNetLab, PowerShell, Visor de eventos, Bloc de notas

---

## 1. Matriz de pruebas

Las pruebas se ejecutan en orden. Antes de empezar: `show clock` en ambos equipos y verificar que
`show aaa servers` esté en `UP`.

| ID | Prueba | Procedimiento | Resultado esperado | Evidencia |
|---|---|---|---|---|
| **T01** | Consola R1 — nivel 0 | `login: usr.nivel0` / `CAMBIAR_CLAVE` → `show privilege` → `show version` | Prompt `>`; nivel 0; `show version` rechazado (`% Invalid input`) | `04_consola_nivel0.png` |
| **T02** | Consola R1 — nivel 5 | `login: usr.nivel5` → `show privilege` → `show version` → `show running-config` | Nivel 5; `show version` OK; `show running-config` rechazado | `05_consola_nivel5.png` |
| **T03** | Consola R1 — nivel 10 | `login: usr.nivel10` → `show privilege` → `show running-config` → `configure terminal` → `aaa new-model` | Nivel 10; lectura de config OK; comando `aaa` rechazado por privilegio | `06_consola_nivel10.png` |
| **T04** | Consola SW1 — nivel 10 | Igual que T03 en el switch | Nivel 10; `show vlan brief` y `show running-config` OK | `03_sw1_show_run_aaa.png` |
| **T05** | Credenciales inválidas | `login: usr.nivel5` con contraseña incorrecta | Acceso denegado; mensaje de autenticación fallida; evento **6273** en NPS | `14_nps_evento_6273.png` |
| **T06** | *Fallback* local | En SRV1: `Stop-Service IAS` → login en consola R1 con `admin.p4` | Acceso concedido con nivel 15 tras el timeout (~5 s) | `07_consola_admin_fallback.png` |
| **T07** | SSH local | Desde SRV1: `ssh admin.p4@10.7.84.129` y `@10.7.84.130` → `show privilege` | Acceso con nivel 15 por SSH | `08_ssh_local_ok.png` |
| **T08** | SSH con usuario RADIUS | `ssh usr.nivel10@10.7.84.129` | Rechazado: la VTY usa base local | `09_telnet_denegado.png` |
| **T09** | Telnet | Desde SRV1: `telnet 10.7.84.129` | Conexión rechazada (`transport input ssh`) | `09_telnet_denegado.png` |
| **T10** | ACL de gestión | Desde R1: `ssh -l admin.p4 10.7.84.130` (origen .129) | Rechazado por `access-class SSH-ADMIN` (solo .64/26) | `08_ssh_local_ok.png` |
| **T11** | Estado RADIUS | `show aaa servers` y `show radius statistics` | Servidor `UP`, sin timeouts, peticiones contabilizadas | `15_show_aaa_servers.png` |
| **T12** | Logs del dispositivo | `show logging` | Entradas de login exitoso/fallido y mensajes AAA | `16_show_logging.png` |
| **T13** | Evento de acceso concedido | En SRV1: filtrar evento **6272** por usuario y hora | Coincide con el login de T02/T03 | `13_nps_evento_6272.png` |
| **T14** | Contabilidad NPS | Abrir `C:\P4\NPS-Logs\*.log` | Registros `Start`/`Stop` y comandos de nivel 15 | `16_show_logging.png` |

### Pruebas complementarias (opcionales)

| Prueba | Procedimiento | Esperado |
|---|---|---|
| Aislamiento de VLAN 99 | Conectar un VPC en `Gi0/3` y `ping 10.7.84.130` | Sin respuesta (ACL `ACL-USUARIOS-IN`) |
| DHCP en VLAN 10 | En el VPC: `ip dhcp` | Recibe IP 10.7.84.20–.62, GW .1, DNS .66 |
| Port-security | Cambiar la MAC del VPC conectado a `Gi0/3` | Violación `Restrict`, contador incrementado |
| BPDU guard | Conectar un switch no autorizado a `Gi0/3` | Puerto en `err-disabled` |

## 2. Comandos de referencia rápida

```text
! En el equipo Cisco (consola o SSH)
show privilege
show aaa servers
show aaa method-lists
show radius statistics
show logging | include LOGIN|AAA|RADIUS
show running-config | section line
show ip ssh
show users

! En el servidor
Get-Service IAS
Get-NpsRadiusClient
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=6272} -MaxEvents 5
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=6273} -MaxEvents 5
Get-Content C:\P4\NPS-Logs\*.log -Tail 20
```

## 3. Registro de resultados

Completar tras ejecutar cada prueba (el evaluador debe poder reproducirla con la misma evidencia).

| ID | Fecha/hora | Resultado (OK / FALLA) | Observaciones |
|---|---|---|---|
| T01 | | | |
| T02 | | | |
| T03 | | | |
| T04 | | | |
| T05 | | | |
| T06 | | | |
| T07 | | | |
| T08 | | | |
| T09 | | | |
| T10 | | | |
| T11 | | | |
| T12 | | | |
| T13 | | | |
| T14 | | | |

## 4. Salidas esperadas (extracto)

```text
R1-P4>show privilege
Current privilege level is 0
R1-P4>show version
                ^
% Invalid input detected at '^' marker.
```

```text
R1-P4#show privilege
Current privilege level is 10
R1-P4#configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R1-P4(config)#aaa new-model
                     ^
% Invalid input detected at '^' marker.
```

```text
R1-P4#show aaa servers
RADIUS: id 1, priority 1, host 10.7.84.66, auth-port 1812, acct-port 1813
     State: current UP, duration 1264s, previous state: DOWN
     Requests: 23, Retransmits: 1, Timeouts: 0, Failures: 0
```

```text
R1-P4#show logging
Syslog logging: enabled (0 messages dropped, 2 messages rate-limited, 0 flushes)
    Console logging: level warnings, 0 messages logged
    Buffer logging: level informational, 148 messages logged
...
%SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: usr.nivel5] [Source: 10.7.84.66] [localport: 0] at 19:42:11 COT Wed Oct 28 2026
%SEC_LOGIN-4-LOGIN_FAILED: Login failed [user: usr.nivel5] [Source: 10.7.84.66] [localport: 0] [Reason: Login Authentication Failed] at 19:44:02 COT Wed Oct 28 2026
```

> Los identificadores exactos de syslog varían según la versión de IOS; lo relevante es que el evento
> aparezca con usuario, puerto y hora.

## 5. Cómo capturar las evidencias

1. **Capturar solo la ventana relevante** (no el escritorio completo).
2. Incluir la barra de título o el reloj cuando aporte contexto.
3. Guardar en PNG con el nombre exacto indicado en `images/`.
4. Reemplazar el marcador de posición generado por `scripts/tools/generar_imagenes.py`.
5. No incluir datos personales, correos ni rutas con el nombre de usuario de Windows.
6. Verificar que el texto se lea a 1080p (fuente de consola ≥ 14 pt).

Comando útil para dejar constancia de la hora en una captura de consola:

```text
show clock
```

---

**Anterior:** [06 · Servidor AD/NPS](06_Servidor_AD_NPS.md) · **Siguiente:** [08 · Conclusiones](08_Conclusiones.md)
