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
    print(corpo[:4000])
    time.sleep(2)
    return json.loads(corpo)


def main():
    ligas = pedir("leagues", {})
    liga_id = None
    if ligas:
        lista = ligas if isinstance(ligas, list) else ligas.get("data", [])
        for item in lista:
            nome = (item.get("name") or "").lower()
            if "premier league" in nome and "u2" not in nome and "women" not in nome:
                liga_id = item.get("id") or item.get("leagueId")
                print(f"\n>>> Encontrado: {item}")
                break
        print(f"\n>>> A usar leagueId={liga_id} para os próximos pedidos")

    if liga_id is None:
        print("\nNão consegui obter um leagueId — a parar aqui.", file=sys.stderr)
        return

    for season in (2026, 2025):
        jogos = pedir("matches", {"leagueId": liga_id, "season": season})
        lista = jogos if isinstance(jogos, list) else (jogos or {}).get("data", [])
        terminados = [j for j in lista if (j.get("state") or {}).get("score", {}).get("current") is not None]
        print(f"\n>>> season={season}: {len(lista)} jogos devolvidos, {len(terminados)} com resultado.")
        if terminados:
            match_id = terminados[-1].get("id")
            print(f">>> A usar match_id={match_id}: {terminados[-1]}")
            pedir(f"statistics/{match_id}", {})
            pedir(f"events/{match_id}", {})
            break
    else:
        print("\nNenhuma das duas épocas testadas (2025, 2026) devolveu jogos.", file=sys.stderr)


if __name__ == "__main__":
    main()
