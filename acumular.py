"""
Acumula o histórico de dividendos de FIIs com datas corretas.

Roda diariamente via GitHub Actions (ver .github/workflows/acumular.yml).
Busca o dividendos.json do radar-dividendos e adiciona entradas novas
ao historico_fiis_acumulado.json, sem sobrescrever o que já existe.

Dedup por: ativo + data_com (normalizado para ISO yyyy-MM-dd).
"""

import json
import os
import requests

RADAR_URL = "https://raw.githubusercontent.com/Gemiclo/radar-dividendos/main/dividendos.json"
OUTPUT_FILE = "historico_fiis_acumulado.json"


def norm_key(data_com: str) -> str:
    """Normaliza dd/mm/yy ou dd/mm/yyyy para yyyy-MM-dd."""
    parts = data_com.strip().split("/")
    if len(parts) != 3:
        return data_com
    d, m, y = parts[0], parts[1], parts[2]
    if len(y) == 2:
        y = "20" + y
    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"


def main():
    # Carrega histórico acumulado existente
    existing: list = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    # Monta conjunto de chaves já presentes (dedup)
    seen: set[str] = set()
    for item in existing:
        ativo = item.get("ativo", "")
        data_com = item.get("data_com", "")
        if ativo and data_com:
            seen.add(f"{ativo}|{norm_key(data_com)}")

    # Busca dividendos.json atual do radar-dividendos
    resp = requests.get(RADAR_URL, timeout=15)
    resp.raise_for_status()
    novos: list = resp.json()

    # Adiciona entradas que ainda não existem
    added = 0
    for item in novos:
        ativo = item.get("ativo", "")
        data_com = item.get("data_com", "")
        if not ativo or not data_com:
            continue
        key = f"{ativo}|{norm_key(data_com)}"
        if key not in seen:
            existing.append(item)
            seen.add(key)
            added += 1

    # Ordena por ativo + data_com para leitura humana
    existing.sort(key=lambda x: (x.get("ativo", ""), norm_key(x.get("data_com", ""))))

    # Salva
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)

    print(f"Adicionados: {added} | Total: {len(existing)}")


if __name__ == "__main__":
    main()
