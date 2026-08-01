#!/usr/bin/env python3
"""
O mesmo registro da Paizo, capturado duas vezes com grafia diferente.

O extrator do AoN e o do Foundry as vezes escrevem o mesmo feat com uma letra
trocada (`Vermilion`/`Vermillion`), um espaco a mais (`Flash Forge`/
`Flashforge`), um plural (`Whisper`/`Whispers of Warning`) ou uma palavra de
ligacao (`Voice of (the) Elements`). `reconciliar.py` casa por slug do nome;
como os slugs diferem, os dois nunca colidem e SOBREVIVEM como registros
independentes -- o jogador ve dois botoes para a mesma coisa, e cada um ocupa
um slot de escolha.

Isto NAO e inventar dado: os dois registros ja afirmam ser a mesma coisa
(mesmo livro, mesmo nivel, mesmos traits). O passo so para de trata-los como
dois.

As tres guardas que impedem fusao errada:

1. BLOCO por (kind, book, level). Sem ele a distancia de edicao 3 funde nome
   curto de coisas distintas -- medido: 8 divindades colapsam em `Norns`.
2. PARENTESES. `desmembrar_colisoes.py` cria irmaos com qualificador entre
   parenteses de proposito; fundir desfaria isso. Excecao: parentese identico
   dos dois lados nao desambigua nada (`Submersible Helm (Greater)`).
3. GUARDA ESTRUTURAL. Se o AoN conhece os DOIS nomes como docs distintos, sao
   duas coisas -- e o caso de `Eagle Eye`/`Eagle Eyes` (feat-8725/feat-8770) e
   `Goblin Lore`/`Goblin Song`. Hoje nenhum desses esta no estado
   so-aon/so-foundry, mas uma re-extracao futura pode armar a mina.

O nome canonico NAO e sempre o do AoN: o dump dele carrega typo em ~10 dos
pares (`Exemplar Resilency`, `Camoflage Coat`, `Repulse the Wicken`). O
desempate usa `pf2etools` como terceira fonte quando ela conhece um lado so.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_duplicata_de_nome.md

Spec: specs/2026-08-01-fusao-de-duplicata-de-nome.md (item 84 do TODO)
"""
import collections
import itertools
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
DUMP = f"{AQUI}/dados_brutos/aon_dump"

LIGACAO = {"the", "of", "dedication"}
DISTANCIA_MAX = 3


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def palavras(s: str) -> set:
    return {t for t in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split() if t}


def parentese(s: str):
    achado = re.findall(r"\(([^)]*)\)", s or "")
    return norm(achado[0]) if achado else None


def distancia(a: str, b: str) -> int:
    """Levenshtein, com corte barato por diferenca de tamanho."""
    if abs(len(a) - len(b)) > DISTANCIA_MAX:
        return 99
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1,
                             anterior[j - 1] + (ca != cb)))
        anterior = atual
    return anterior[-1]


def fonte_unica(registro: dict, qual: str) -> bool:
    xref = registro.get("xref") or {}
    outra = "foundry" if qual == "aon" else "aon"
    return qual in xref and outra not in xref


def teto_de_distancia(na: str, nb: str) -> int:
    """Quantas letras podem mudar, PROPORCIONAL ao tamanho do nome.

    Distancia absoluta 3 e segura em nome longo (`Automatic`/`Autonomic
    Psychic Action`, 22 caracteres) e catastrofica em nome curto: medido, ela
    funde `Cong` com `Norns` -- duas divindades distintas, mesmo livro, ambas
    com `level: None`, e o bloco por (kind, book, level) as poe no MESMO grupo
    em vez de separar. Nao adianta guarda estrutural: `Norns` nao existe no
    dump do AoN, entao nada la o desmente.

    3 letras num nome de 5 e outra palavra; 3 num de 22 e um typo.
    """
    maior = max(len(na), len(nb))
    return max(1, min(DISTANCIA_MAX, int(maior * 0.15)))


