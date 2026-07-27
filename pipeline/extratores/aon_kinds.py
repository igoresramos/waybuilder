#!/usr/bin/env python3
"""
Extrator das categorias que so existem no AoN.

`relic` (219) e `language` (155) nunca sairam porque a lista de kinds da spec
nao os mencionava -- mesma classe de erro do `ritual`: omissao ao escrever a
lista, nao falha de extrator. Medido contra o censo do AoN em 2026-07-26.

Nenhuma das duas categorias existe no Foundry nem no pf2etools, entao aqui nao
ha reconciliacao a fazer: o AoN e a unica fonte, e `prov` diz isso em todo
campo.

Uso: python3 extratores/aon_kinds.py [relic language ...]
Saida: pipeline/saida/aon_kinds.json
"""
import json, os, re, sys, unicodedata, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
sys.path.insert(0, PIPELINE)
import traits_uniao                                # noqa: E402
DUMP = os.path.join(PIPELINE, "dados_brutos", "aon_dump")
SAIDA = os.path.join(PIPELINE, "saida", "aon_kinds.json")

# Sub-escolhas de classe: a segunda camada da progressao. Quando voce sobe de
# Bardo escolhe uma Musa, de Ladino um Racket, de Mago uma Escola e uma Tese.
# Modelando so `classe -> feature`, elas ficam invisiveis -- e pior, entram na
# progressao como se fossem concedidas: o Wizard listava **37 features no nivel
# 1**, das quais a maioria e opcao mutuamente exclusiva.
#
# O AoN ja categoriza cada eixo separadamente, entao nao ha o que inferir.
# 80 `requires` da base ja citam essas entidades (portao 3) e nao achavam nada.
SUBESCOLHAS = [
    "arcane-school", "arcane-thesis", "bloodline", "cause", "conscious-mind",
    "doctrine", "druidic-order", "element", "hellknight-order", "hunters-edge",
    "hybrid-study", "ikon", "implement", "innovation", "instinct", "lesson",
    "methodology", "muse", "mystery", "patron", "racket", "research-field",
    "style", "subconscious-mind", "way", "draconic-exemplar", "mythic-calling",
    "deviant-ability-classification",
]

KINDS_PADRAO = ["relic", "language", "background"] + SUBESCOLHAS

# `background` ja tinha 332 registros vindos do extrator de ancestrias, mas o
# censo do AoN tem 499 entidades: faltavam 168, quase todas de Player's Guide de
# Adventure Path. Os que ja existem fundem por id no reconciliador; entram so os
# ausentes.
CAMPOS_POR_KIND = {
    "background": ("skill", "feat", "attribute"),
}

# Data de publicacao do Player Core no AoN -- mesmo corte usado pelo extrator
# de ancestrias, para nao ter dois criterios de "e remaster?" na mesma base.
REMASTER_CUTOFF = "2023-11-15"


