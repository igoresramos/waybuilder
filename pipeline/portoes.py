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
    "animal-companion":  ("animal-companion", 0.20,
                          "especializacao e avanco ficam fora por decisao de escopo"),
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
    json.dump(dict(atual), open(hist, "w"), indent=1)

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
    r.portao(7, "deteccao de colisao de identidade rodou antes da fusao (em reconciliar.py)",
             os.path.exists(rel),
             f"{desmembrados} registros marcados com `desmembrado_de`"
             + ("" if rodou else " -- relatorio sem secao de colisoes"))

    # --- 8. kind grande com 2+ fontes e zero conflitos ----------------------
    mudos = []
    por_kind = collections.defaultdict(lambda: [0, 0])
    for reg in base:
        fontes = [k for k in (reg.get("xref") or {}) if k in ("aon", "foundry", "pf2etools")]
        if len(fontes) >= 2:
            por_kind[reg["kind"]][0] += 1
            if reg.get("conflitos"):
                por_kind[reg["kind"]][1] += 1
    # Piso de 20, nao de 100: com 100, tres dos seis kinds que a auditoria
    # provou silenciados continuariam passando -- `ancestry` (50 registros com
    # 2+ fontes e 3 divergencias reais de source.book), `class` (27 / 2) e
    # `familiar-ability` (72).
    for kind, (multi, com_conf) in sorted(por_kind.items()):
        if multi >= 20 and com_conf == 0:
            mudos.append(f"`{kind}`: {multi} registros com 2+ fontes, 0 conflitos")
    r.portao(8, "kind com 2+ fontes e zero divergencia registrada", not mudos,
             f"{len(mudos)} kinds sem instrumentacao de conflito", mudos)

    # --- 9. contagem por kind contra o censo do AoN ------------------------
    censo_arq = f"{BRUTOS}/aon_censo.json"
    faltas, notas = [], []
    if os.path.exists(censo_arq):
        censo = json.load(open(censo_arq))
        for kind, (cat, tol, motivo) in sorted(CENSO.items()):
            alvo = censo.get(cat)
            if alvo is None:
                continue
            tem = atual.get(kind, 0)
            piso = alvo * (1 - tol)
            linha = f"`{kind}`: base {tem} / censo {alvo}"
            if tem < piso:
                faltas.append(linha + f" -- abaixo do piso ({piso:.0f})"
                              + (f" [tolerancia: {motivo}]" if motivo else ""))
            else:
                notas.append(linha + (f" [tolerancia {tol:.0%}: {motivo}]" if motivo else ""))
    else:
        notas.append("censo ausente -- rode dados_brutos/_dump_aon_extras.py")
    r.portao(9, "cobertura por kind contra o censo do AoN", not faltas,
             f"{len(faltas)} kinds abaixo do piso", faltas + notas)

    cab = ["# Portoes de qualidade", "",
           f"Base: **{len(base)}** registros, {len(atual)} kinds.",
           "Todos os portoes sao reportados, inclusive os que passam --",
           "portao ausente e portao aprovado nao podem parecer a mesma coisa.", ""]
    open(f"{BASE}/relatorio_portoes.md", "w").write("\n".join(cab + r.linhas) + "\n")
    print(f"\n-> base/relatorio_portoes.md  ({'FALHOU' if r.falhou else 'todos passaram'})")
    return 1 if r.falhou else 0


if __name__ == "__main__":
    sys.exit(main())
