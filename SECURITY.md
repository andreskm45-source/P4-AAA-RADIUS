# Política de seguridad del repositorio

Este repositorio documenta un **laboratorio académico**. Las credenciales publicadas
(`admin.p4`, `usr.nivel*`, `enable secret` y el secreto RADIUS) son de laboratorio y no protegen
información real.

## Uso responsable

- No reutilizar estas contraseñas ni este secreto en equipos productivos.
- Rotar el secreto RADIUS y el `enable secret` antes de cualquier despliegue real.
- El repositorio no contiene claves privadas, certificados ni datos personales de terceros.

## Reportar un problema

Si encuentras un error de configuración o una exposición involuntaria, abre un *issue* describiendo el
archivo y la línea, sin incluir credenciales reales.

## Alcance

Este documento no constituye un análisis de seguridad de un entorno productivo. Las decisiones y
limitaciones del diseño están descritas en [`docs/08_Conclusiones.md`](docs/08_Conclusiones.md).