def slug(nome):
    s = unicodedata.normalize("NFKD", str(nome or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def partir_fonte(bruto):
    """'Gamemastery Guide pg. 96' -> ('Gamemastery Guide', 96)."""
    if not bruto:
        return None, None
    texto = bruto[0] if isinstance(bruto, list) else str(bruto)
    m = re.match(r"^(.*?)\s+pg\.\s*(\d+)", texto)
    if m:
        return m.group(1).strip(), int(m.group(2))
    return texto.strip() or None, None


def limpar(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", str(t))
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return re.sub(r"[ \t]+", " ", t).strip()


def converter(d, kind):
    nome = d.get("name")
    if not nome:
        return None
    livro, pagina = partir_fonte(d.get("primary_source_raw") or d.get("primary_source"))
    lancamento = str(d.get("release_date") or "")
    # mesma uniao do reconciliador (mapa legado->remaster + absorcao por
    # granularidade), senao o trait entra cru e desfaz o item 20
    traits, aliases_traits, _ = traits_uniao.unir(
        {"aon": [str(t) for t in (d.get("trait") or [])]})
    reg = {
        "id": f"wb:{kind}/{slug(nome)}",
        "kind": kind,
        "name": nome,
        "level": d.get("level"),
        "traits": traits,
        "rarity": (d.get("rarity") or "common"),
        "source": {"book": livro, "page": pagina,
                   "remaster": bool(lancamento >= REMASTER_CUTOFF) if lancamento else False},
        "requires": None,
        "grants": [],
        # `mechanized: false` nao e lacuna, e o caso normal (principio zero da
        # spec): o app exibe o texto e o jogador resolve na mesa. Nem reliquia
        # nem idioma tem efeito derivavel para o construtor calcular.
        "mechanized": False,
        "text": f"wb:text/{kind}/{slug(nome)}",
        "xref": {"aon": str(d.get("id"))},
        "prov": {"name": "aon", "level": "aon", "traits": "aon", "rarity": "aon",
                 "source": "aon", "text": "aon"},
    }
    if d.get("remaster_id") or d.get("legacy_id"):
        reg["xref"]["aon_ponte"] = [str(x) for x in
                                    (d.get("remaster_id") or d.get("legacy_id") or [])]

    # campos proprios do kind: sem eles o registro novo sairia mais pobre que os
    # que ja estavam na base, e o merge nao teria de onde completar
    for campo in CAMPOS_POR_KIND.get(kind, ()):
        valor = d.get(campo)
        if valor not in (None, "", []):
            reg[campo] = valor
            reg["prov"][campo] = "aon"
    return reg


def extrair(kinds=None):
    kinds = kinds or KINDS_PADRAO
    saida, por_kind = [], collections.Counter()
    for kind in kinds:
        caminho = os.path.join(DUMP, f"{kind}.json")
        if not os.path.exists(caminho):
            print(f"  ! sem dump para '{kind}' em {caminho}", file=sys.stderr)
            continue
        vistos = {}
        # o VIGENTE pega o slug limpo, o legado leva o sufixo. Sem esta ordem
        # quem chega primeiro no dump e que fica com o id bonito, e ai o
        # canonico sai como `wb:methodology/alchemical-sciences-methodology-5`
        # enquanto `wb:methodology/alchemical-sciences` some na fusao -- toda
        # referencia que cita o nome limpo vira orfa.
        docs = sorted(json.load(open(caminho)),
                      key=lambda d: (1 if d.get("remaster_id") else 0,
                                     str(d.get("id"))))
        for d in docs:
            reg = converter(d, kind)
            if not reg:
                continue
            # Colisao de slug e o normal aqui: o AoN indexa a versao legada e a
            # remaster com o MESMO nome (`relic` cai de 219 para 123 se a
            # segunda for descartada). Descartar violaria "nada e descartado" e
            # repetiria o defeito que este trabalho esta corrigindo. Cada uma
            # ganha id proprio; `fundir_renomeados.py` reune o par depois, pela
            # ponte declarada em remaster_id/legacy_id.
            if reg["id"] in vistos:
                if d.get("remaster_id"):
                    reg["id"] = f"{reg['id']}-legacy"      # este e o lado antigo
                    reg["text"] = reg["text"] + "-legacy"
                if reg["id"] in vistos:
                    reg["id"] = f"{reg['id']}-{slug(d.get('id'))}"
                    reg["text"] = f"wb:text/{kind}/{reg['id'].split('/', 1)[-1]}"
            vistos[reg["id"]] = reg
            saida.append(reg)
            por_kind[kind] += 1
    return saida, por_kind


def main():
    kinds = sys.argv[1:] or KINDS_PADRAO
    regs, por_kind = extrair(kinds)
    json.dump(regs, open(SAIDA, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"registros: {len(regs)}")
    for k, n in por_kind.most_common():
        print(f"  {k:12} {n:>5}")
    print(f"-> {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
