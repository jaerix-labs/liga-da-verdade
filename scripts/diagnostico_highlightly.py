import json
import os
import sys
import time
from urllib import error, parse, request

BASE_URL = "https://soccer.highlightly.net"


def pedir(caminho, params):
    qs = parse.urlencode(params)
    url = f"{BASE_URL}/{caminho}?{qs}" if params else f"{BASE_URL}/{caminho}"
    req = request.Request(
        url,
        headers={
            "x-rapidapi-key": os.environ["HIGHLIGHTLY_KEY"],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    print(f"\n=== PEDIDO: {url} ===")
    try:
        with request.urlopen(req, timeout=30) as resp:
            corpo = resp.read().decode()
            cabecalhos_limite = {k: v for k, v in resp.getheaders() if "rate" in k.lower() or "limit" in k.lower() or "quota" in k.lower()}
            if cabecalhos_limite:
                print(f">>> cabeçalhos de limite: {cabecalhos_limite}")
    except error.HTTPError as e:
        print(f"ERRO HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        return None
    print(corpo[:3000])
    dados = json.loads(corpo)
    if isinstance(dados, dict):
        print(f">>> chaves de topo: {list(dados.keys())}")
        for k in ("plan", "pagination", "meta", "page", "totalPages", "hasNextPage"):
            if k in dados:
                print(f">>> {k} = {dados[k]}")
    time.sleep(2)
    return dados


ALVOS = {
    "GB-ENG": (["premier league"], "Premier League"),
    "ES": (["la liga", "laliga"], "La Liga"),
    "IT": (["serie a"], "Serie A"),
    "DE": (["bundesliga"], "Bundesliga"),
    "FR": (["ligue 1"], "Ligue 1"),
    "PT": (["primeira liga"], "Primeira Liga"),
}


def main():
    encontrados = {}
    candidatos_es_it = []
    for offset in (0, 100, 200, 300, 400, 500, 600, 700, 800, 900):
        if len(encontrados) == len(ALVOS):
            break
        ligas = pedir("leagues", {"offset": offset, "limit": 100})
        lista = ligas if isinstance(ligas, list) else (ligas or {}).get("data", [])
        if not lista:
            break
        for item in lista:
            nome = (item.get("name") or "").lower()
            pais = (item.get("country") or {}).get("code") or ""
            if pais in ("ES", "IT", "DE", "FR"):
                candidatos_es_it.append((pais, item.get("id"), item.get("name")))
            for pais_alvo, (trechos, etiqueta) in ALVOS.items():
                if pais_alvo in encontrados:
                    continue
                if pais == pais_alvo and any(t in nome for t in trechos):
                    encontrados[pais_alvo] = (item.get("id"), etiqueta)
                    print(f"\n>>> {etiqueta} ({pais_alvo}): leagueId={item.get('id')}")

    faltam = set(ALVOS) - set(encontrados)
    if faltam:
        print(f"\nNão encontrei por nome: {[ALVOS[p][1] for p in faltam]}", file=sys.stderr)
        print(f">>> Todas as ligas vistas em ES/IT/DE/FR (para procurar à mão): {candidatos_es_it}")

    print(f"\n>>> RESUMO FINAL: { {ALVOS[p][1]: lid for p, (lid, _) in encontrados.items()} }")


if __name__ == "__main__":
    main()
