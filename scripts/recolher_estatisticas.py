import json
import os
import sys
import time
from pathlib import Path
from urllib import error, parse, request

BASE_URL = "https://soccer.highlightly.net"
SEASON = 2026
LIGAS = {
    80778: "Primeira Liga",
    33973: "Premier League",
    119924: "La Liga",
    115669: "Serie A",
    67162: "Bundesliga",
    52695: "Ligue 1",
}
LIGA_GRANDES = 80778
NOMES_GRANDES = ["Benfica", "Porto", "Sporting"]

# Margem de segurança sob o limite de 100 pedidos/dia do plano gratuito do
# Highlightly (confirmado no cabeçalho x-ratelimit-requests-limit). Se uma
# corrida precisar de mais do que isto, o resto fica para a corrida seguinte
# — ver CLAUDE.md, Segunda Parte.
MAX_PEDIDOS_POR_CORRIDA = 90

SAIDA = Path(__file__).resolve().parent.parent / "dados" / "estatisticas-2026-27.json"

pedidos_feitos = 0
ultimo_pedido = 0.0


def pedir(caminho, params):
    global pedidos_feitos, ultimo_pedido

    if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
        return None

    espera = 1.0 - (time.monotonic() - ultimo_pedido)
    if espera > 0:
        time.sleep(espera)

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

    try:
        with request.urlopen(req, timeout=30) as resp:
            corpo = json.loads(resp.read())
    except error.HTTPError as e:
        print(f"ERRO HTTP {e.code} em {caminho}: {e.read().decode(errors='replace')}", file=sys.stderr)
        raise

    pedidos_feitos += 1
    ultimo_pedido = time.monotonic()
    return corpo


def carregar_existente():
    if SAIDA.exists():
        return json.loads(SAIDA.read_text(encoding="utf-8"))
    return {"epoca": "2026-27", "ligas": LIGAS, "equipas": {}}


def top3_liga(liga_id):
    """None = sem orçamento/erro (o chamador deve manter a marcação anterior).
    {} = pedido respondeu mas sem classificação utilizável."""
    classificacao = pedir("standings", {"leagueId": liga_id, "season": SEASON})
    if classificacao is None:
        return None
    grupos = classificacao.get("groups") or []
    if not grupos:
        return {}
    tabela = sorted(grupos[0].get("standings", []), key=lambda linha: linha.get("position", 999))
    return {linha["team"]["id"]: linha["team"]["name"] for linha in tabela[:3]}


def fixtures_terminados(liga_id):
    terminados = []
    for offset in (0, 100, 200, 300, 400):
        jogos = pedir("matches", {"leagueId": liga_id, "season": SEASON, "offset": offset, "limit": 100})
        if jogos is None:
            break
        lista = jogos.get("data", [])
        if not lista:
            break
        terminados.extend(j for j in lista if (j.get("state") or {}).get("description") == "Finished")
        if len(lista) < 100:
            break
    return terminados


def valor_stat(stats_equipa, nome_campo):
    for item in stats_equipa.get("statistics", []):
        if item.get("displayName") == nome_campo:
            return item.get("value") or 0
    return 0


