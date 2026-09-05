import json
import os
import sys
import time
from urllib import error, request

BASE_URL = "https://soccer.highlightly.net"


def pedir(caminho, params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE_URL}/{caminho}?{qs}" if params else f"{BASE_URL}/{caminho}"
    req = request.Request(url, headers={"x-rapidapi-key": os.environ["HIGHLIGHTLY_KEY"]})
    print(f"\n=== PEDIDO: {url} ===")
    try:
        with request.urlopen(req, timeout=30) as resp:
            corpo = resp.read().decode()
    except error.HTTPError as e:
        print(f"ERRO HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        return None
    print(corpo[:4000])
    time.sleep(2)
    return json.loads(corpo)


def main():
    ligas = pedir("leagues", {"name": "Premier League"})
    liga_id = None
    if ligas:
        lista = ligas if isinstance(ligas, list) else ligas.get("data", [])
        if lista:
            liga_id = lista[0].get("id") or lista[0].get("leagueId")
            print(f"\n>>> A usar leagueId={liga_id} para os próximos pedidos")

    if liga_id is None:
        print("\nNão consegui obter um leagueId — a parar aqui.", file=sys.stderr)
        return

    for season in (2026, 2025):
        jogos = pedir("matches", {"leagueId": liga_id, "season": season})
        lista = jogos if isinstance(jogos, list) else (jogos or {}).get("data", [])
        if lista:
            print(f"\n>>> season={season} devolveu {len(lista)} jogos — a usar este.")
            match_id = lista[0].get("id")
            pedir(f"statistics/{match_id}", {})
            pedir(f"events/{match_id}", {})
            break
    else:
        print("\nNenhuma das duas épocas testadas (2025, 2026) devolveu jogos.", file=sys.stderr)


if __name__ == "__main__":
    main()
