# 10 · Checklist de entrega

## 1. Requisitos de la tarea

| # | Requisito | Estado | Dónde |
|---:|---|---|---|
| 1 | Repositorio en GitHub | ☐ | Crear y subir (ver §4) |
| 2 | Video al inicio del repositorio | ☐ | `README.md`, sección 1 |
| 3 | Documentación con imágenes | ☐ | `docs/` + `images/` |
| 4 | Documentación con diagramas | ☐ | `diagrams/` (3 SVG + Mermaid) |
| 5 | Propósito del laboratorio documentado | ☐ | `docs/01_Proposito_Alcance.md` |
| 6 | Todos los scripts en el repositorio | ☐ | `scripts/` |
| 7 | Running-configs en el repositorio | ☐ | `configs/*_running-config.txt` |
| 8 | Router: AAA, RADIUS cliente, usuario local, solo con/aux, logs, SSH | ☐ | `configs/R1-P4_base.cfg` |
| 9 | Switch: los mismos controles | ☐ | `configs/SW1-P4_base.cfg` |
| 10 | AD: grupos nivel 0, 5 y 10 | ☐ | `scripts/01_AD_Setup.ps1` |
| 11 | Servicio NPS con políticas y VSA | ☐ | `docs/06_Servidor_AD_NPS.md` |
| 12 | Archivo TXT con el enlace | ☐ | `RafaelAndresReyesDeLaCruz_20250784_P4.txt` |
| 13 | Video ≤ 10 min, fecha/hora, cara y voz | ☐ | `docs/09_Guion_Video.md` |
| 14 | Direccionamiento basado en matrícula | ☐ | `10.7.84.0/24` |
| 15 | Formato del nombre del archivo TXT | ☐ | `RafaelAndresReyesDeLaCruz_20250784_P4.txt` |

> Si la matrícula oficial se escribe con guion (`2025-0784`), el nombre del archivo puede requerir
> `RafaelAndresReyesDeLaCruz_2025-0784_P4.txt`. Confirmar con el docente y, si es necesario, duplicar el
> archivo con ambos nombres.

## 2. Antes de subir: reemplazar marcadores

| Marcador | Archivo | Acción |
|---|---|---|
| `REEMPLAZAR_ID` | `README.md` y TXT | Pegar el ID real de YouTube |
| `REEMPLAZAR_USUARIO` | TXT | Pegar el usuario real de GitHub |
| `images/*.png` (marcadores grises) | `images/` | Reemplazar por capturas reales manteniendo el nombre |
| `configs/*_running-config.txt` | `configs/` | Reemplazar por la salida real de `show running-config` |
| Fecha/hora de la tabla de resultados | `docs/07_Pruebas_Evidencias.md` | Completar tras las pruebas |

Comprobar que no queden marcadores:

```powershell
Select-String -Path .\README.md, .\*.txt -Pattern "REEMPLAZAR"
Get-ChildItem .\images -Filter *.png | Where-Object Length -lt 60000
```

## 3. Verificación del repositorio

```powershell
# Estructura
Get-ChildItem -Recurse -File | Select-Object FullName

# Enlaces relativos del README (deben existir)
Select-String -Path .\README.md, .\docs\*.md -Pattern "\]\((\.\./)?(docs|configs|scripts|diagrams|images)/" |
  ForEach-Object { $_.Matches.Value }

# Git
git status
git log --oneline -n 5
```

Checklist de contenido:

- [ ] `README.md` abre con el video (iframe/miniatura enlazada).
- [ ] Todos los enlaces del README resuelven (sin 404).
- [ ] `images/` contiene las 20 capturas reales (no los marcadores).
- [ ] `diagrams/*.svg` se visualizan en GitHub.
- [ ] `configs/` tiene las configuraciones base y los running-configs reales.
- [ ] `scripts/` tiene los tres scripts y se ejecutan sin errores de sintaxis.
- [ ] `docs/` tiene los 12 documentos.
- [ ] El TXT tiene nombre y contenido correctos.
- [ ] No hay contraseñas reales de producción ni datos personales.

## 4. Publicación en GitHub

```powershell
cd P4-AAA-RADIUS-NPS
git init
git add .
git commit -m "P4: AAA con RADIUS/NPS, documentacion, configs y scripts"
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

Si el repositorio ya existe y tiene contenido:

```powershell
git remote add origin https://github.com/<usuario>/<repositorio>.git
git fetch origin
git pull --rebase origin main
git push -u origin main
```

## 5. Video

- [ ] Duración ≤ 10:00.
- [ ] Fecha y hora visibles al inicio.
- [ ] Rostro visible y voz propia.
- [ ] Se muestran las pruebas T01–T14 (o al menos las críticas).
- [ ] Enlace abre en incógnito.
- [ ] Enlace pegado en README y TXT.

## 6. Integridad académica

- [ ] La topología y las capturas corresponden al laboratorio propio.
- [ ] No se reutilizaron videos, capturas ni configuraciones de otro estudiante.
- [ ] El video no está editado para ocultar fallos.
- [ ] Se citan las fuentes en [12 · Referencias](12_Referencias.md).

## 7. Entrega

1. Subir el TXT a la plataforma con el enlace del repositorio y del video.
2. Verificar permisos: repositorio **público** (o con acceso al docente) y video accesible.
3. Guardar una copia local del repositorio (`git clone`) como respaldo.

---

**Anterior:** [09 · Guion del video](09_Guion_Video.md) · **Siguiente:** [11 · Troubleshooting](11_Troubleshooting.md)
