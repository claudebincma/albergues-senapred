# Albergues Habilitados — Sistema Frontal Julio 2026

Dashboard público de albergues habilitados en respuesta a emergencias climáticas en Chile, compilado desde comunicados de SENAPRED, delegaciones presidenciales regionales y municipios.

**Sitio en vivo:** (se completa después de deploy a Netlify)

## Estructura

```
albergues-senapred/
├── index.html              # Dashboard (carga datos de data.json)
├── data.json               # Datos de albergues + metadata
├── scripts/
│   └── update_albergues.py # Script de verificación de cambios
├── .github/workflows/
│   └── check.yml           # GitHub Actions: verifica cambios cada 24h
└── README.md
```

## Cómo usar

### Deploy inicial (Netlify)

1. En tu máquina, asegúrate de estar en la carpeta del repo:
   ```bash
   cd ~/Documents/Claude/albergues-senapred
   ```

2. Inicializa git y haz el primer commit:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: albergues dashboard with data"
   ```

3. Crea un repo en GitHub (privado o público) y haz push:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/albergues-senapred.git
   git branch -M main
   git push -u origin main
   ```

4. En [app.netlify.com](https://app.netlify.com):
   - Click "Import from Git"
   - Selecciona el repo
   - Netlify auto-detecta `index.html` como entry point
   - Listo — obtuviste un link público tipo `xxx.netlify.app`

### Actualizar albergues

#### Opción 1: Disparo manual
Cuando hay nuevos comunicados de SENAPRED/municipios:

1. Edita `data.json` con los nuevos albergues
2. Ejecuta el script (actualiza timestamp):
   ```bash
   python scripts/update_albergues.py
   ```
3. Haz commit y push:
   ```bash
   git add data.json
   git commit -m "Agregar albergues: [región, municipio]"
   git push
   ```
4. Netlify se redeploy automáticamente

#### Opción 2: Verificación automática (cada 24h)
El workflow `.github/workflows/check.yml` ejecuta cada 24 horas y:
- Verifica si hay cambios en fuentes públicas (cuando se implemente el scraping)
- Comenta en un issue si detecta cambios
- Tú haces el update manual de `data.json` y push

Para probar el workflow manualmente:
```bash
# En GitHub, ve a Actions → "Verificar cambios en albergues" → "Run workflow"
```

## Estructura de data.json

```json
{
  "last_updated": "2026-07-16T12:00:00Z",
  "last_updated_es": "16 jul 2026, mediodía",
  "source": "Comunicados de SENAPRED, delegaciones presidenciales y municipios",
  "albergues": [
    {
      "name": "...",
      "region": "Coquimbo",
      "comuna": "Ovalle",
      "addr": "...",
      "details": "...",
      "contact": "...",
      "lat": -30.6031,
      "lon": -71.2030,
      "precision": "aprox" | "exacta"
    }
  ]
}
```

- **precision**: `"exacta"` = dirección/localidad puntual encontrada; `"aprox"` = centroide de comuna (sin dirección específica publicada)

## Scripts

### `update_albergues.py`

Uso:
```bash
python scripts/update_albergues.py
```

Hoy: verifica sin cambios y actualiza timestamp.

Futuro: implementar scraping de:
- `senapred.cl/albergues-emergencia`
- `@Senapred` en X (Twitter)
- Comunicados de prensa regionales

## GitHub Actions

**Workflow**: `.github/workflows/check.yml`
- Ejecuta cada 24 horas (cron `0 12 * * *` = 12:00 UTC / 08:00 CLT)
- Ejecuta `python scripts/update_albergues.py`
- Si detecta cambios, comenta en un issue de seguimiento
- Disparo manual: GitHub Actions UI → "Run workflow"

**Nota**: No hace auto-commit. El cambio real en `data.json` lo haces tú, y Netlify se redeploy en cada push.

## Precisión de coordenadas

- **Exacta**: Dirección o localidad geocodificada desde Nominatim/OpenStreetMap
- **Aproximada**: No hay dirección pública específica; se usó centroide de la comuna

Antes de enviar a alguien a un albergue, confirma la dirección exacta con el municipio.

## Fuentes

- SENAPRED: https://senapred.cl/
- Delegaciones presidenciales regionales
- Municipios (comunicados de prensa)
- Geocodificación: OpenStreetMap Nominatim

## Contacto y licencia

Proyecto de [4DRR.com](https://4drr.com) — asesoría en DRR y continuidad operacional.

Licencia: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — compartir y adaptar libremente con atribución.