def forma_do_par(a: dict, b: dict):
    """Como os dois nomes diferem, ou None se diferem demais."""
    na, nb = norm(a["name"]), norm(b["name"])
    if na == nb:
        return "espaco"
    pa, pb = palavras(a["name"]), palavras(b["name"])
    if (pa < pb or pb < pa) and abs(len(pa) - len(pb)) == 1 and (pa ^ pb) <= LIGACAO:
        return "palavra"
    d = distancia(na, nb)
    return f"letra{d}" if d <= teto_de_distancia(na, nb) else None


def parenteses_ok(a: dict, b: dict) -> bool:
    """Sem parenteses nos dois, ou parentese identico nos dois."""
    qa, qb = parentese(a["name"]), parentese(b["name"])
    if qa is None and qb is None:
        return True
    return qa is not None and qa == qb


def carregar_nomes_do_aon() -> dict:
    """Nomes normalizados que o AoN conhece, por arquivo de categoria."""
    conhecidos = collections.defaultdict(set)
    if not os.path.isdir(DUMP):
        return conhecidos
    for arquivo in os.listdir(DUMP):
        if not arquivo.endswith(".json") or arquivo.startswith("_"):
            continue
        try:
            with open(f"{DUMP}/{arquivo}", encoding="utf-8") as fh:
                docs = json.load(fh)
        except Exception:
            continue
        if isinstance(docs, dict):
            docs = docs.get("docs") or docs.get("hits") or []
        if not isinstance(docs, list):
            continue
        categoria = arquivo[:-5]
        for doc in docs:
            if isinstance(doc, dict) and doc.get("name"):
                conhecidos[categoria].add(norm(doc["name"]))
    return conhecidos


def aon_conhece_os_dois(a: dict, b: dict, conhecidos: dict) -> bool:
    """Guarda estrutural: se o AoN tem os dois nomes, sao duas coisas.

    A comparacao e por nome NORMALIZADO, entao ela nao sabe distinguir um par
    que difere so por espaco (`Flash Forge` e `Flashforge` normalizam para a
    mesma string). Nesse caso a guarda veria "o AoN conhece os dois" olhando
    para o mesmo registro duas vezes, e vetaria fusao legitima -- medido: ela
    barrou 6 pares, entre eles `Flash Forge`, um dos 7 defeitos que a triagem
    documentou. Se os nomes normalizados sao iguais, nao ha o que a guarda
    possa afirmar: ela se abstem.
    """
    if norm(a["name"]) == norm(b["name"]):
        return False
    kind = a.get("kind")
    nomes = conhecidos.get(kind) or set()
    if not nomes:
        nomes = set().union(*conhecidos.values()) if conhecidos else set()
    return norm(a["name"]) in nomes and norm(b["name"]) in nomes


def escolher_canonico(a: dict, b: dict):
    """Quem fica com o nome. Devolve (vencedor, perdedor, motivo)."""
    lado_aon, lado_fnd = (a, b) if fonte_unica(a, "aon") else (b, a)
    tem_p2t_aon = "pf2etools" in (lado_aon.get("xref") or {})
    tem_p2t_fnd = "pf2etools" in (lado_fnd.get("xref") or {})
    if tem_p2t_fnd and not tem_p2t_aon:
        return lado_fnd, lado_aon, "pf2etools conhece so o nome do Foundry"
    if tem_p2t_aon and not tem_p2t_fnd:
        return lado_aon, lado_fnd, "pf2etools conhece so o nome do AoN"
    return lado_aon, lado_fnd, "empate na terceira fonte -- vence o AoN"


def unir_grants(vencedor: dict, perdedor: dict):
    """Uniao dos grants. Devolve (grants, divergiu)."""
    gv = vencedor.get("grants") or []
    gp = perdedor.get("grants") or []
    if not gp:
        return gv, False
    if not gv:
        return gp, False
    vistos = {json.dumps(g, sort_keys=True) for g in gv}
    extras = [g for g in gp if json.dumps(g, sort_keys=True) not in vistos]
    return gv + extras, bool(extras)


