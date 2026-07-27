#!/usr/bin/env python3
"""
Tabela de slots de conjuracao a partir do markdown do AoN.

Por que existe: a extracao de 2026-07-26 concluiu que "nem Foundry nem AoN
materializam a tabela numerica -- so referenciam 'Animist Spells per Day' como
nome de tabela". A primeira metade e verdade: o item de classe do Foundry so
tem `spellcasting: 1`, um flag. A segunda **estava errada** -- o AoN carrega a
tabela inteira dentro do campo `markdown`, em HTML, e o extrator olhava so para
`text`, que e a versao achatada e sem tabela.

Consequencia daquele engano: o Animist ficou sem tabela, alguem foi ler as
paginas 12-13 do War of Immortals a olho (PDF imagem-only), o resultado foi
gravado num diretorio ignorado pelo git e se perdeu. O dado estava em disco o
tempo todo.

As 12 classes conjuradoras tem a tabela. As 11 que ja vieram do pf2etools
servem de validacao cruzada: se este parser reproduz as 11, ele esta certo para
a 12a.

Formato das celulas:
  "3"      slots simples
  "2+1"    Animist -- slots de animist + slots de apparition, pools separados
  "—"      sem slot naquele rank
  "—*"     sem slot normal, mas uma feature concede slots daquele rank. E o
           caso do Magus (studious spells, a partir do nivel 7). O asterisco
           NAO vira zero: vira anotacao, senao o registro diria que existe um
           rank com zero slots, que e diferente de "nao existe".

Uso:
    python3 tabelas_conjuracao_aon.py            # valida contra a base
    python3 tabelas_conjuracao_aon.py --emitir   # grava saida/tabelas_conjuracao_aon.json
"""
import json, os, re, sys, html

AQUI = os.path.dirname(os.path.abspath(__file__))
AON_CLASSES = f"{AQUI}/dados_brutos/aon_dump/class.json"
BASE = f"{AQUI}/base/index.json"
SAIDA = f"{AQUI}/saida/tabelas_conjuracao_aon.json"

RANK = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5,
        "6th": 6, "7th": 7, "8th": 8, "9th": 9, "10th": 10}
VAZIO = ("—", "-", "–", "", "0")


def celulas(tabela_html):
    """HTML da tabela -> lista achatada de celulas, na ordem de leitura."""
    puro = html.unescape(re.sub(r"<[^>]+>", "\t", tabela_html))
    return [c.strip() for c in puro.split("\t") if c.strip()]


def tabela_de_slots(markdown):
    """Acha a tabela de spells-per-day e devolve {nivel: {rank: n}}.

    A tabela e reconhecida pelo cabecalho -- comeca em 'Your Level' e traz uma
    coluna '1st'. Nao depende do titulo, que varia por classe ('Wizard Spells
    per Day', 'Apparition Spells per Day'...).
    """
    for t in re.findall(r"<table.*?</table>", markdown, re.S):
        cs = celulas(t)
        if not cs or "1st" not in cs[:14]:
            continue
        # cabecalho vai ate a ultima coluna de rank reconhecida
        fim = max(i for i, c in enumerate(cs[:14]) if c in RANK or c == "Cantrips"
                  or c == "Your Level")
        cab, corpo = cs[:fim + 1], cs[fim + 1:]
        larg = len(cab)
        colunas = [RANK.get(c) for c in cab]        # None em Your Level/Cantrips

        linhas = {}
        for i in range(0, len(corpo) - larg + 1, larg):
            fatia = corpo[i:i + larg]
            if not re.fullmatch(r"\d{1,2}", fatia[0]):
                break                                 # chegou nas notas de rodape
            nivel = int(fatia[0])
            if not 1 <= nivel <= 20:
                break
            ranks, notas = {}, []
            for col, cab_nome, val in zip(colunas, cab, fatia):
                if col is None:
                    if cab_nome == "Cantrips" and val not in VAZIO:
                        ranks["_cantrips"] = val.replace("*", "").strip()
                    continue
                marcado = "*" in val
                limpo = val.replace("*", "").strip()
                if limpo in VAZIO:
                    if marcado:
                        notas.append(col)      # rank so acessivel por feature
                    continue
                ranks[col] = limpo
            linhas[nivel] = ranks
            if notas:
                linhas[nivel] = dict(ranks, _por_feature=notas)
        if len(linhas) == 20:
            return linhas
    return None


def soma_celula(v):
    """'2+1' -> 3; '3' -> 3. O total e o que conta para numero de slots."""
    return sum(int(x) for x in re.findall(r"\d+", str(v)))


