import json
import os
import sys
import time
from pathlib import Path
from urllib import error, request

BASE_URL = "https://v3.football.api-sports.io"
SEASON = 2026
LIGAS = {
    94: "Primeira Liga",
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
}
LIGA_GRANDES = 94
NOMES_GRANDES = ["Benfica", "Porto", "Sporting"]

# Margem de segurança sob o limite de 100 pedidos/dia do plano gratuito da
# API-Football. Se uma corrida precisar de mais do que isto, o resto fica
# para a corrida seguinte — ver CLAUDE.md, Segunda Parte.
MAX_PEDIDOS_POR_CORRIDA = 90

SAIDA = Path(__file__).resolve().parent.parent / "dados" / "estatisticas-2026-27.json"

pedidos_feitos = 0
ultimo_pedido = 0.0


def pedir(caminho, params):
    global pedidos_feitos, ultimo_pedido

    if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
        return None

    espera = 6.5 - (time.monotonic() - ultimo_pedido)
    if espera > 0:
        time.sleep(espera)

    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE_URL}/{caminho}?{qs}"
    req = request.Request(url, headers={"x-apisports-key": os.environ["API_FOOTBALL_KEY"]})

    try:
        with request.urlopen(req, timeout=30) as resp:
            corpo = json.loads(resp.read())
    except error.HTTPError as e:
        print(f"ERRO HTTP {e.code} em {caminho}: {e.read().decode(errors='replace')}", file=sys.stderr)
        raise

    pedidos_feitos += 1
    ultimo_pedido = time.monotonic()

    if corpo.get("errors"):
        print(f"AVISO — a API devolveu erros em {caminho}: {corpo['errors']}", file=sys.stderr)

    return corpo["response"]


def carregar_existente():
    if SAIDA.exists():
        return json.loads(SAIDA.read_text(encoding="utf-8"))
    return {"epoca": "2026-27", "ligas": LIGAS, "equipas": {}}


def resolver_grandes():
    equipas = pedir("teams", {"league": LIGA_GRANDES, "season": SEASON})
    if equipas is None:
        return {}
    grandes = {}
    for item in equipas:
        nome = item["team"]["name"]
        if any(alvo.lower() in nome.lower() for alvo in NOMES_GRANDES):
            grandes[item["team"]["id"]] = nome
    return grandes


def top3_liga(liga_id):
    classificacao = pedir("standings", {"league": liga_id, "season": SEASON})
    if not classificacao:
        return {}
    tabela = classificacao[0]["league"]["standings"][0]
    return {linha["team"]["id"]: linha["team"]["name"] for linha in tabela[:3]}


def fixtures_terminados(liga_id):
    jogos = pedir("fixtures", {"league": liga_id, "season": SEASON})
    if jogos is None:
        return []
    return [j for j in jogos if j["fixture"]["status"]["short"] == "FT"]


def valor_stat(stats_equipa, tipo):
    for item in stats_equipa["statistics"]:
        if item["type"] == tipo:
            return item["value"] or 0
    return 0


def processar_fixture(fixture_id, id_casa, id_fora):
    stats = pedir("fixtures/statistics", {"fixture": fixture_id})
    eventos = pedir("fixtures/events", {"fixture": fixture_id})
    if stats is None or eventos is None:
        return None
    if len(stats) < 2:
        return None

    stats_por_equipa = {s["team"]["id"]: s for s in stats}
    delta = {
        id_casa: _delta_vazio(),
        id_fora: _delta_vazio(),
    }

    for equipa_id, adversario_id in ((id_casa, id_fora), (id_fora, id_casa)):
        s = stats_por_equipa.get(equipa_id)
        if s is None:
            continue
        delta[equipa_id]["faltas_cometidas"] += valor_stat(s, "Fouls")
        delta[adversario_id]["faltas_sofridas"] += valor_stat(s, "Fouls")
        delta[equipa_id]["remates_area_propria"] += valor_stat(s, "Shots insidebox")
        delta[adversario_id]["remates_area_adversario"] += valor_stat(s, "Shots insidebox")

    for ev in eventos:
        equipa_id = ev["team"]["id"]
        adversario_id = id_fora if equipa_id == id_casa else id_casa
        tipo = ev["type"]
        detalhe = (ev.get("detail") or "").lower()

        if tipo == "Card":
            if "yellow" in detalhe and "red" in detalhe:
                delta[equipa_id]["segundo_amarelo_propria_equipa"] += 1
                delta[adversario_id]["segundo_amarelo_adversario"] += 1
            elif "yellow" in detalhe:
                delta[equipa_id]["amarelos_propria_equipa"] += 1
                delta[adversario_id]["amarelos_adversario"] += 1
            elif "red" in detalhe:
                delta[equipa_id]["vermelhos_propria_equipa"] += 1
                delta[adversario_id]["vermelhos_adversario"] += 1
            else:
                print(f"AVISO — cartão com detalhe desconhecido no jogo {fixture_id}: {ev.get('detail')}", file=sys.stderr)
        elif tipo == "Goal" and detalhe in ("penalty", "missed penalty"):
            delta[equipa_id]["penaltis_a_favor"] += 1
            delta[adversario_id]["penaltis_contra"] += 1

    return delta