def fundir(vencedor: dict, perdedor: dict, motivo: str) -> dict:
    """Aplica a politica de fusao da spec sobre o vencedor, no lugar."""
    conflitos = list(vencedor.get("conflitos") or [])

    aliases = list(vencedor.get("aliases") or [])
    for nome in [perdedor["name"], *(perdedor.get("aliases") or [])]:
        if nome and nome not in aliases and nome != vencedor["name"]:
            aliases.append(nome)
    vencedor["aliases"] = aliases

    vencedor["xref"] = {**(perdedor.get("xref") or {}), **(vencedor.get("xref") or {})}

    herdou_grants = not (vencedor.get("grants") or []) and bool(perdedor.get("grants"))
    grants, divergiu = unir_grants(vencedor, perdedor)
    vencedor["grants"] = grants
    if herdou_grants:
        pv, pp = vencedor.get("prov"), perdedor.get("prov")
        if isinstance(pv, dict) and isinstance(pp, dict) and "grants" in pp:
            pv["grants"] = pp["grants"]
    if divergiu:
        conflitos.append({"campo": "grants", "de": perdedor["id"],
                          "valor": perdedor.get("grants"), "estado": "REVISAR"})

    # Herdar campo exige herdar a PROVENIENCIA dele junto: o portao 1 cobra
    # `prov[campo]` para todo campo preenchido, e adotar o valor sem a origem
    # deixava 6 registros sem rastro.
    prov_v = vencedor.get("prov")
    prov_p = perdedor.get("prov")
    for campo in ("text", "requires", "rarity"):
        if perdedor.get(campo) and perdedor.get(campo) != vencedor.get(campo):
            if not vencedor.get(campo):
                vencedor[campo] = perdedor[campo]
                if isinstance(prov_v, dict) and isinstance(prov_p, dict) and campo in prov_p:
                    prov_v[campo] = prov_p[campo]
            else:
                conflitos.append({"campo": campo, "de": perdedor["id"],
                                  "valor": perdedor[campo]})

    fonte_v = vencedor.get("source") or {}
    fonte_p = perdedor.get("source") or {}
    if fonte_v.get("page") is None and fonte_p.get("page") is not None:
        fonte_v["page"] = fonte_p["page"]
    if fonte_p.get("remaster") is not None and fonte_p.get("remaster") != fonte_v.get("remaster"):
        conflitos.append({"campo": "source.remaster", "de": perdedor["id"],
                          "valor": fonte_p.get("remaster")})
    vencedor["source"] = fonte_v

    # `prov` NAO vira lista. A v2 da spec mandava unir as duas proveniencias
    # num array; medido, isso quebra o portao 1 (proveniencia por campo
    # preenchido) em 286 registros, porque o portao le `prov` como mapa de
    # campo -> fonte. A proveniencia do perdedor vai para `historico`, que e
    # onde rastro de fusao ja mora.
    if perdedor.get("prov"):
        conflitos.append({"campo": "prov", "de": perdedor["id"],
                          "valor": perdedor["prov"]})

    hist = list(vencedor.get("historico") or []) + list(perdedor.get("historico") or [])
    hist.append({"passo": "fundir_duplicata_de_nome", "absorveu": perdedor["id"],
                 "motivo": motivo})
    vencedor["historico"] = hist

    if conflitos:
        vencedor["conflitos"] = conflitos
    return vencedor


def reapontar(registros: list, de_para: dict) -> int:
    """Toda citacao do id perdedor passa a citar o canonico. Devolve trocas."""
    if not de_para:
        return 0
    # O lookahead nao e detalhe: `wb:feat/knight-vigilant` e PREFIXO de
    # `wb:feat/knight-vigilant-dedication`, e sem ele as 23 citacoes do segundo
    # viravam `...-dedication-dedication`. Medido -- o criterio de prova 5
    # pegou.
    padrao = re.compile("(?:" + "|".join(
        re.escape(k) for k in sorted(de_para, key=len, reverse=True)) + r")(?![a-z0-9-])")
    trocas = 0
    for registro in registros:
        for campo in ("requires", "grants", "progressao", "requires_residuo"):
            if campo not in registro or registro[campo] is None:
                continue
            bruto = json.dumps(registro[campo], ensure_ascii=False)
            if not padrao.search(bruto):
                continue
            novo, n = padrao.subn(lambda m: de_para[m.group(0)], bruto)
            if n:
                registro[campo] = json.loads(novo)
                trocas += n
    return trocas