def processar_fixture(fixture_id, id_casa, id_fora):
    stats = pedir(f"statistics/{fixture_id}", {})
    eventos = pedir(f"events/{fixture_id}", {})
    if stats is None or eventos is None:
        return None
    if not isinstance(stats, list) or len(stats) < 2:
        return None

    stats_por_equipa = {s["team"]["id"]: s for s in stats}
    delta = {id_casa: _delta_vazio(), id_fora: _delta_vazio()}

    for equipa_id, adversario_id in ((id_casa, id_fora), (id_fora, id_casa)):
        s = stats_por_equipa.get(equipa_id)
        if s is None:
            continue
        delta[equipa_id]["faltas_cometidas"] += valor_stat(s, "Fouls")
        delta[adversario_id]["faltas_sofridas"] += valor_stat(s, "Fouls")
        delta[equipa_id]["remates_area_propria"] += valor_stat(s, "Shots within penalty area")
        delta[adversario_id]["remates_area_adversario"] += valor_stat(s, "Shots within penalty area")

    # O Highlightly não distingue vermelho direto de 2º amarelo num campo
    # próprio: emite dois eventos "Yellow Card" para o mesmo jogador e depois
    # um "Red Card" — a consequência do 2º amarelo, não uma expulsão nova.
    # Por isso contamos amarelos por jogador e ignoramos o "Red Card" que se
    # segue a um 2º amarelo já contado, para não duplicar a expulsão.
    amarelos_por_jogador = {}
    expulso_por_segundo_amarelo = set()
    for ev in eventos:
        equipa_id = ev["team"]["id"]
        adversario_id = id_fora if equipa_id == id_casa else id_casa
        tipo = ev.get("type")
        jogador = ev.get("playerId")

        if tipo == "Yellow Card":
            amarelos_por_jogador[jogador] = amarelos_por_jogador.get(jogador, 0) + 1
            if amarelos_por_jogador[jogador] >= 2:
                delta[equipa_id]["segundo_amarelo_propria_equipa"] += 1
                delta[adversario_id]["segundo_amarelo_adversario"] += 1
                expulso_por_segundo_amarelo.add(jogador)
            else:
                delta[equipa_id]["amarelos_propria_equipa"] += 1
                delta[adversario_id]["amarelos_adversario"] += 1
        elif tipo == "Red Card":
            if jogador not in expulso_por_segundo_amarelo:
                delta[equipa_id]["vermelhos_propria_equipa"] += 1
                delta[adversario_id]["vermelhos_adversario"] += 1
        elif tipo in ("Penalty", "Missed Penalty"):
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
    base = {
        "nome": nome,
        "liga": liga_nome,
        "grande": False,
        "top3_atualmente": False,
        "jogos_processados": {},
        "jogos_analisados": 0,
    }
    base.update(_delta_vazio())
    return base


def recalcular_totais(equipa):
    totais = _delta_vazio()
    for entrada in equipa["jogos_processados"].values():
        for campo, valor in entrada["delta"].items():
            totais[campo] += valor
    equipa.update(totais)
    equipa["jogos_analisados"] = len(equipa["jogos_processados"])


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
    """Processa TODAS as equipas das 6 ligas — não só as 18 seguidas. O
    top-3/"grande" é uma marcação calculada no fim (atualizar_marcacoes_top3),
    não um filtro do que se recolhe. Ver CLAUDE.md, Segunda Parte, D36: sem
    isto não há como calcular o percentil "contra todas as equipas"."""
    fixtures_por_liga = {}
    for liga_id in LIGAS:
        if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
            break
        fixtures_por_liga[liga_id] = fixtures_terminados(liga_id)

    agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for liga_id, fixtures in fixtures_por_liga.items():
        liga_nome = LIGAS[liga_id]
        for jogo in fixtures:
            if pedidos_feitos >= MAX_PEDIDOS_POR_CORRIDA:
                print("Limite de pedidos desta corrida atingido — o resto fica para a próxima.", file=sys.stderr)
                break

            fid = str(jogo["id"])
            id_casa = jogo["homeTeam"]["id"]
            id_fora = jogo["awayTeam"]["id"]

            for equipa_id, nome in ((id_casa, jogo["homeTeam"]["name"]), (id_fora, jogo["awayTeam"]["name"])):
                chave = str(equipa_id)
                if chave not in equipas:
                    equipas[chave] = equipa_vazia(nome, liga_nome)

            ja_processado = fid in equipas[str(id_casa)]["jogos_processados"] and fid in equipas[str(id_fora)]["jogos_processados"]
            if ja_processado:
                continue

            delta = processar_fixture(jogo["id"], id_casa, id_fora)
            if delta is None:
                continue

            for equipa_id in (id_casa, id_fora):
                chave = str(equipa_id)
                if fid in equipas[chave]["jogos_processados"]:
                    continue
                equipas[chave]["jogos_processados"][fid] = {
                    "delta": delta[equipa_id],
                    "data_jogo": jogo.get("date"),
                    "revisto_em": agora,
                    "adversario_id": id_fora if equipa_id == id_casa else id_casa,
                    "mandante": equipa_id == id_casa,
                }
                recalcular_totais(equipas[chave])

    atualizar_marcacoes_top3(equipas)
    revisar_fixtures_antigos(equipas, dados)


