#!/usr/bin/env python3
"""
Os portoes de qualidade da base canonica (spec v2, secao "Portoes de qualidade").

Regra que este arquivo existe para cumprir: **portao ausente e portao aprovado
nao podem parecer a mesma coisa.** Todos sao reportados, inclusive quando
passam. Na v1 o relatorio listava so falhas, e por isso 6 dos 7 portoes nunca
implementados passaram um build inteiro despercebidos.

O portao 7 (duas entidades no mesmo id) NAO mora aqui: ele tem de rodar antes
da fusao de id, e por isso vive em reconciliar.py. Aqui so se confere que ele
rodou.

Uso: python3 pipeline/portoes.py    (depois de reconciliar + emitir_textos + fundir)
Saida: pipeline/base/relatorio_portoes.md, exit 1 se algum falhar.
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comum  # noqa: E402

BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# kind -> (categoria no censo do AoN, tolerancia para MENOS, motivo da tolerancia)
#
# Excesso nao falha: o Foundry lista variantes (runas, graus, tamanhos) que o
# AoN indexa como uma entrada so. Falta falha -- e o sintoma que achou ritual,
# relic e language.
CENSO = {
    "ritual":            ("ritual", 0.02, ""),
    "relic":             ("relic", 0.02, ""),
    "language":          ("language", 0.02, ""),
    "background":        ("background", 0.02, ""),
    "spell":             ("spell", 0.02, ""),
    "feat":              ("feat", 0.02, ""),
    "class-feature":     ("class-feature", 0.10,
                          "o AoN indexa escolha de subclasse em categoria propria "
                          "(mystery, patron, instinct, doctrine)"),
    "heritage":          ("heritage", 0.03,
                          "o AoN indexa heranca versatil como ancestry"),
    "ancestry":          ("ancestry", 0.30,
                          "o AoN conta heranca versatil dentro de ancestry"),
    "deity":             ("deity", 0.02, ""),
    "domain":            ("domain", 0.02, ""),
    "trait":             ("trait", 0.02, ""),
    "skill":             ("skill", 0.02, ""),
    "archetype":         ("archetype", 0.02, ""),
    "familiar-ability":  ("familiar-ability", 0.05, ""),
    "tactic":            ("tactic", 0.02, ""),
    "class-kit":         ("class-kit", 0.02, ""),
    # `equipment` no AoN e categoria guarda-chuva: arma, armadura e escudo
    # entram nela. Comparar so contra o kind `equipment` da base acusava um
    # deficit de 205 que nao existe -- medido: 0 dos 6.304 vigentes esta
    # ausente da base quando se contam os quatro kinds juntos.
    "equipment":         ("equipment", 0.02,
                          "categoria guarda-chuva: soma equipment+weapon+armor+shield"),
    "weapon":            ("weapon", 0.02,
                          "a base emite variante por grau/runa que o AoN indexa "
                          "como uma entrada so, entao o excesso e esperado"),
    "armor":             ("armor", 0.02, "idem weapon"),
    "shield":            ("shield", 0.02, "idem weapon"),
    "class":             ("class", 0.02, ""),
    "familiar-specific": ("familiar-specific", 0.03, ""),
    "animal-companion":  ("animal-companion", 0.20,
                          "especializacao e avanco ficam fora por decisao de escopo"),
}


# Categorias do censo do AoN que estao FORA do escopo por decisao registrada
# na spec (bestiario, perigo, NPC, veiculo, conteudo de aventura, regra de
# reino). Categoria de fora fica aqui, nao no silencio.
FORA_DE_ESCOPO = {
    "creature", "creature-family", "creature-ability", "creature-adjustment",
    "hazard", "npc", "vehicle", "siege-weapon", "kingdom-structure",
    "kingdom-event", "rules", "sidebar", "action", "item-bonus", "source",
    "category-page", "article", "class-sample", "curse", "condition",
    "disease", "draconic-exemplar", "monster-family",
    "plane", "adventure", "trap", "spell-effect", "affliction", "campaign",
    "creature-theme-template", "weather-hazard", "equipment-list",
    # verificados contra a base em 2026-07-27, com o motivo:
    "deity-category",   # agrupamento editorial de deidades, nao entidade
    "campsite-meal",    # subsistema de acampamento do Kingmaker, nao escolha de ficha
    "warfare-tactic",   # regra de reino/guerra do Kingmaker -- a spec ja exclui
}

# Categoria do AoN que a base ja cobre DENTRO de outro kind. Nao e ausencia,
# e diferenca de taxonomia -- e fica escrito para ninguem "descobrir" de novo.
CATEGORIA_COBERTA = {
    "ikon": "class-feature (21 de 21 conferidos por nome: as ikons do Exemplar "
            "sao class-features na base)",
    "arcane-school": "trait (22 de 23: as escolas do Legacy sao traits; a base "
                     "segue a taxonomia remaster)",
}

# Kinds que podem ficar sem prosa, com o motivo escrito. Tudo que nao esta
# aqui e obrigado a ter `text`.
# Kind onde zero conflito nao e falta de instrumentacao: as fontes concordam
# mesmo. Exige medicao, nao suposicao -- a evidencia fica escrita aqui.
CONCORDANCIA_VERIFICADA = {
    "shield": "medido em 2026-07-27: dos 112 shields com 2+ fontes, 0 divergem "
              "de `source.book` contra o doc do AoN apontado pelo proprio xref",
}

ISENTOS_DE_PROSA = {
    "equipment": "objeto de tesouro (gema, obra de arte) nao tem texto de regra "
                 "em fonte nenhuma -- so nome, nivel e preco",
    "armor": "barding de montaria segue a tabela da armadura base, sem texto proprio",
}


class Resultado:
    def __init__(self):
        self.linhas = []
        self.falhou = False

    def portao(self, num, nome, ok, detalhe="", amostra=()):
        estado = "PASSA" if ok else "FALHA"
        if not ok:
            self.falhou = True
        self.linhas.append(f"### Portao {num} -- {nome}: **{estado}**")
        if detalhe:
            self.linhas.append("")
            self.linhas.append(detalhe)
        if amostra:
            self.linhas.append("")
            for a in list(amostra)[:25]:
                self.linhas.append(f"- {a}")
        self.linhas.append("")
        print(f"portao {num} {nome}: {estado} {detalhe.splitlines()[0] if detalhe else ''}")


def carregar_saida():
    """Estado pre-merge, por id: e onde da para ver divergencia entre fontes."""
    por_id = collections.defaultdict(list)
    for arq in sorted(os.listdir(f"{AQUI}/saida")):
        if not arq.endswith(".json") or arq.startswith("_"):
            continue
        d = json.load(open(f"{AQUI}/saida/{arq}"))
        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
        for r in lista:
            if isinstance(r, dict) and r.get("id"):
                por_id[r["id"]].append(r)
    return por_id


def ids_citados(reg):
    """Todo id `wb:` que este registro cita em requires, grants ou progressao."""
    achados = []

    def anda(v):
        if isinstance(v, str):
            if v.startswith("wb:") and not v.startswith("wb:text/"):
                achados.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                anda(x)
        elif isinstance(v, list):
            for x in v:
                anda(x)

    for campo in ("requires", "grants", "progressao"):
        anda(reg.get(campo))
    return achados


def main():
    base = json.load(open(f"{BASE}/index.json"))
    ids = {r["id"] for r in base}
    r = Resultado()

    # --- 1. prov para todo campo preenchido, sem valor fora do vocabulario --
    sem_prov = []
    for reg in base:
        prov = reg.get("prov") or {}
        for campo, valor in reg.items():
            if campo in ("id", "kind", "prov", "xref", "conflitos", "_origem",
                         "aliases_traits", "desmembrado_de", "historico",
                         "fusao_vetada") or comum.vazio(valor):
                continue
            p = prov.get(campo)
            if not p or not comum.prov_valido(p):
                sem_prov.append(f"`{reg['id']}` campo `{campo}` prov={p!r}")
    r.portao(1, "prov por campo, vocabulario fechado", not sem_prov,
             f"{len(sem_prov)} campos preenchidos sem prov valido", sem_prov)

    # --- 2. level/rank divergente entre fontes sem conflito registrado ------
    pre = carregar_saida()
    por_id = {reg["id"]: reg for reg in base}
    silenciados = []
    for ident, grupo in pre.items():
        if len(grupo) < 2 or ident not in por_id:
            continue
        for campo in ("level", "rank"):
            vals = {json.dumps(g.get(campo)) for g in grupo if g.get(campo) is not None}
            if len(vals) > 1:
                confs = por_id[ident].get("conflitos") or []
                if not any(c.get("campo") == campo for c in confs):
                    silenciados.append(f"`{ident}` {campo}: {sorted(vals)} sem conflito")
    # invariante do espelho: em spell, `level` e copia de `rank`. Sem isto os
    # dois se soltam com o tempo e o filtro do cliente passa a mentir.
    espelho = [f"`{reg['id']}` rank={reg.get('rank')} level={reg.get('level')}"
               for reg in base
               if reg.get("kind") == "spell" and reg.get("rank") is not None
               and reg.get("level") != reg.get("rank")]
    silenciados += espelho
    r.portao(2, "level/rank divergente sem conflito, e espelho rank==level em spell",
             not silenciados,
             f"{len(silenciados) - len(espelho)} divergencias silenciadas, "
             f"{len(espelho)} spells com espelho quebrado", silenciados)

    # --- 3. referencia wb: quebrada ---------------------------------------
    #
    # Excecao declarada, no mesmo espirito da tolerancia do portao 9: id sem
    # sucessor conhecido, com o motivo escrito em aliases_referencias.json,
    # nao falha o build -- mas continua listado. Portao que falha para sempre
    # vira ruido e para de ser lido.
    declaradas = {}
    curado = f"{AQUI}/aliases_referencias.json"
    if os.path.exists(curado):
        with open(curado) as fh:
            declaradas = (json.load(fh).get("sem_sucessor_conhecido") or {})

    quebradas = collections.Counter()
    onde = {}
    for reg in base:
        for alvo in ids_citados(reg):
            if alvo not in ids:
                quebradas[alvo] += 1
                onde.setdefault(alvo, reg["id"])
    inesperadas = {k: v for k, v in quebradas.items() if k not in declaradas}
    r.portao(3, "requires/grants/progressao citando id inexistente", not inesperadas,
             f"{sum(inesperadas.values())} citacoes para {len(inesperadas)} ids "
             f"inexistentes nao declarados; {len(quebradas) - len(inesperadas)} "
             f"declarados sem sucessor conhecido",
             [f"`{k}` ({v}x, ex. em `{onde[k]}`)" for k, v in quebradas.most_common(25)]
             + [f"declarado: `{k}` -- {v}" for k, v in declaradas.items()])

    # --- 4. cobertura contra o build anterior ------------------------------
    atual = collections.Counter(reg.get("kind") for reg in base)
    hist = f"{BASE}/cobertura_anterior.json"
    quedas = []
    if os.path.exists(hist):
        anterior = json.load(open(hist))
        for kind, n in anterior.items():
            if atual.get(kind, 0) < n:
                quedas.append(f"`{kind}`: {n} -> {atual.get(kind, 0)}")
    r.portao(4, "queda de cobertura contra o build anterior", not quedas,
             ("sem build anterior registrado" if not os.path.exists(hist)
              else f"{len(quedas)} kinds encolheram"), quedas)
    # Gravar a baseline mesmo quando o portao falha rebaixa a linha de
    # comparacao: a regressao seria acusada uma vez e nunca mais.
    if not quedas:
        with open(hist, "w") as fh:
            json.dump(dict(atual), fh, indent=1)

    # --- 5. license ausente ou xref vazio ----------------------------------
    ruins = []
    for reg in base:
        if not (reg.get("source") or {}).get("license"):
            ruins.append(f"`{reg['id']}` sem license")
        if not (reg.get("xref") or {}):
            ruins.append(f"`{reg['id']}` sem xref -- nenhuma fonte identificavel")
    r.portao(5, "license presente e xref nao vazio", not ruins,
             f"{len(ruins)} registros", ruins)

    # --- 6. traits categoricamente disjuntos sobrando pos-uniao -------------
    #
    # A entrada SEMPRE tem o par disjunto -- e por isso que a colisao existe.
    # O que interessa e se ela sobreviveu: o portao so falha quando o id
    # continuou unico, ou seja, quando o desmembramento nao separou as duas
    # entidades.
    resolvidos = {reg.get("desmembrado_de") for reg in base if reg.get("desmembrado_de")}
    disjuntos, ja_tratados = [], []
    for ident, grupo in pre.items():
        if len(grupo) < 2:
            continue
        for i, a in enumerate(grupo):
            for b in grupo[i + 1:]:
                if not comum.traits_disjuntos(a.get("traits"), b.get("traits")):
                    continue
                linha = (f"`{ident}`: {sorted(a.get('traits') or [])} x "
                         f"{sorted(b.get('traits') or [])}")
                (ja_tratados if ident in resolvidos else disjuntos).append(linha)
    # Segundo sinal, para a colisao que os traits nao denunciam: salto grande
    # de `level` entre fontes. `Efficient Alchemy` (nv4, arquetipo) e
    # `Efficient Alchemy (Paragon)` (nv20) tem o MESMO trait `alchemist`, e a
    # quimera so aparece aqui. Restrito a kind de escolha (feat, class-feature,
    # archetype): em equipment, level 0 contra level 8 e materia-prima contra
    # variante do mesmo material, ja verificado como legitimo.
    KINDS_DE_ESCOLHA = {"feat", "class-feature", "archetype", "heritage"}
    saltos = []
    for reg in base:
        if reg.get("kind") not in KINDS_DE_ESCOLHA or reg.get("desmembrado_de"):
            continue
        for c in (reg.get("conflitos") or []):
            if c.get("campo") != "level":
                continue
            vals = [v for k, v in c.items()
                    if k not in ("campo", "escolhido") and isinstance(v, int)]
            if len(vals) >= 2 and max(vals) - min(vals) >= 8:
                saltos.append(f"`{reg['id']}` level {sorted(vals)} -- "
                              f"suspeita de duas entidades no mesmo id")
    r.portao(6, "traits disjuntos ou salto de level sobrando depois da uniao",
             not disjuntos and not saltos,
             f"{len(disjuntos)} grupos ainda fundidos num id so; "
             f"{len(saltos)} com salto de level >= 8 em kind de escolha; "
             f"{len(ja_tratados)} ja desmembrados",
             disjuntos + saltos + ja_tratados)

    # --- 7. confere que o desmembramento rodou antes da fusao --------------
    rel = f"{BASE}/relatorio_reconciliacao.md"
    rodou = os.path.exists(rel) and "Colisoes de identidade" in open(rel).read()
    desmembrados = sum(1 for reg in base if reg.get("desmembrado_de"))
    # A condicao e `rodou`, nao `os.path.exists(rel)`: reconciliar SEMPRE
    # escreve esse arquivo, entao checar a existencia era um portao que nunca
    # podia falhar -- o mesmo defeito do portao 7 da v1, de novo.
    r.portao(7, "deteccao de colisao de identidade rodou antes da fusao (em reconciliar.py)",
             rodou,
             f"{desmembrados} registros marcados com `desmembrado_de`"
             + ("" if rodou else " -- relatorio sem secao de colisoes"))

    # --- 8. kind grande com 2+ fontes e zero conflitos ----------------------
    mudos = []
    por_kind = collections.defaultdict(lambda: [0, 0])
    for reg in base:
        fontes = [k for k in (reg.get("xref") or {}) if k in ("aon", "foundry", "pf2etools")]
        if len(fontes) >= 2:
            por_kind[reg["kind"]][0] += 1
            # `traits` saiu da precedencia e nao produz mais conflito; contar
            # conflito de traits fazia `shield` passar com 47 conflitos que
            # eram 100% ruido de trait.
            if any(c.get("campo") != "traits" for c in (reg.get("conflitos") or [])):
                por_kind[reg["kind"]][1] += 1
    # Piso de 20, nao de 100: com 100, tres dos seis kinds que a auditoria
    # provou silenciados continuariam passando -- `ancestry` (50 registros com
    # 2+ fontes e 3 divergencias reais de source.book), `class` (27 / 2) e
    # `familiar-ability` (72).
    concordam = []
    for kind, (multi, com_conf) in sorted(por_kind.items()):
        if multi < 20 or com_conf:
            continue
        if kind in CONCORDANCIA_VERIFICADA:
            concordam.append(f"`{kind}`: 0 conflitos -- {CONCORDANCIA_VERIFICADA[kind]}")
        else:
            mudos.append(f"`{kind}`: {multi} registros com 2+ fontes, 0 conflitos")
    r.portao(8, "kind com 2+ fontes e zero divergencia registrada", not mudos,
             f"{len(mudos)} kinds sem instrumentacao de conflito, "
             f"{len(concordam)} com concordancia verificada", mudos + concordam)

    # --- 9. contagem por kind contra o censo do AoN ------------------------
    #
    # Iterar sobre CENSO (allow-list escrita a mao) deixava o portao cego para
    # exatamente o que ele existe para achar: kind que ninguem lembrou de
    # listar. A varredura agora parte das CATEGORIAS DO CENSO, e categoria sem
    # kind mapeado vira aviso no relatorio em vez de silencio.
    censo_arq = f"{BRUTOS}/aon_censo.json"
    faltas, notas, sem_mapa = [], [], []
    if os.path.exists(censo_arq):
        with open(censo_arq) as fh:
            censo = json.load(fh)
        cat_para_kind = {cat: kind for kind, (cat, _, _) in CENSO.items()}
        # categoria do AoN -> kinds da base que a cobrem juntos
        SOMA = {"equipment": ["equipment", "weapon", "armor", "shield"]}
        for cat, alvo in sorted(censo.items(), key=lambda kv: -kv[1]):
            kind = cat_para_kind.get(cat)
            if kind is None:
                if cat in FORA_DE_ESCOPO or alvo < 20:
                    continue
                if cat in CATEGORIA_COBERTA:
                    notas.append(f"`{cat}` ({alvo}) coberta por {CATEGORIA_COBERTA[cat]}")
                    continue
                sem_mapa.append(f"`{cat}` ({alvo} docs vigentes) sem kind mapeado "
                                "-- decidir se entra no escopo ou vai para FORA_DE_ESCOPO")
                continue
            _, tol, motivo = CENSO[kind]
            tem = sum(atual.get(k, 0) for k in SOMA.get(cat, [kind]))
            piso = alvo * (1 - tol)
            linha = f"`{kind}`: base {tem} / censo {alvo}"
            if tem < piso:
                faltas.append(linha + f" -- abaixo do piso ({piso:.0f})"
                              + (f" [tolerancia: {motivo}]" if motivo else ""))
            else:
                notas.append(linha + (f" [tolerancia {tol:.0%}: {motivo}]" if motivo else ""))
    else:
        notas.append("censo ausente -- rode dados_brutos/_dump_aon_extras.py")
    r.portao(9, "cobertura por kind contra o censo do AoN",
             not faltas and not sem_mapa,
             f"{len(faltas)} kinds abaixo do piso, "
             f"{len(sem_mapa)} categorias do censo sem kind mapeado",
             faltas + sem_mapa + notas)

    # --- 10. prosa: todo registro emitido tem `text` ----------------------
    #
    # A spec promete isso e nenhum portao cobria -- justificativa em documento
    # sem portao e regressao futura de graca.
    sem_texto = collections.Counter(reg.get("kind") for reg in base if not reg.get("text"))
    fora = {k: n for k, n in sem_texto.items() if k not in ISENTOS_DE_PROSA}
    r.portao(10, "todo registro emitido tem prosa", not fora,
             f"{sum(sem_texto.values())} registros sem `text` "
             f"({sum(fora.values())} em kind nao isento)",
             [f"`{k}`: {n}" for k, n in sorted(sem_texto.items())]
             + [f"isencao declarada: `{k}` -- {v}" for k, v in ISENTOS_DE_PROSA.items()])

    cab = ["# Portoes de qualidade", "",
           f"Base: **{len(base)}** registros, {len(atual)} kinds.",
           "Todos os portoes sao reportados, inclusive os que passam --",
           "portao ausente e portao aprovado nao podem parecer a mesma coisa.", ""]
    open(f"{BASE}/relatorio_portoes.md", "w").write("\n".join(cab + r.linhas) + "\n")
    print(f"\n-> base/relatorio_portoes.md  ({'FALHOU' if r.falhou else 'todos passaram'})")
    return 1 if r.falhou else 0


if __name__ == "__main__":
    sys.exit(main())
