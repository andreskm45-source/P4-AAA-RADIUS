# Evidencias e imágenes

Las imágenes de esta carpeta son **capturas reales del laboratorio**. Los archivos generados por
`scripts/tools/generar_imagenes.py` son marcadores grises que deben reemplazarse conservando el nombre.

## Lista de capturas

| Archivo | Qué debe mostrar | Documento |
|---|---|---|
| `01_topologia_pnetlab.png` | Topología completa en PNetLab con los equipos encendidos | [03](../docs/03_Direccionamiento_IP.md) |
| `02_r1_show_run_aaa.png` | R1: `show running-config \| section aaa` y `section line` | [04](../docs/04_Configuracion_Router.md) |
| `03_sw1_show_run_aaa.png` | SW1: misma salida | [05](../docs/05_Configuracion_Switch.md) |
| `04_consola_nivel0.png` | Login `usr.nivel0` y `show privilege` = 0 | [07](../docs/07_Pruebas_Evidencias.md) |
| `05_consola_nivel5.png` | Login `usr.nivel5`, `show privilege` = 5, `show version` | [07](../docs/07_Pruebas_Evidencias.md) |
| `06_consola_nivel10.png` | Login `usr.nivel10`, `show privilege` = 10, `show running-config` | [07](../docs/07_Pruebas_Evidencias.md) |
| `07_consola_admin_fallback.png` | NPS detenido y login con `admin.p4` en nivel 15 | [07](../docs/07_Pruebas_Evidencias.md) |
| `08_ssh_local_ok.png` | SSH con `admin.p4` desde SRV1 y `show privilege` | [07](../docs/07_Pruebas_Evidencias.md) |
| `09_telnet_denegado.png` | Telnet rechazado / SSH con usuario AD rechazado | [07](../docs/07_Pruebas_Evidencias.md) |
| `10_nps_clientes.png` | Clientes RADIUS `P4-R1` y `P4-SW1` | [06](../docs/06_Servidor_AD_NPS.md) |
| `11_nps_politicas.png` | Las tres políticas de red | [06](../docs/06_Servidor_AD_NPS.md) |
| `12_nps_vsa_privlvl.png` | VSA `Cisco-AV-Pair = shell:priv-lvl=10` | [06](../docs/06_Servidor_AD_NPS.md) |
| `13_nps_evento_6272.png` | Evento 6272 con usuario y hora | [06](../docs/06_Servidor_AD_NPS.md) |
| `14_nps_evento_6273.png` | Evento 6273 de acceso denegado | [06](../docs/06_Servidor_AD_NPS.md) |
| `15_show_aaa_servers.png` | `show aaa servers` en `UP` | [04](../docs/04_Configuracion_Router.md) |
| `16_show_logging.png` | `show logging` con eventos de login y AAA | [07](../docs/07_Pruebas_Evidencias.md) |
| `17_ad_grupos.png` | Grupos `GRP_NIVEL0/5/10` en AD | [06](../docs/06_Servidor_AD_NPS.md) |
| `18_ad_usuarios.png` | Usuarios y pertenencia a grupos | [06](../docs/06_Servidor_AD_NPS.md) |
| `19_fecha_hora_video.png` | Fecha/hora visible durante el video | [09](../docs/09_Guion_Video.md) |
| `20_ping_validacion.png` | Ping SRV1 → R1 / SW1 por VLAN 99 | [05](../docs/05_Configuracion_Switch.md) |

`portada_video.png` es la miniatura del video (generada, no requiere reemplazo).