def _delta_vazio():
    return {
        "faltas_cometidas": 0,
        "faltas_sofridas": 0,
        "amarelos_propria_equipa": 0,
        "amarelos_adversario": 0,
        "segundo_amarelo_propria_equipa": 0,
        "segundo_amarelo_adversario": 0,
        "vermelhos_propria_equipa": 0,
        "vermelhos_adversario": 0,
        "remates_area_propria": 0,
        "remates_area_adversario": 0,
        "penaltis_a_favor": 0,
        "penaltis_contra": 0,
    }


def equipa_vazia(nome, liga_nome):
    base = {"nome": nome, "liga": liga_nome, "top3_atualmente": True, "jogos_processados": [], "jogos_analisados": 0}
    base.update(_delta_vazio())
    return base


def main():
    dados = carregar_existente()
    equipas = dados["equipas"]
    try:
        processar_tudo(dados, equipas)
    finally:
        dados["gerado_em"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        dados["pedidos_usados_nesta_corrida"] = pedidos_feitos
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Gravado em {SAIDA} ({pedidos_feitos} pedidos usados nesta corrida) — mesmo que a corrida tenha parado a meio por erro.")


def processar_tudo(dados, equipas):
    grupo_desta_corrida = {}
    grandes = resolver_grandes()
    for equipa_id, nome in grandes.items():
        grupo_desta_corrida[equipa_id] = (nome, LIGAS[LIGA_GRANDES])

    for liga_id, liga_nome in LIGAS.items():
        if liga_id == LIGA_GRANDES:
            continue
        for equipa_id, nome in top3_liga(liga_id).items():
            grupo_desta_corrida[equipa_id] = (nome, liga_nome)

    if not grupo_desta_corrida:
        print("Não foi possível determinar nenhuma equipa nesta corrida — a sair sem tocar no ficheiro.", file=sys.stderr)
        sys.exit(1)

    ids_desta_corrida = set(grupo_desta_corrida)
    for chave, equipa in equipas.items():
        equipa["top3_atualmente"] = int(chave) in ids_desta_corrida

    for equipa_id, (nome, liga_nome) in grupo_desta_corrida.items():
        chave = str(equipa_id)
        if chave not in equipas:
            equipas[chave] = equipa_vazia(nome, liga_nome)
        else:
            equipas[chave]["nome"] = nome
            equipas[chave]["liga"] = liga_nome

    fixtures_por_liga = {}
    for liga_id in LIGAS:
        if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
            break
        fixtures_por_liga[liga_id] = fixtures_terminados(liga_id)

    for liga_id, fixtures in fixtures_por_liga.items():
        for jogo in fixtures:
            if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
                print("Limite de pedidos desta corrida atingido — o resto fica para a próxima.", file=sys.stderr)
                break

            fid = jogo["fixture"]["id"]
            id_casa = jogo["teams"]["home"]["id"]
            id_fora = jogo["teams"]["away"]["id"]

            if id_casa not in grupo_desta_corrida and id_fora not in grupo_desta_corrida:
                continue

            ja_processado = all(
                fid in equipas[str(eid)]["jogos_processados"]
                for eid in (id_casa, id_fora)
                if eid in grupo_desta_corrida
            )
            if ja_processado:
                continue

            delta = processar_fixture(fid, id_casa, id_fora)
            if delta is None:
                continue

            for equipa_id in (id_casa, id_fora):
                if equipa_id not in grupo_desta_corrida:
                    continue
                chave = str(equipa_id)
                if fid in equipas[chave]["jogos_processados"]:
                    continue
                for campo, valor in delta[equipa_id].items():
                    equipas[chave][campo] += valor
                equipas[chave]["jogos_processados"].append(fid)
                equipas[chave]["jogos_analisados"] = len(equipas[chave]["jogos_processados"])


if __name__ == "__main__":
    main()
