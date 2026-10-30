# 01 · Propósito, alcance y objetivos

**Laboratorio P4 — Seguridad de Redes**
**Autor:** Rafael Andrés Reyes De La Cruz · **Matrícula:** 2025-0784
**Red:** 10.7.84.0/24 · **Plataforma:** PNetLab

---

## 1. Contexto y problema

En muchos laboratorios y redes pequeñas los equipos Cisco se administran con un único usuario local
compartido. Esa práctica tiene tres consecuencias:

1. **Sin trazabilidad individual:** todos los administradores usan la misma cuenta; un cambio no puede
   atribuirse a una persona.
2. **Sin separación de funciones:** quien solo necesita consultar el estado del equipo recibe privilegio
   total, y un error o un uso indebido puede tumbar la red.
3. **Credenciales dispersas:** cada equipo guarda su propia base de usuarios, lo que multiplica los
   puntos de exposición y complica la rotación.

La práctica resuelve el problema con **AAA centralizado**: un servidor Windows (AD DS + NPS) actúa como
servidor **RADIUS**, y el router y el switch lo consultan para autenticar y autorizar el acceso por
**consola y puerto auxiliar**.

## 2. Objetivo general

Implementar autenticación, autorización y auditoría centralizadas con RADIUS/NPS en la infraestructura
del laboratorio, aplicando **tres niveles de privilegio** derivados de grupos de Active Directory y
manteniendo un acceso local de emergencia controlado.

## 3. Objetivos específicos

| # | Objetivo | Criterio de cumplimiento |
|---:|---|---|
| 1 | Configurar RADIUS como cliente en router y switch | `show aaa servers` muestra el servidor `10.7.84.66` en estado UP |
| 2 | Crear un usuario local de respaldo | `admin.p4` privilegio 15 funciona con NPS detenido |
| 3 | Aplicar AAA **solo** a consola y auxiliar | `show running-config \| section line` muestra AAA en `con 0` y `aux 0`, y `login local` en VTY |
| 4 | Traducir grupos AD en privilegios IOS | `usr.nivel0/5/10` obtienen nivel 0, 5 y 10 (`show privilege`) |
| 5 | Habilitar SSH y deshabilitar Telnet | `transport input ssh`; Telnet rechazado |
| 6 | Registrar autenticación, autorización y RADIUS | `show logging` + Eventos 6272/6273/6274 + log de contabilidad |
| 7 | Segmentar y endurecer la red | VLAN 10/20/99/999, ACL de gestión, port-security, BPDU guard, DHCP snooping |
| 8 | Documentar y evidenciar | Repositorio con diagramas, configuraciones, scripts, capturas y video |

## 4. Alcance

**Incluido**

- 1 router Cisco IOS (R1-P4) y 1 switch Cisco (SW1-P4).
- 1 servidor Windows Server con AD DS, DNS y NPS.
- VLAN de usuarios (10), de servidores (20), de gestión/AAA (99) y nativa de parking (999).
- AAA RADIUS para consola y auxiliar; SSH con autenticación local; auditoría en ambos equipos.
- Tres grupos de AD (`GRP_NIVEL0`, `GRP_NIVEL5`, `GRP_NIVEL10`) y tres usuarios de prueba.
- Endurecimiento L2 del switch y ACLs de protección de la VLAN de gestión.

**Fuera de alcance (mejoras posibles)**

- 802.1X / NAC para puertos de acceso y MAB.
- TACACS+ para autorización por comando (se documenta como opción, no se habilita para evitar bloqueos).
- RADIUS sobre TLS (RadSec) o IPsec.
- Alta disponibilidad de NPS (NPS proxy / dos servidores).
- Integración con SIEM, MFA o gestión de identidades externa.

## 5. Supuestos

- El servidor es **miembro del dominio** y, en este laboratorio, también controlador de dominio.
- Router y switch alcanzan `10.7.84.66` por la VLAN 99 a través del trunk.
- El reloj de los tres equipos está sincronizado (NTP o `clock set`), requisito para correlacionar logs.
- El estudiante tiene privilegios de administrador local en el servidor y acceso a la consola de los
  equipos en PNetLab.

## 6. Riesgos identificados y mitigaciones

| Riesgo | Impacto | Mitigación implementada |
|---|---|---|
| NPS no disponible | Pérdida de acceso por consola | *Fallback* local `admin.p4` (nivel 15) y sesión de consola abierta durante cambios |
| Secreto RADIUS débil o compartido | Suplantación del NAS | Secreto de laboratorio y nota de rotación; ACL de gestión |
| Usuario de nivel 10 conoce `enable secret` | Escalada a 15 | El secreto solo lo conoce el administrador; se documenta como riesgo residual |
| VLAN de gestión accesible desde usuarios | Compromiso de AAA | ACL `ACL-USUARIOS-IN` + `access-class SSH-ADMIN` en VTY |
| Puerto de acceso con dispositivo no autorizado | Acceso físico | Port-security *sticky*, BPDU guard y puertos no usados apagados |
| Reloj desincronizado | Evidencia no correlacionable | NTP hacia el DC y `service timestamps ... localtime` |
| Bloqueo por cambio remoto | Pérdida total de administración | Cambios por consola y `reload in 5` como red de seguridad |

## 7. Criterios de éxito

1. Los tres usuarios de AD inician sesión en la consola del router y del switch y reciben exactamente el
   nivel 0, 5 o 10.
2. Un usuario RADIUS **no** puede abrir SSH; el usuario local **sí**.
3. Con NPS detenido, `admin.p4` sigue entrando por consola con nivel 15.
4. Cada intento (exitoso o fallido) deja rastro en el dispositivo y en el servidor.
5. La VLAN de gestión no responde a intentos desde la VLAN de usuarios.

## 8. Referencias normativas

- **NIST SP 800-53 Rev. 5** — controles IA-2 (identificación y autenticación), IA-5 (gestión de
  autenticadores), AC-6 (mínimo privilegio), AU-2/AU-3 (registro y revisión).
- **ISO/IEC 27001:2022** — A.5.15 (control de acceso), A.5.17 (autenticación), A.8.15 (registro),
  A.8.16 (supervisión).
- **RFC 2865 / RFC 2866** — RADIUS de autenticación y contabilidad.
- **Cisco IOS AAA** — niveles de privilegio 0–15 y atributo `shell:priv-lvl`.

---

**Siguiente:** [02 · Diseño de la topología](02_Diseno_Topologia.md) · **Volver al** [README](../README.md)
