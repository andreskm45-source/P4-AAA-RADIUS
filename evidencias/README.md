# Evidencias de verificación

Esta carpeta guarda los informes generados por
[`scripts/03_Verificacion_AAA.ps1`](../scripts/03_Verificacion_AAA.ps1).

## Generar un informe

```powershell
cd scripts
.\03_Verificacion_AAA.ps1 -RouterIP 10.7.84.129 -SwitchIP 10.7.84.130
```

Salida: `evidencias/verificacion_AAA_AAAAMMDD_HHMMSS.txt` con:

1. Conectividad ICMP a R1, SW1 y SRV1.
2. Estado de SSH (TCP/22).
3. Servicio NPS y puerto UDP/1812.
4. Clientes RADIUS.
5. Grupos y miembros de AD.
6. Eventos 6272/6273/6274.
7. Últimas 10 líneas del log de contabilidad.
8. Fecha y hora del servidor.

## Publicar en el repositorio

- Subir el informe **sin** datos sensibles (el script no incluye contraseñas).
- Mantener un informe por ejecución; el más reciente debe corresponder al video.
- No subir archivos `*.log` con información de producción.

## Relación con el video

El informe permite al evaluador contrastar la hora y los eventos mostrados en el video con los registros
del servidor. Si el video se graba en otra fecha, volver a ejecutar el script y conservar ambos.