def main() -> None:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        registros = json.load(fh)

    conhecidos = carregar_nomes_do_aon()

    blocos = collections.defaultdict(list)
    for registro in registros:
        fonte = registro.get("source") or {}
        blocos[(registro.get("kind"), fonte.get("book"), registro.get("level"))].append(registro)

    pares, vetados = [], []
    for grupo in blocos.values():
        for a, b in itertools.combinations(grupo, 2):
            if not ((fonte_unica(a, "aon") and fonte_unica(b, "foundry"))
                    or (fonte_unica(b, "aon") and fonte_unica(a, "foundry"))):
                continue
            if tuple(sorted(a.get("traits") or [])) != tuple(sorted(b.get("traits") or [])):
                continue
            pa = (a.get("source") or {}).get("page")
            pb = (b.get("source") or {}).get("page")
            if pa is not None and pb is not None and pa != pb:
                continue
            if not parenteses_ok(a, b):
                continue
            forma = forma_do_par(a, b)
            if not forma:
                continue
            if aon_conhece_os_dois(a, b, conhecidos):
                vetados.append((a, b, forma))
                continue
            pares.append((a, b, forma))

    de_para, fundidos = {}, []
    mortos = set()
    for a, b, forma in pares:
        if a["id"] in mortos or b["id"] in mortos:
            continue          # um registro so participa de uma fusao por rodada
        vencedor, perdedor, motivo = escolher_canonico(a, b)
        fundir(vencedor, perdedor, motivo)
        de_para[perdedor["id"]] = vencedor["id"]
        mortos.add(perdedor["id"])
        fundidos.append((vencedor, perdedor, forma, motivo))

    registros = [r for r in registros if r["id"] not in mortos]
    trocas = reapontar(registros, de_para)

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=1)

    por_kind = collections.Counter(v.get("kind") for v, _, _, _ in fundidos)
    por_forma = collections.Counter(f for _, _, f, _ in fundidos)
    linhas = [
        "# Fusao de duplicata de nome aon/foundry",
        "",
        f"Pares fundidos: **{len(fundidos)}**. "
        f"Registros: {len(registros) + len(mortos)} -> **{len(registros)}**.",
        f"Referencias re-apontadas: **{trocas}**.",
        f"Vetados pela guarda estrutural (o AoN conhece os dois nomes): {len(vetados)}.",
        "",
        f"Por kind: {dict(por_kind)}",
        f"Por forma: {dict(por_forma)}",
        "",
        "| canonico | absorvido | kind | forma | desempate |",
        "|---|---|---|---|---|",
    ]
    for vencedor, perdedor, forma, motivo in sorted(fundidos, key=lambda x: x[0]["name"]):
        linhas.append(f"| {vencedor['name']} | {perdedor['name']} | "
                      f"{vencedor.get('kind')} | {forma} | {motivo} |")
    if vetados:
        linhas += ["", "## Vetados pela guarda estrutural", "",
                   "O AoN conhece os DOIS nomes como docs distintos.", "",
                   "| a | b | forma |", "|---|---|---|"]
        for a, b, forma in sorted(vetados, key=lambda x: x[0]["name"]):
            linhas.append(f"| {a['name']} | {b['name']} | {forma} |")

    with open(f"{BASE}/relatorio_duplicata_de_nome.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")

    print(f"fundidos: {len(fundidos)} pares  "
          f"({len(registros) + len(mortos)} -> {len(registros)} registros)")
    print(f"referencias re-apontadas: {trocas}")
    print(f"vetados pela guarda estrutural: {len(vetados)}")
    print(f"por kind: {dict(por_kind)}")
    print(f"-> {BASE}/relatorio_duplicata_de_nome.md")


if __name__ == "__main__":
    main()