def atualizar_marcacoes_top3(equipas):
    """"Grande" nunca depende de pedidos à API — é só nome + liga, sempre
    recalculável de graça. O top-3 atual (móvel, D36) já precisa da
    classificação; se uma liga não responder por falta de orçamento nesta
    corrida, mantém-se a marcação da corrida anterior — nunca se apaga uma
    marcação por engano só porque a corrida ficou sem pedidos."""
    for equipa in equipas.values():
        equipa["grande"] = equipa.get("liga") == LIGAS[LIGA_GRANDES] and any(
            alvo.lower() in equipa["nome"].lower() for alvo in NOMES_GRANDES
        )

    for liga_id, liga_nome in LIGAS.items():
        ids_top3 = top3_liga(liga_id)
        if ids_top3 is None:
            continue
        for chave, equipa in equipas.items():
            if equipa.get("liga") != liga_nome:
                continue
            equipa["top3_atualmente"] = equipa["grande"] or (int(chave) in ids_top3)


DIAS_MINIMO_PARA_REVISAO = 18
PEDIDOS_RESERVADOS_PARA_REVISAO = 10


def revisar_fixtures_antigos(equipas, dados):
    """Revisita jogos já processados há mais de ~3 jornadas, para o caso de a
    API ter completado dados que na altura vieram incompletos (ex.: eventos
    vazios) — ver CLAUDE.md, Segunda Parte. Corre com um orçamento de pedidos
    à parte, para não competir com a recolha de jogos novos."""
    limite = min(MAX_PEDIDOS_POR_CORRIDA, pedidos_feitos + PEDIDOS_RESERVADOS_PARA_REVISAO)
    agora_struct = time.gmtime()

    # fid -> lista de (chave_equipa, entrada) — desde que passámos a seguir
    # todas as equipas das 6 ligas, cada jogo tem sempre as duas entradas.
    por_fixture = {}
    for chave, equipa in equipas.items():
        for fid, entrada in equipa["jogos_processados"].items():
            por_fixture.setdefault(fid, []).append((chave, entrada))

    candidatos = []
    for fid, entradas in por_fixture.items():
        revisto_mais_antigo = min(e["revisto_em"] for _, e in entradas)
        idade_dias = (time.mktime(agora_struct) - time.mktime(time.strptime(revisto_mais_antigo, "%Y-%m-%dT%H:%M:%SZ"))) / 86400
        if idade_dias >= DIAS_MINIMO_PARA_REVISAO:
            candidatos.append((revisto_mais_antigo, fid))
    candidatos.sort()

    for _, fid in candidatos:
        if pedidos_feitos >= limite:
            break

        chave_ref, entrada_ref = por_fixture[fid][0]
        id_equipa_ref = int(chave_ref)
        id_adversario = entrada_ref["adversario_id"]
        id_casa, id_fora = (id_equipa_ref, id_adversario) if entrada_ref["mandante"] else (id_adversario, id_equipa_ref)

        delta_novo = processar_fixture(int(fid), id_casa, id_fora)
        if delta_novo is None:
            continue

        agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for chave, entrada in por_fixture[fid]:
            equipa_id = int(chave)
            novo = delta_novo.get(equipa_id)
            if novo is None:
                continue
            if entrada["delta"] != novo:
                dados.setdefault("correcoes_detectadas", []).append(
                    {
                        "jogo": fid,
                        "equipa": equipas[chave]["nome"],
                        "antes": entrada["delta"],
                        "depois": novo,
                        "detetado_em": agora,
                    }
                )
                print(f"AVISO — correção detetada no jogo {fid} para {equipas[chave]['nome']}: {entrada['delta']} -> {novo}", file=sys.stderr)
            entrada["delta"] = novo
            entrada["revisto_em"] = agora
            recalcular_totais(equipas[chave])


if __name__ == "__main__":
    main()
