# 08 · Conclusiones y trabajo futuro

## 1. Resultados alcanzados

El laboratorio demuestra un modelo AAA completo y verificable:

| Capacidad | Resultado |
|---|---|
| Autenticación centralizada | Router y switch validan consola/auxiliar contra NPS (AD) |
| Autorización por rol | Los grupos `GRP_NIVEL0/5/10` producen niveles IOS 0/5/10 vía `shell:priv-lvl` |
| Mínimo privilegio | El nivel 5 no lee la configuración; el 10 no modifica AAA |
| Continuidad | `admin.p4` local (nivel 15) funciona con NPS caído |
| Administración remota segura | Solo SSH, solo desde 10.7.84.64/26, Telnet deshabilitado |
| Auditoría | Accounting en el equipo + eventos 6272/6273/6274 + log de contabilidad |
| Segmentación | VLAN 10/20/99/999, ACL de gestión, port-security, BPDU guard, DHCP snooping |

## 2. Aprendizajes clave

1. **La autorización no termina en el login.** El atributo `shell:priv-lvl` es el puente entre el
   directorio y el IOS; sin él, todos los usuarios quedan en el nivel por defecto.
2. **El *fallback* debe probarse.** Un método `group radius local` solo usa la base local cuando el
   servidor **no responde**; un rechazo explícito no cae al siguiente método. Confundir ambos casos es
   la causa más común de bloqueos.
3. **La VTY es un plano distinto.** Aplicar AAA solo a consola/auxiliar exige revisar explícitamente
   que las VTY usen `login local`, o el requisito se cumple a medias.
4. **El origen RADIUS importa.** Si `ip radius source-interface` no coincide con el cliente declarado
   en NPS, el servidor descarta la petición (evento 6274) aunque las credenciales sean válidas.
5. **Sin hora sincronizada no hay evidencia.** Los eventos de NPS y los logs del equipo deben poder
   correlacionarse al segundo.

## 3. Limitaciones

- Un único servidor NPS y un único enlace: no hay alta disponibilidad.
- El `enable secret` compartido permite, en teoría, que un usuario de nivel 10 escale si lo conoce.
  Se mitiga con gestión del secreto y auditoría, no con la configuración AAA.
- El acceso físico a la consola sigue siendo un vector: quien tenga la consola puede intentar el
  *fallback* local. La protección es física y organizativa.
- RADIUS viaja sin cifrado de extremo a extremo dentro de la VLAN 99; el secreto compartido solo protege
  el atributo de contraseña.
- El laboratorio no implementa 802.1X, por lo que un dispositivo conectado a un puerto de acceso no se
  autentica a nivel de red.

## 4. Trabajo futuro

| Mejora | Beneficio |
|---|---|
| **802.1X + MAB** en puertos de acceso | Autenticación de dispositivos antes de asignar VLAN |
| **TACACS+** para autorización por comando | Control granular y auditoría de cada comando |
| **RadSec (RADIUS/TLS)** o IPsec | Confidencialidad del tráfico AAA |
| **Dos servidores NPS** con el mismo secreto | Continuidad ante caída del servidor |
| **MFA** para consola (servidor de acceso) | Protección contra robo de credenciales |
| **SIEM** (Wazuh, Splunk, ELK) | Correlación de eventos y alertas |
| **Automatización** (Ansible/Nornir) | Despliegue consistente de la configuración |
| **Rotación de secretos** (Vault) | Elimina secretos estáticos en el repositorio |

## 5. Conclusión

La topología cumple el objetivo de la práctica: **la identidad deja de ser local y compartida, y pasa a
ser centralizada, individual y auditada**, con un mecanismo de emergencia que evita perder la
administración. El diseño es deliberadamente simple (tres dispositivos, cuatro VLAN) para que cada
control sea observable y reproducible, y lo suficientemente realista como para extenderse a 802.1X,
TACACS+ y alta disponibilidad en un entorno productivo.

---

**Anterior:** [07 · Pruebas](07_Pruebas_Evidencias.md) · **Siguiente:** [09 · Guion del video](09_Guion_Video.md)
