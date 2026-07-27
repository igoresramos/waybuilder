#!/usr/bin/env python3
"""
Waybuilder -- medicao da regra 17b (teto de invocacao).

Pergunta: a rota de NIVEL DE CLASSE (dip conjurador) entrega mais ou menos
invocacao que a rota de DEDICACAO de arquetipo, que sob Free Archetype e
gratuita? Regra 21 exige que entregue MAIS.

Nenhum numero deste arquivo e inventado. Cada um vem de leitura de arquivo em
disco ou de chamada ao motor de producao. As fontes estao em FONTES.

Uso:  python3 medir_17b.py
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "motor"))

import motor  # noqa: E402  (precisa do sys.path acima)

INDEX = os.path.join(RAIZ, "pipeline", "base", "index.json")
BENCH = os.path.join(RAIZ, "pipeline", "dados_brutos", "bench_monstros.json")
QUICKRULES = os.path.join(RAIZ, "pipeline", "dados_brutos", "pf2etools_repo",
                          "data", "quickrules.json")

FONTES = {
    "index": "pipeline/base/index.json (kind=spell, campos traits/rank/texto)",
    "bench": "pipeline/dados_brutos/bench_monstros.json (mediana AoN por nivel)",
    "quickrules": ("pipeline/dados_brutos/pf2etools_repo/data/quickrules.json "
                   "-> pf2-h3 'Spellcasting Archetypes' (APG p.149)"),
    "motor": "motor/motor.py -> Personagem.cap_invocacao / .conjuracao",
}

# ----------------------------------------------------------------- premissas
#
# Declaradas de proposito. A LESSONS.md registra que uma simulacao anterior de
# nivel 20 foi invalidada por comparar lados que gastavam acoes diferentes.
# Aqui os quatro regimes pagam EXATAMENTE o mesmo custo de acao, entao a unica
# variavel e o rank da magia. Nada de gear, atributo ou DC entra na conta --
# invocacao nao rola ataque nem impoe save do conjurador, o minion e que rola.
#
PREMISSAS = [
    "Alvo: monstro MEDIANO do bench_monstros no MESMO nivel do personagem.",
    "Minion: usa atk/dmg medianos do bench_monstros no nivel da criatura.",
    "Acoes -- identicas nos 4 regimes: 3 para conjurar, 1 por rodada para "
    "comandar o minion (trait minion). Nenhum regime gasta acao a mais.",
    "Minion comandado recebe 2 acoes: 2 Strikes com MAP 0 / -5.",
    "Combate de 4 rodadas. Rodada 1 o conjurador gasta as 3 acoes conjurando "
    "e nao sobra acao para comandar; o minion age nas rodadas 2, 3 e 4.",
    "Gear/atributo/DC do conjurador NAO entram: nao afetam invocacao.",
    "Dedicacao roda RAW puro (regra 18): sem elevacao e sem teto 17b.",
]


# ------------------------------------------------------------------- fontes
def carregar_magias() -> list[dict]:
    with open(INDEX, encoding="utf-8") as fh:
        idx = json.load(fh)
    return [e for e in idx if e.get("kind") == "spell"]


def carregar_bench() -> dict[int, dict]:
    with open(BENCH, encoding="utf-8") as fh:
        return {int(k): v for k, v in json.load(fh).items()}


def rank_dedicacao_por_nivel() -> dict[int, int]:
    """Progressao RAW de slot de arquetipo conjurador.

    Lida do texto de quickrules.json em vez de escrita a mao. O bloco
    'Spellcasting Archetypes' (APG p.149) descreve os tres feats em prosa;
    o parser abaixo extrai (nivel -> rank de slot) de cada frase.
    """
    with open(QUICKRULES, encoding="utf-8") as fh:
        dados = json.load(fh)
    bruto = json.dumps(dados, ensure_ascii=False)
    ini = bruto.find('"Spellcasting Archetypes"')
    fim = bruto.find('"Alchemical Archetypes"', ini)
    if ini < 0 or fim < 0:
        raise RuntimeError("bloco 'Spellcasting Archetypes' nao achado em quickrules")
    bloco = bruto[ini:fim]

    ORD = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5,
           "6th": 6, "7th": 7, "8th": 8}
    # nivel em que o feat costuma ser pego, por feat
    base_feat = {}
    for nome, chave in (("Basic Spellcasting Feat", "basic"),
                        ("Expert Spellcasting Feat", "expert"),
                        ("Master Spellcasting Feat", "master")):
        m = re.search(re.escape(nome) + r".{0,80}?(\d+)(?:st|nd|rd|th) level", bloco)
        if not m:
            raise RuntimeError(f"nivel base de {nome} nao achado")
        base_feat[chave] = int(m.group(1))

    ganhos: dict[int, int] = {}
    # frases do tipo "grant a Nth-level spell slot" (no nivel base do feat)
    # e "At Nth level, they grant you a Mth-level spell slot"
    for chave, nome in (("basic", "Basic Spellcasting Feat"),
                        ("expert", "Expert Spellcasting Feat"),
                        ("master", "Master Spellcasting Feat")):
        i = bloco.find(nome)
        j = bloco.find("Spellcasting Feat", i + len(nome))
        trecho = bloco[i:j if j > 0 else len(bloco)]
        # primeiro slot: o que o feat concede no nivel em que e pego
        m = re.search(r"grant(?:s)?(?: you)? an? (\w+)-level spell slot", trecho)
        if m:
            ganhos[base_feat[chave]] = ORD[m.group(1)]
        # slots posteriores. Tres armadilhas no texto do APG:
        #  - "at 16th level" vem em minuscula, depois de "and";
        #  - o rank 8 vem como "an 8th-level", nao "a 8th-level";
        #  - "Usually available at 4th level, these feats grant a 1st-level..."
        #    casa com um `.{0,120}?` frouxo e rouba o "At 6th level" seguinte.
        #    Por isso o "they grant you" fica colado, sem curinga no meio.
        for m in re.finditer(r"[Aa]t (\d+)(?:st|nd|rd|th) level, they "
                             r"grant you an? (\w+)-level spell slot", trecho):
            ganhos[int(m.group(1))] = ORD[m.group(2)]

    # acumula: rank maximo acessivel em cada nivel de personagem
    tabela, atual = {}, 0
    for nv in range(1, 21):
        if nv in ganhos:
            atual = max(atual, ganhos[nv])
        tabela[nv] = atual
    return tabela, ganhos


# ------------------------------------------------- escada rank -> criatura
LADDER_RE = re.compile(r"Heightened \((\d+)(?:st|nd|rd|th)\) Level (-?\d+)")
BASE_RE = re.compile(r"whose level is (?:(-?\d+)|(-?\d+) or lower|"
                     r"(-?\d+) to fight)", re.I)


def escada_de_invocacao(magia: dict) -> dict[int, int] | None:
    """rank da magia -> nivel da criatura invocada, lido da prosa."""
    # o AoN usa travessao (en dash) para nivel negativo: "whose level is -1"
    txt = (magia.get("texto") or "").replace("–", "-").replace("−", "-")
    escada: dict[int, int] = {}
    # nivel base, no rank nativo da magia
    m = re.search(r"whose level is (-?\d+)", txt)
    if m:
        escada[magia["rank"]] = int(m.group(1))
    for m in LADDER_RE.finditer(txt):
        escada[int(m.group(1))] = int(m.group(2))
    return escada or None


# --------------------------------------------------------------- combate
def grau(total: int, dc: int, nat: int) -> int:
    g = 3 if total >= dc + 10 else 2 if total >= dc else 1 if total > dc - 10 else 0
    if nat == 20:
        g = min(3, g + 1)
    elif nat == 1:
        g = max(0, g - 1)
    return g


def dano_esperado_strike(atk: int, dmg: int, ac: int, mapen: int) -> float:
    """Valor esperado exato, enumerando as 20 faces. Sem Monte Carlo."""
    tot = 0.0
    for n in range(1, 21):
        g = grau(n + atk + mapen, ac, n)
        if g == 3:
            tot += 2 * dmg
        elif g == 2:
            tot += dmg
    return tot / 20.0


def dpr_minion(nivel_criatura: int, bench: dict, ac_alvo: int) -> float:
    """Dano por rodada de um minion comandado: 2 Strikes, MAP 0 / -5."""
    if nivel_criatura < min(bench) or nivel_criatura > max(bench):
        # bench comeca no nivel 1; criatura de nivel <= 0 nao tem linha.
        return 0.0
    m = bench[nivel_criatura]
    return (dano_esperado_strike(m["atk"], m["dmg"], ac_alvo, 0)
            + dano_esperado_strike(m["atk"], m["dmg"], ac_alvo, -5))


# ----------------------------------------------------------------- regimes
def ceil2(n: int) -> int:
    return math.ceil(n / 2)


def cap_17b(class_level: int, char_level: int) -> int:
    """Formula da regra 17b, replicada para checagem contra o motor."""
    return min(ceil2(class_level) + 2, ceil2(char_level))


def cap_proposto(class_level: int, char_level: int, rank_ded: int) -> int:
    """Variante com PISO na rota gratuita -- satisfaz a regra 21 por construcao."""
    return min(max(ceil2(class_level) + 2, rank_ded), ceil2(char_level))


def doc_sintetico(splits: list[tuple[str, int]]) -> dict:
    esc = [{"em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/human"},
           {"em": "criacao", "slot": "heranca", "pega": "wb:heritage/skilled-heritage"},
           {"em": "criacao", "slot": "background",
            "pega": "wb:background/scholar-of-the-ancients"}]
    n = 0
    for cid, qtd in splits:
        for _ in range(qtd):
            n += 1
            esc.append({"em": n, "slot": "nivel_de_classe", "pega": cid})
    return {"esquema": "waybuilder/personagem@1", "escolhas": esc,
            "atores": [], "inventario": [], "manual": {}}


# -------------------------------------------------------------------- main
def main() -> None:
    magias = carregar_magias()
    bench = carregar_bench()
    tabela_ded, ganhos_ded = rank_dedicacao_por_nivel()
    base = motor.Base(INDEX)

    saida: list[str] = []

    def p(s: str = "") -> None:
        saida.append(s)
        print(s)

    p("=" * 78)
    p("1. RECORTE POR TRAIT")
    p("=" * 78)
    p(f"fonte: {FONTES['index']}")
    summon = [e for e in magias if "summon" in (e.get("traits") or [])]
    incarn = [e for e in magias if "incarnate" in (e.get("traits") or [])]
    inter = {e["id"] for e in summon} & {e["id"] for e in incarn}
    p(f"magias no index                 : {len(magias)}")
    p(f"trait `summon`                  : {len(summon)}")
    p(f"trait `incarnate`               : {len(incarn)}")
    p(f"interseccao                     : {len(inter)}")
    p(f"total sob a 17b                 : {len(summon) + len(incarn)}")
    p()

    def dist(lst):
        d = {}
        for e in lst:
            d[e["rank"]] = d.get(e["rank"], 0) + 1
        return dict(sorted(d.items()))

    p(f"distribuicao de rank `summon`   : {dist(summon)}")
    p(f"distribuicao de rank `incarnate`: {dist(incarn)}")
    p(f"rank minimo `incarnate`         : {min(e['rank'] for e in incarn)}")
    p()

    # incarnate escala com heightened?
    com_h = [e for e in incarn if e.get("heightened")]
    com_hp = [e for e in incarn if e.get("heightened_so_prosa")]
    p(f"`incarnate` com heightened estruturado : {len(com_h)}  "
      f"{[e['name'] for e in com_h]}")
    p(f"`incarnate` com heightened so em prosa : {len(com_hp)}  "
      f"{[e['name'] for e in com_hp]}")
    p("=> incarnate nao eleva: acima do portao o dip tem o MESMO poder que o puro.")
    p("   O teto sobre incarnate e binario (acesso), nao gradual.")
    p()
    sum_com_h = [e for e in summon if escada_de_invocacao(e)]
    p(f"`summon` com escada de nivel de criatura: {len(sum_com_h)}/{len(summon)}")
    p()

    p("=" * 78)
    p("2. ESCADA rank-da-magia -> nivel-da-criatura")
    p("=" * 78)
    p(f"fonte: prosa do campo `texto` em {FONTES['index']}")
    escadas: dict[str, dict[int, int]] = {}
    for e in sorted(summon, key=lambda x: (x["rank"], x["name"])):
        esc = escada_de_invocacao(e)
        if esc:
            escadas[e["name"]] = esc
    # a escada canonica: a mais longa (Summon Animal, rank 1 -> 10)
    canonica = max(escadas.values(), key=len)
    nome_canonica = [k for k, v in escadas.items() if v is canonica][0]
    p(f"escada canonica ({nome_canonica}):")
    for r in sorted(canonica):
        p(f"   rank {r:2d} -> criatura nivel {canonica[r]:3d}")
    divergentes = []
    for nome, esc in escadas.items():
        for r, lv in esc.items():
            if r in canonica and canonica[r] != lv:
                divergentes.append((nome, r, lv, canonica[r]))
    p(f"magias `summon` que divergem da escada canonica: {len(divergentes)}")
    for d in divergentes:
        p(f"   {d[0]}: rank {d[1]} -> nivel {d[2]} (canonica {d[3]})")
    p()

    p("=" * 78)
    p("3. PROGRESSAO DA ROTA GRATUITA (dedicacao de arquetipo, RAW)")
    p("=" * 78)
    p(f"fonte: {FONTES['quickrules']}")
    p(f"ganhos de slot lidos do texto: {ganhos_ded}")
    p("nivel de personagem -> rank maximo de slot de arquetipo:")
    p("   " + "  ".join(f"{nv}:{tabela_ded[nv]}" for nv in range(4, 21, 2)))
    p()

    p("=" * 78)
    p("4. CHECAGEM: a formula do motor bate com a spec?")
    p("=" * 78)
    p(f"fonte: {FONTES['motor']}")
    divs = 0
    for cl in range(0, 21):
        for ch in range(max(cl, 1), 21):
            stub = type("S", (), {"nivel": ch})()
            do_motor = motor.Personagem.cap_invocacao(stub, cl)
            se_esperado = cap_17b(cl, ch)
            if do_motor != se_esperado:
                divs += 1
    p(f"pares (class_level, char_level) testados : 231")
    p(f"divergencias motor vs spec               : {divs}")
    p()
    p("checagem fim-a-fim, personagem sintetico completo pelo motor:")
    for rotulo, splits in (("Wizard 20 puro", [("wb:class/wizard", 20)]),
                           ("Fighter 18 / Wizard 2",
                            [("wb:class/fighter", 18), ("wb:class/wizard", 2)]),
                           ("Fighter 19 / Wizard 1",
                            [("wb:class/fighter", 19), ("wb:class/wizard", 1)])):
        pj = motor.Personagem(doc_sintetico(splits), base)
        for c in pj.conjuracao:
            p(f"   {rotulo:24s} cl={c['nivel_de_classe']:2d} "
              f"slot_cru={c['max_rank_do_slot']:2d} "
              f"rank_efetivo(17)={c['rank_efetivo']:2d} "
              f"rank_invoc(17b)={c['rank_de_invocacao']:2d} slots={c['slots']}")
    p()

    p("=" * 78)
    p("5. COMPARACAO DOS QUATRO REGIMES")
    p("=" * 78)
    p(f"fonte de poder de criatura: {FONTES['bench']}")
    p("premissas:")
    for a in PREMISSAS:
        p(f"   - {a}")
    p()

    RODADAS_ATIVAS = 3   # rodada 1 e gasta conjurando (3 acoes)
    resumo = []
    for char in (12, 15, 20):
        alvo = bench[char]
        ac_alvo = alvo["ac"]
        rank_ded = tabela_ded[char]
        p("-" * 78)
        p(f"NIVEL DE PERSONAGEM {char}  "
          f"(alvo: monstro mediano nivel {char}, AC {ac_alvo}, "
          f"HP {alvo['hp']}, n={alvo['n']})")
        p("-" * 78)

        regimes = [
            ("(a) conjurador PURO (RAW)", char, ceil2(char), "17/17b"),
            ("(b) dip 2 SEM teto 17b", 2, ceil2(char), "so 17"),
            ("(c) dip 2 COM teto 17b", 2, cap_17b(2, char), "17b"),
            ("(c') dip 1 COM teto 17b", 1, cap_17b(1, char), "17b"),
            ("(d) dedicacao FREE ARCHETYPE", 0, rank_ded, "RAW (regra 18)"),
            ("(e) PROPOSTA piso-dedicacao, dip 2", 2,
             cap_proposto(2, char, rank_ded), "17b-v2"),
        ]
        p(f"{'regime':36s} {'cl':>3s} {'rank':>4s} {'criat':>5s} "
          f"{'DPR':>7s} {'4-rod':>7s} {'HP':>5s}")
        linhas = {}
        for nome, cl, rank, _origem in regimes:
            rank = max(0, min(10, rank))
            nivel_cri = canonica.get(rank)
            if nivel_cri is None:
                p(f"{nome:36s} {cl:3d} {rank:4d}  sem entrada na escada")
                continue
            d = dpr_minion(nivel_cri, bench, ac_alvo)
            fora = nivel_cri not in bench
            hp_cri = bench[nivel_cri]["hp"] if not fora else 0
            p(f"{nome:36s} {cl:3d} {rank:4d} {nivel_cri:5d} "
              f"{d:7.1f} {d * RODADAS_ATIVAS:7.1f} {hp_cri:5d}"
              + ("   (nivel fora do bench, que comeca em 1)" if fora else ""))
            linhas[nome] = (rank, nivel_cri, d, d * RODADAS_ATIVAS, hp_cri)

        a = linhas["(a) conjurador PURO (RAW)"]
        c = linhas["(c) dip 2 COM teto 17b"]
        d_ = linhas["(d) dedicacao FREE ARCHETYPE"]
        e_ = linhas["(e) PROPOSTA piso-dedicacao, dip 2"]
        p()
        p(f"   (c) vs (d): rank {c[0]} vs {d_[0]} | criatura nivel {c[1]} vs {d_[1]} "
          f"| dano 4 rodadas {c[3]:.1f} vs {d_[3]:.1f}")
        if d_[3] > 0:
            p(f"   (c) entrega {c[3] / d_[3] * 100:.0f}% do que a rota GRATUITA entrega"
              f"  -> regra 21 {'OK' if c[3] >= d_[3] else 'VIOLADA'}")
        if a[3] > 0:
            p(f"   (c) entrega {c[3] / a[3] * 100:.0f}% do conjurador puro (a)")
            p(f"   (d) entrega {d_[3] / a[3] * 100:.0f}% do conjurador puro (a)")
            frac_d = f", {e_[3] / d_[3] * 100:.0f}% da dedicacao" if d_[3] else ""
            p(f"   (e) entrega {e_[3] / a[3] * 100:.0f}% do conjurador puro (a)"
              + frac_d)
        # quantos niveis de classe o dip precisa pra empatar com a rota gratuita
        preciso = next((cl for cl in range(1, 21) if cap_17b(cl, char) >= rank_ded), None)
        p(f"   niveis de classe necessarios para o dip EMPATAR com a dedicacao: "
          f"{preciso}")
        # acesso a incarnate
        acc_c = sum(1 for x in incarn if x["rank"] <= c[0])
        acc_d = sum(1 for x in incarn if x["rank"] <= d_[0])
        acc_a = sum(1 for x in incarn if x["rank"] <= a[0])
        acc_e = sum(1 for x in incarn if x["rank"] <= e_[0])
        p(f"   magias `incarnate` acessiveis (de {len(incarn)}): "
          f"(a) {acc_a}  (c) {acc_c}  (d) {acc_d}  (e-proposta) {acc_e}")
        p()
        resumo.append(dict(char=char, rank_c=c[0], rank_d=d_[0], rank_a=a[0],
                           rank_e=e_[0], cri_c=c[1], cri_d=d_[1], cri_a=a[1],
                           cri_e=e_[1], dano_c=c[3], dano_d=d_[3], dano_a=a[3],
                           dano_e=e_[3], inc_c=acc_c, inc_d=acc_d, inc_a=acc_a,
                           inc_e=acc_e, empate=preciso))

    p("=" * 78)
    p("6. AS INCARNATE QUE O TETO BLOQUEIA (evidencia de que o cap importa)")
    p("=" * 78)
    for e in sorted(incarn, key=lambda x: (x["rank"], x["name"])):
        dados = re.findall(r"\d+d\d+", e.get("texto") or "")
        p(f"   rank {e['rank']:2d}  {e['rarity']:9s} {e['name']:38s} "
          f"dados no texto: {' '.join(dados[:6]) if dados else '(sem dado)'}")
    p()

    p("=" * 78)
    p("6b. MAGIAS `summon` SEM ESCADA (o teto nao tem o que reduzir nelas)")
    p("=" * 78)
    for e in summon:
        if not escada_de_invocacao(e):
            txt = re.sub(r"\s+", " ", e.get("texto") or "")
            m = re.search(r"---(.{0,220})", txt)
            p(f"   rank {e['rank']}  {e['name']}: {m.group(1).strip() if m else txt[:200]}")
    p()

    p("=" * 78)
    p("7. VERIFICACAO DA PROPOSTA (piso na rota gratuita)")
    p("=" * 78)
    p("formula: rank = min( max( ceil(cl/2)+2 , rank_dedicacao(char) ), ceil(char/2) )")
    quebras = 0
    for c in range(1, 21):
        if cap_proposto(c, c, tabela_ded[c]) != ceil2(c):
            quebras += 1
    p(f"classe unica continua == RAW em todos os 20 niveis: "
      f"{'SIM' if quebras == 0 else f'NAO ({quebras} quebras)'}")
    viola_atual = viola_prop = 0
    for ch in range(4, 21):
        for cl in range(1, ch + 1):
            if cap_17b(cl, ch) < tabela_ded[ch]:
                viola_atual += 1
            if cap_proposto(cl, ch, tabela_ded[ch]) < tabela_ded[ch]:
                viola_prop += 1
    total = sum(ch for ch in range(4, 21))
    p(f"pares (cl, char) com char>=4 testados          : {total}")
    p(f"violacoes da regra 21 -- formula ATUAL         : {viola_atual}")
    p(f"violacoes da regra 21 -- formula PROPOSTA      : {viola_prop}")
    p()
    p("exemplos trabalhados que a spec cita, sob a proposta:")
    for rot, cl, ch in (("Summoner 2 / personagem 12", 2, 12),
                        ("Summoner 20 puro", 20, 20),
                        ("Mago 2 / personagem 5", 2, 5),
                        ("Mago 1 / personagem 20", 1, 20),
                        ("Mago 10 / Guerreiro 10", 10, 20)):
        p(f"   {rot:28s} atual={cap_17b(cl, ch):2d}  "
          f"proposta={cap_proposto(cl, ch, tabela_ded[ch]):2d}  "
          f"(sem teto seria {ceil2(ch)})")
    p()

    p("=" * 78)
    p("8. RESUMO")
    p("=" * 78)
    p(f"{'char':>4s} {'(a) puro':>9s} {'(c) 17b':>8s} {'(d) ded':>8s} "
      f"{'(e) prop':>9s} {'c/d':>6s} {'c/a':>6s} {'empate':>7s}")
    for r in resumo:
        p(f"{r['char']:4d} {r['dano_a']:9.1f} {r['dano_c']:8.1f} {r['dano_d']:8.1f} "
          f"{r['dano_e']:9.1f} {r['dano_c'] / r['dano_d'] * 100 if r['dano_d'] else 0:5.0f}% "
          f"{r['dano_c'] / r['dano_a'] * 100 if r['dano_a'] else 0:5.0f}% "
          f"{r['empate']:7d}")

    with open(os.path.join(HERE, "medir_17b_saida.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(saida) + "\n")


if __name__ == "__main__":
    main()
