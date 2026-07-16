#!/usr/bin/env python3
"""
Busca noticias nuevas sobre albergues/refugios de emergencia en Chile
(Google News RSS) y las deja en pending_review.md para revisión humana.

No escribe directamente en data.json: solo detecta candidatos.
Cristóbal decide qué entra al dashboard y edita data.json a mano
en la misma rama del PR que abre el workflow.

Uso local: python scripts/scrape_news.py
"""

import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

QUERIES = [
    "albergues SENAPRED",
    "albergue habilitado Chile",
    "refugio emergencia Chile sistema frontal",
    "evacuación preventiva albergue Chile",
]

SEEN_FILE = "seen_articles.json"
OUTPUT_FILE = "pending_review.md"
LOOKBACK_HOURS = 30  # margen sobre el intervalo de 24h del cron


def fetch_rss(query):
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(query)
        + "&hl=es-CL&gl=CL&ceid=CL:es"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_items(xml_bytes, query):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = item.findtext("pubDate")
        source = item.findtext("source")
        try:
            pub_date = parsedate_to_datetime(pub_date_raw)
        except Exception:
            pub_date = None
        items.append(
            {
                "query": query,
                "title": title,
                "link": link,
                "source": source or "",
                "pub_date": pub_date.isoformat() if pub_date else None,
            }
        )
    return items


def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(seen_links):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_links), f, ensure_ascii=False, indent=2)


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    seen = load_seen()
    new_items = []

    for query in QUERIES:
        try:
            xml_bytes = fetch_rss(query)
        except Exception as e:
            print(f"⚠️  Error consultando '{query}': {e}", file=sys.stderr)
            continue

        for item in parse_items(xml_bytes, query):
            if item["link"] in seen:
                continue
            if item["pub_date"]:
                try:
                    pub_dt = datetime.fromisoformat(item["pub_date"])
                    if pub_dt < cutoff:
                        continue
                except ValueError:
                    pass
            new_items.append(item)
            seen.add(item["link"])

    if not new_items:
        print("✓ Sin noticias nuevas sobre albergues en las últimas horas.")
        save_seen(seen)
        return 0

    print(f"🔔 {len(new_items)} noticia(s) nueva(s) detectada(s).")

    lines = [
        "# Noticias candidatas — revisar antes de actualizar `data.json`",
        "",
        f"Generado automáticamente: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Esto **no** modifica `data.json` solo. Revisa cada noticia, y si corresponde,",
        "agrega/edita el albergue a mano en `data.json` dentro de esta misma rama antes de mergear.",
        "",
    ]
    for it in new_items:
        lines.append(f"## {it['title']}")
        lines.append(f"- Fuente: {it['source'] or 'desconocida'}")
        lines.append(f"- Fecha: {it['pub_date'] or 'sin fecha'}")
        lines.append(f"- Link: {it['link']}")
        lines.append(f"- Búsqueda: `{it['query']}`")
        lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    save_seen(seen)
    return 1  # señala al workflow que hay novedades


if __name__ == "__main__":
    sys.exit(main())