def normalizar(linhas):
    """{nivel: {rank: celula}} -> formato slots_per_level da base."""
    out = {}
    for nivel, ranks in sorted(linhas.items()):
        so_rank = {k: v for k, v in ranks.items()
                   if k not in ("_por_feature", "_cantrips")}
        feats = ranks.get("_por_feature") or []
        r = {str(k): soma_celula(v) for k, v in sorted(so_rank.items())}
        linha = {"cantrips": soma_celula(ranks["_cantrips"])
                 if "_cantrips" in ranks else None,
                 "ranks": r,
                 "max_rank": max((int(k) for k in r), default=0)}
        if feats:
            linha["ranks_por_feature"] = sorted(feats)
        out[str(nivel)] = linha
    return out


def carregar_aon():
    docs = json.load(open(AON_CLASSES))
    fora = {}
    for d in docs:
        if d.get("category") != "class" or not d.get("markdown"):
            continue
        nome = d.get("name")
        # o AoN traz o mesmo nome duas vezes (legacy + remaster); o que tem a
        # tabela com mais niveis ganha
        t = tabela_de_slots(d["markdown"])
        if t and (nome not in fora or len(t) > len(fora[nome])):
            fora[nome] = t
    return fora


def carregar_base():
    b = json.load(open(BASE))
    it = list(b.values()) if isinstance(b, dict) else b
    out = {}
    for r in it:
        sc = r.get("spellcasting")
        if r.get("kind") == "class" and isinstance(sc, dict):
            out[r["name"]] = sc.get("slots_per_level") or {}
    return out


def main():
    aon, base = carregar_aon(), carregar_base()
    print(f"classes com tabela no markdown do AoN: {len(aon)}")

    iguais, difs, novas = [], [], []
    for nome, linhas in sorted(aon.items()):
        atual = base.get(nome)
        derivado = normalizar(linhas)
        if not atual:
            novas.append(nome)
            continue
        erros = []
        for nv in map(str, range(1, 21)):
            a, d = atual.get(nv) or {}, derivado.get(nv) or {}
            ra = {k: int(v) for k, v in (a.get("ranks") or {}).items()}
            if ra != (d.get("ranks") or {}):
                erros.append(f"nv{nv} ranks: base={ra} aon={d.get('ranks')}")
            if a.get("cantrips") is not None and d.get("cantrips") is not None \
                    and int(a["cantrips"]) != d["cantrips"]:
                erros.append(f"nv{nv} truques: base={a['cantrips']} "
                             f"aon={d['cantrips']}")
        (iguais if not erros else difs).append((nome, erros))

    print(f"\nbatem exatamente com a base: {len(iguais)}")
    for n, _ in iguais:
        print(f"  OK   {n}")
    if difs:
        print(f"\nDIVERGEM: {len(difs)}")
        for n, e in difs:
            print(f"  DIF  {n} -- {len(e)} nivel(is)")
            for l in e[:4]:
                print(f"         {l}")
    if novas:
        print(f"\nSO NO AON (a base nao tem): {len(novas)}")
        for n in novas:
            d = normalizar(aon[n])
            print(f"  NOVA {n}: 20 niveis, max_rank nv20 = {d['20']['max_rank']}")

    if "--emitir" in sys.argv:
        payload = {
            "_doc": "Tabelas de slots extraidas do campo markdown do AoN. "
                    "Fonte independente do pf2etools -- serve de validacao "
                    "cruzada e cobre o Animist, que o pf2etools nao tem.",
            "prov": "aon (campo markdown do doc de classe, tabela reconhecida "
                    "pelo cabecalho 'Your Level' + coluna '1st')",
            "classes": {n: normalizar(t) for n, t in sorted(aon.items())},
            "celulas_hibridas": {
                "_doc": "Animist tem dois pools que nao se misturam. "
                        "slots_per_level soma os dois; o detalhe fica aqui.",
                "Animist": {
                    str(nv): {("cantrips" if k == "_cantrips" else str(k)): v
                              for k, v in sorted(r.items(), key=lambda x: str(x[0]))
                              if k != "_por_feature"}
                    for nv, r in sorted(aon.get("Animist", {}).items())},
            },
        }
        json.dump(payload, open(SAIDA, "w"), indent=1, ensure_ascii=False)
        print(f"\n-> {SAIDA}")
    return 1 if difs else 0


if __name__ == "__main__":
    sys.exit(main())
