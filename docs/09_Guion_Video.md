# 09 · Guion del video demostrativo (máximo 10 minutos)

**Objetivo:** demostrar que la topología cumple el objetivo de seguridad, sin editar ni ocultar pasos.
**Duración objetivo:** 9:30 min · **Formato:** 1080p, 16:9 · **Audio:** voz en vivo.

---

## 1. Preparación previa (30 min antes)

| Elemento | Acción |
|---|---|
| Fecha y hora | Verificar reloj de Windows y de los equipos (`show clock`) |
| Pestañas abiertas | PNetLab (topología), consola R1, consola SW1, NPS, AD, README del repo |
| Ventanas | Fuente de consola ≥ 14 pt, zoom del navegador al 110 % |
| Grabación | OBS con escena «Pantalla + webcam» (cámara en un círculo, arriba a la derecha) |
| Micrófono | Prueba de 10 s; sin eco ni teclado |
| Notificaciones | Modo «No molestar»; cerrar correo y mensajería |
| Credenciales | A mano en un papel, no en pantalla antes de tiempo |
| NPS | Servicio `IAS` iniciado; `show aaa servers` en `UP` |

> Mostrar la cara y la voz es un requisito: no se permite narración sintética ni video sin cámara.

## 2. Estructura y tiempos

### 0:00 – 0:25 · Presentación (cámara encendida)

- «Buenos días/tardes. Soy **Rafael Andrés Reyes De La Cruz**, matrícula **2025-0784**. Esta es la
  práctica **P4** de Seguridad de Redes: AAA con RADIUS, Active Directory y NPS.»
- Mostrar en pantalla la **fecha y hora** del sistema (reloj de Windows) y el `show clock` de R1.
- Aclarar: «El video muestra únicamente el funcionamiento del laboratorio; no se editan ni se ocultan
  pasos.»

### 0:25 – 1:15 · Topología y propósito

- Mostrar el diagrama del README y la topología en PNetLab.
- Explicar en 30 segundos:
  - R1: gateway de VLAN 10/20/99.
  - SW1: acceso, SVI de gestión `.130`.
  - SRV1: AD DS + NPS en `.66`.
  - Objetivo: usuarios de AD con niveles 0/5/10 por consola/auxiliar; SSH local restringido.

### 1:15 – 2:30 · Active Directory y NPS

1. Mostrar los grupos `GRP_NIVEL0`, `GRP_NIVEL5`, `GRP_NIVEL10` y sus miembros.
2. En NPS → **Clientes RADIUS**: `P4-R1` (.129) y `P4-SW1` (.130).
3. En NPS → **Directivas de red**: las tres políticas y el atributo
   `Cisco-AV-Pair = shell:priv-lvl=N`.
4. Mostrar que el método de autenticación permite **PAP** (necesario para el login de IOS).

### 2:30 – 3:40 · Router R1

```text
show aaa servers
show running-config | section aaa
show running-config | section line
show ip ssh
```

Narrar:

- «El router es cliente del NPS en 10.7.84.66, con origen 10.7.84.129.»
- «La lista `CON-RADIUS` solo está aplicada en `line con 0` y `line aux 0`.»
- «La VTY usa `login local` y solo acepta SSH: los usuarios de AD no entran por SSH.»

### 3:40 – 4:30 · Switch SW1

```text
show aaa servers
show vlan brief
show interfaces trunk
show port-security
```

Narrar: trunk 802.1Q con nativa 999, port-security en el puerto del servidor, puertos no usados apagados.

### 4:30 – 6:30 · Consola con los tres niveles (prueba central)

En la consola de R1, cerrar sesión y repetir:

**Nivel 0**

```text
login: usr.nivel0
password: CAMBIAR_CLAVE
show privilege          → nivel 0
show version            → comando rechazado
```

**Nivel 5**

```text
login: usr.nivel5
password: CAMBIAR_CLAVE
show privilege          → nivel 5
show version            → funciona
show running-config     → rechazado
```

**Nivel 10**

```text
login: usr.nivel10
password: CAMBIAR_CLAVE
show privilege          → nivel 10
show running-config     → funciona
configure terminal
aaa new-model           → rechazado (nivel 15)
exit
```

Cerrar con: «El mismo usuario, en el mismo equipo, obtiene permisos distintos según su grupo de AD.»

En SW1, repetir el login con `usr.nivel10` y mostrar `show privilege` y `show vlan brief`.

### 6:30 – 7:20 · Intento fallido y registro

1. Intentar login con `usr.nivel5` y contraseña incorrecta → acceso denegado.
2. En el router: `show logging | include LOGIN`.
3. En el servidor: Visor de eventos → **Seguridad** → filtrar **6273**.
4. Mostrar que el evento incluye usuario, hora y NAS.

### 7:20 – 8:10 · SSH y superficie de ataque

Desde SRV1 (PowerShell):

```powershell
ssh admin.p4@10.7.84.129      # funciona, nivel 15
ssh usr.nivel10@10.7.84.129   # rechazado: VTY con login local
telnet 10.7.84.129            # rechazado: solo SSH
```

Desde R1 (origen .129, fuera de la ACL):

```text
ssh -l admin.p4 10.7.84.130   # rechazado por access-class
```

### 8:10 – 9:00 · Continuidad: NPS caído

1. En SRV1: `Stop-Service IAS`.
2. En la consola de R1: login con `admin.p4` → entra con **nivel 15** tras el timeout.
3. Explicar: «El acceso local es solo de emergencia y funciona porque NPS no responde.»
4. En SRV1: `Start-Service IAS` y verificar `show aaa servers` en `UP`.

### 9:00 – 9:30 · Auditoría y cierre

1. `show logging` (eventos de AAA).
2. `C:\P4\NPS-Logs\*.log`: registros `Start`/`Stop`.
3. Cierre: «La topología cumple: autenticación centralizada, autorización por niveles, auditoría y
   acceso de emergencia controlado. Gracias.»

## 3. Comandos de respaldo (si algo falla)

| Situación | Acción |
|---|---|
| RADIUS no responde | `show aaa servers`; revisar IP de origen y secreto |
| Consola bloqueada | Segunda sesión + `reload in 5`; el usuario local entra con NPS caído |
| Evento 6273 inesperado | Revisar grupo del usuario y política de NPS |
| Usuario sin privilegio | Verificar VSA `shell:priv-lvl` y `show aaa method-lists` |
| SSH no arranca | `crypto key generate rsa modulus 2048`; verificar `ip domain name` |

## 4. Publicación

1. Subir a YouTube: **público** o **no listado** (el enlace debe abrir sin cuenta).
2. Título: `P4 Seguridad de Redes - AAA RADIUS/NPS - Rafael Reyes 2025-0784`.
3. Descripción: nombre, matrícula, propósito, enlace al repositorio y capítulos con marcas de tiempo.
4. Copiar el enlace (`https://youtu.be/...`) en:
   - el bloque de video del `README.md` (reemplazar `REEMPLAZAR_ID`);
   - `RafaelAndresReyesDeLaCruz_20250784_P4.txt`.
5. Verificar que la miniatura y el video se vean en una ventana de incógnito.

## 5. Errores que descalifican

- No mostrar la cara o no usar la propia voz.
- Ocultar la fecha/hora o editar la secuencia de comandos.
- Presentar capturas de otro laboratorio o configuraciones no aplicadas.
- Superar los 10 minutos o incluir contenido ajeno a la demostración.

---

**Anterior:** [08 · Conclusiones](08_Conclusiones.md) · **Siguiente:** [10 · Checklist](10_Checklist_Entrega.md)
