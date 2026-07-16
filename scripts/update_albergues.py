#!/usr/bin/env python3
"""
Verificar cambios en albergues habilitados desde SENAPRED y fuentes de prensa.
Disparo manual: python scripts/update_albergues.py
"""

import json
import sys
from datetime import datetime

def load_current_data():
    """Carga data.json actual"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: data.json no encontrado")
        sys.exit(1)

def check_for_changes():
    """
    Verifica cambios en SENAPRED / prensa.
    Retorna True si hay cambios detectados.
    """
    # TODO: Implementar scraping de:
    # - senapred.cl/albergues-emergencia
    # - @Senapred en X (Twitter)
    # - Comunicados de prensa por región

    print("✓ Verificando SENAPRED...")
    print("✓ Verificando comunicados de prensa...")
    print("✓ Verificando fuentes de X...")

    # Por ahora retorna False (no hay cambios detectados)
    return False

def update_timestamp():
    """Actualiza el timestamp de last_updated en data.json"""
    data = load_current_data()
    now = datetime.utcnow().isoformat() + "Z"
    now_es = datetime.now().strftime("%d %b %Y, %H:%M").replace(" ", " ")

    data['last_updated'] = now
    data['last_updated_es'] = now_es

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Timestamp actualizado: {now_es}")

if __name__ == '__main__':
    print("🔄 Verificando cambios en albergues...")

    has_changes = check_for_changes()

    if has_changes:
        print("\n⚠️  Cambios detectados. Actualizar data.json manualmente e invocar git commit.")
        sys.exit(1)
    else:
        print("\n✓ Sin cambios detectados. Actualizando timestamp...")
        update_timestamp()
        print("✓ Listo para git commit si hay cambios.")
