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


def testar_liga(liga_id, etiqueta):
    print(f"\n########## {etiqueta} (leagueId={liga_id}) ##########")
    for offset in (0, 100, 200, 300):
        jogos = pedir("matches", {"leagueId": liga_id, "season": 2026, "offset": offset, "limit": 100})
        lista = jogos if isinstance(jogos, list) else (jogos or {}).get("data", [])
        terminados = [j for j in lista if (j.get("state") or {}).get("score", {}).get("current") is not None]
        print(f"\n>>> offset={offset}: {len(lista)} jogos devolvidos, {len(terminados)} com resultado.")
        if terminados:
            match_id = terminados[-1].get("id")
            print(f">>> A usar match_id={match_id}: {terminados[-1]}")
            pedir(f"statistics/{match_id}", {})
            pedir(f"events/{match_id}", {})
            return
        if not lista:
            break
    print(f"\nNenhum offset testado devolveu jogos terminados para {etiqueta}.", file=sys.stderr)


def main():
    ligas = pedir("leagues", {})
    id_premier = None
    id_primeira = None
    if ligas:
        lista = ligas if isinstance(ligas, list) else ligas.get("data", [])
        for item in lista:
            nome = (item.get("name") or "").lower()
            pais = (item.get("country") or {}).get("code") or ""
            if "premier league" in nome and pais == "GB-ENG":
                id_premier = item.get("id") or item.get("leagueId")
            if "primeira liga" in nome and pais == "PT":
                id_primeira = item.get("id") or item.get("leagueId")
        print(f"\n>>> Premier League (Inglaterra) leagueId={id_premier}")
        print(f">>> Primeira Liga (Portugal) leagueId={id_primeira}")

    if id_premier:
        testar_liga(id_premier, "Premier League")
    if id_primeira:
        testar_liga(id_primeira, "Primeira Liga")


if __name__ == "__main__":
    main()
