# Albergues Habilitados — Sistema Frontal Julio 2026

Dashboard público de albergues habilitados en respuesta a emergencias climáticas en Chile, compilado desde comunicados de SENAPRED, delegaciones presidenciales regionales y municipios.

**Sitio en vivo:** (se completa después de deploy a Netlify)

## Estructura

```
albergues-senapred/
├── index.html              # Dashboard (carga datos de data.json)
├── data.json               # Datos de albergues + metadata
├── scripts/
│   └── scrape_news.py      # Busca noticias nuevas de albergues (Google News RSS)
├── seen_articles.json      # Links ya vistos, evita duplicados entre corridas
├── .github/workflows/
│   └── check.yml           # GitHub Actions: corre diario a mediodía Santiago hasta 23 jul 2026
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
2. Haz commit y push:
   ```bash
   git add data.json
   git commit -m "Agregar albergues: [región, municipio]"
   git push
   ```
3. Netlify se redeploy automáticamente

#### Opción 2: Revisión diaria automática (hasta el 23 de julio 2026)
El workflow `.github/workflows/check.yml` corre todos los días a las 12:00 (América/Santiago) y:
1. Busca noticias nuevas sobre albergues/refugios en Google News (RSS, sin necesitar login ni API key)
2. Si encuentra algo que no había visto antes, **abre un Pull Request** con los titulares/links en `pending_review.md` — no toca `data.json` solo
3. Tú revisas el PR, editas `data.json` a mano en esa misma rama si corresponde, y haces merge

No hay scraping de X/Twitter: sin API oficial, un runner de GitHub Actions no puede leer el feed de forma confiable, así que se omitió en vez de simular algo que fallaría en silencio.

Para probar el workflow manualmente:
```bash
# En GitHub, ve a Actions → "Buscar noticias de albergues (diario, mediodía Santiago)" → "Run workflow"
```

**Requisito único:** en el repo, ve a Settings → Actions → General → "Workflow permissions" y marca "Allow GitHub Actions to create and approve pull requests" (viene desactivado por defecto en repos nuevos; sin esto el PR automático falla).

## Estructura de data.json

**Importante**: `index.html` no hace `fetch()` de `data.json` — los datos viven duplicados como arrays JS inline (`DATA` y `CODIGO_AZUL`) dentro del `<script>` del propio HTML, para que el dashboard funcione sin depender de una petición adicional. `data.json` es un **export/referencia** (útil para importar a otras herramientas), no la fuente que lee la página. Si editas albergues, hazlo en ambos lugares o vas a tener el dashboard desincronizado del JSON.

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
  ],
  "codigo_azul": [ /* mismo esquema, 50 albergues */ ],
  "codigo_azul_source": "Ministerio de Desarrollo Social y Familia — Código Azul",
  "codigo_azul_note": "Red permanente de invierno, no activada específicamente por el sistema frontal."
}
```

- **precision**: `"exacta"` = dirección/localidad puntual encontrada; `"aprox"` = centroide de comuna (sin dirección específica publicada)

## Sección "Código Azul" (invierno permanente)

Además de los albergues activados por el sistema frontal (compilados a mano desde prensa), el dashboard incluye un bloque colapsable con los **50 albergues de la red permanente Código Azul / Plan Protege** del Ministerio de Desarrollo Social — dirigida a personas en situación de calle durante el invierno, operativa independiente de la alerta actual.

- Fuente: https://codigoazul.ministeriodesarrollosocial.gob.cl/albergues (tabla oficial, con dirección/institución/cupos por región)
- Geocodificado con Nominatim/OpenStreetMap
- Cubre las 6 regiones de la emergencia actual: Valparaíso, Coquimbo, O'Higgins, Maule, Metropolitana, Los Ríos
- Tiene su propio botón de descarga CSV, separado del de emergencia, para no mezclar ambas categorías en Google My Maps

## Scripts

### `scrape_news.py`

Uso local:
```bash
python scripts/scrape_news.py
```

Busca 4 queries en Google News RSS (`albergues SENAPRED`, `albergue habilitado Chile`, `refugio emergencia Chile sistema frontal`, `evacuación preventiva albergue Chile`), filtra por las últimas ~30 horas, descarta lo ya visto (`seen_articles.json`) y escribe `pending_review.md` con lo nuevo. Exit code `1` si encontró algo nuevo (el workflow lo usa para decidir si abre PR), `0` si no.

No escribe ni inventa datos en `data.json` — solo señala noticias candidatas para revisión humana.

## GitHub Actions

**Workflow**: `.github/workflows/check.yml`
- Cron `0 16 * * *` UTC = 12:00 América/Santiago (Chile en horario estándar en julio, sin DST)
- Se auto-desactiva después del 23 de julio de 2026 (chequeo de fecha dentro del propio workflow, no hace falta borrarlo a mano)
- Ejecuta `scripts/scrape_news.py`
- Si hay noticias nuevas, abre un PR con `pending_review.md` para revisión
- Disparo manual: GitHub Actions UI → "Run workflow"

**Nota**: No hace auto-commit a `main`. El PR es el gate de revisión; el merge lo decides tú.

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
