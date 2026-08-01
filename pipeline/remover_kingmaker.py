#!/usr/bin/env python3
"""
Remove o conteudo de Kingmaker da base -- a UNICA excecao ao principio 4.

O principio 4 do README ("nada e descartado") continua valendo para todo o
resto. Aqui o dono do projeto pediu a remocao nominalmente, por escrito
(Igor, 2026-08-01): a mesa nao usa as regras de reino, e o conteudo produzia
CANDIDATO FALSO em slot de escolha -- medido em 33 das 34 fixtures do motor,
1.142 ocorrencias, sempre em `candidatos` de slot de feat
(`wb:feat/kingdom-assurance` oferecido como `general_feat@1` a um Guerreiro 4).

ANTES de "consertar" a falta de 125 registros na base, leia
`specs/2026-08-01-remover-kingmaker.md`, secao 1: ela explica por que esta
excecao nao se estende a mais nada -- conteudo legado, cortado pela Paizo, raro
ou de outro Adventure Path CONTINUA ficando (Shining Kingdoms 166,
`King of the Mountain` 24, `Crown of the Kobold King` 16, nenhum alcancado
aqui). Desligar este passo e apagar uma linha do build.sh; e reversivel de
proposito, mas exige a mesma coisa que ligou: decisao escrita do Igor.

CRITERIO: `source.book` canonizado, em LISTA FECHADA de tres livros. Nao e
`"kingmaker" in book.lower()` -- a substring erra em silencio (um
`Kingmaker: Companion Guide` futuro nao casaria com a lista, mas a guarda
abaixo o pega e ABORTA; ja a substring engoliria qualquer livro novo com
"kingmaker" no nome sem ninguem ver). O trait `kingmaker` NAO EXISTE na base
(0 de 438 traits distintos), entao nao ha segundo criterio: filtrar tambem por
trait seria uma regra que nunca dispara dando impressao de cobertura.

TRES GUARDAS, todas ANTES de escrever qualquer arquivo:
  1. livro que CONTEM `kingmaker` e nao esta na lista fechada -> aborta;
  2. contagem != ESPERADO (total, por kind, por livro) -> aborta, com o diff
     nominal contra a lista do relatorio anterior;
  3. referencia orfa: contagem de orfas (semantica do portao 3, id + alias)
     nao pode subir. Contar orfa cobre o caso que a busca por id nao cobre --
     registro removido que emprestava um `alias` para a referencia de um
     sobrevivente resolver.

Entrada: pipeline/base/index.json, pipeline/base/text/*.json
Saida:   os dois reescritos, mais
         base/relatorio_kingmaker.md         (a lista NOMINAL do que saiu)
         base/_kingmaker_ausencias.json      (fragmento para censo_ausencias.json)

Spec: specs/2026-08-01-remover-kingmaker.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comum                                            # noqa: E402
BASE = f"{AQUI}/base"

# Lista FECHADA, na grafia canonica que `reconciliar.py` emite via
# `canonico_livros.json`. Por isso este passo roda depois dele -- ver build.sh.
LIVROS = {
    "kingmaker adventure path",
    "kingmaker companion guide",
    "pathfinder kingmaker",
}

# Medido em 2026-08-01 sobre uma base de 20.086 registros. Divergencia nao e
# ruido: significa que alguma coisa a montante mudou (re-extracao, fusao nova,
# desmembramento novo) e merece olho humano. Atualizar e uma linha aqui e uma na
# spec, e o commit que atualiza carrega o motivo.
ESPERADO = 125
ESPERADO_POR_KIND = {"feat": 31, "trait": 31, "equipment": 23, "skill": 16,
                     "spell": 10, "background": 7, "weapon": 6, "ritual": 1}
ESPERADO_POR_LIVRO = {"kingmaker adventure path": 80,
                      "kingmaker companion guide": 41,
                      "pathfinder kingmaker": 4}

# Vocabulario GENERICO do PF2e que o AoN atribui a Kingmaker porque o hardcover
# reimprime o glossario de traits e o dump registra a pagina do hardcover como
# fonte unica. Saem junto, de proposito (spec, secao 3): uso medido hoje e zero
# para tres deles, e os 2 usos de `tech` sao duas armas do proprio Kingmaker.
# Se um dia entrar extrator de criatura ou de perigo, o caminho e re-emiti-los
# pela fonte real (Monster Core / GM Core), NAO desligar este passo.
VOCABULARIO_GENERICO = {
    "wb:trait/shapechanger": "trait de criatura (Monster)",
    "wb:trait/wild-hunt": "trait de familia de criatura (Monster)",
    "wb:trait/weather": "trait de perigo ambiental (Hazard)",
    "wb:trait/tech": "trait de item tecnologico (Mechanics)",
}

MOTIVO_CENSO = (
    "Conteudo de Kingmaker, removido do escopo do construtor por decisao do "
    "Igor em 2026-08-01. Nao e lacuna de extracao: os registros ENTRARAM na "
    "base e foram removidos de proposito pelo passo "
    "`pipeline/remover_kingmaker.py` (build.sh 7h). Sao 125 registros dos "
    "livros `Kingmaker Adventure Path`, `Kingmaker Companion Guide` e "
    "`Pathfinder Kingmaker` -- a maquinaria de reino (16 pericias de reino, 31 "
    "traits de reino/exercito/assentamento, 17 Kingdom Feats) e o conteudo "
    "comum publicado nos mesmos livros (7 backgrounds, 14 feats, 23 "
    "equipamentos, 6 armas, 10 magias, 1 ritual). A mesa nao usa as regras de "
    "reino, e manter o conteudo produzia candidato falso em slot de escolha -- "
    "medido em 33 das 34 fixtures do motor. Esta e a UNICA excecao ao "
    "principio 4 do README (\"nada e descartado\") e ela nao se estende a mais "
    "nada: ver specs/2026-08-01-remover-kingmaker.md, secao 1."
)
DECISAO_CENSO = ("aceitar. Repor exigiria desligar o passo 7h do build.sh, nao "
                 "re-extrair -- o conteudo entra na base e e removido depois.")
SPEC = "specs/2026-08-01-remover-kingmaker.md"


def livro_de(registro):
    """`source.book` normalizado para comparacao com a lista fechada."""
    bruto = (registro.get("source") or {}).get("book")
    return comum.limpar_livro(bruto or "").lower().strip()


# ---------------------------------------------------------------------------
# guarda 3: referencia orfa
# ---------------------------------------------------------------------------

# Espelha `portoes.portao_3_requires` de proposito: as funcoes de varredura
# vivem ANINHADAS dentro dele e nao ha o que importar. Manter as duas em
# sincronia e barato; medir orfa por outra regra que a do portao seria pior --
# este passo passaria e o portao 3 reprovaria o build inteiro tres passos
# adiante, sem dizer que a causa foi aqui.
_IGNORAR = {"id", "text", "xref", "prov", "conflitos", "aliases", "historico"}
_TOLERADAS = {"wb:weapon/light-crossbow"}


def _refs(o):
    if isinstance(o, dict) and "nao_modelavel" in o:
        for k, v in o.items():
            if k != "nao_modelavel":
                yield from _refs(v)
        return
    if isinstance(o, str):
        if o.startswith("wb:") and not o.startswith("wb:text/") \
                and "?nao-resolvido" not in o:
            yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from _refs(v)
    elif isinstance(o, list):
        for x in o:
            yield from _refs(x)


def _norm_slug(s):
    return comum.normalizar(s).replace(" ", "-")


def orfas(registros):
    """(total de citacoes orfas, Counter por id citado) -- semantica do portao 3."""
    ids = {r["id"] for r in registros}
    alias = {}
    for r in registros:
        for a in (r.get("aliases") or []):
            alias[f"wb:{r['kind']}/{_norm_slug(a)}"] = r["id"]
    contagem = collections.Counter()
    for r in registros:
        for campo, valor in r.items():
            if campo in _IGNORAR:
                continue
            for ref in _refs(valor):
                if ref not in ids and ref not in alias and ref not in _TOLERADAS:
                    contagem[ref] += 1
    return sum(contagem.values()), contagem


def citacoes_a(registros, alvos):
    """Quem, entre os que ficam, cita id que sai. Esperado: nada."""
    achados = collections.Counter()
    for r in registros:
        for campo, valor in r.items():
            if campo in _IGNORAR:
                continue
            for ref in _refs(valor):
                if ref in alvos:
                    achados[f"{r['id']} -> {ref} (em `{campo}`)"] += 1
    return achados


# ---------------------------------------------------------------------------
# guarda 2: diff nominal contra a lista do relatorio anterior
# ---------------------------------------------------------------------------

_LINHA_ID = re.compile(r"^\|\s*`(wb:[^`]+)`\s*\|")


def ids_do_relatorio_anterior():
    """Os ids que a rodada anterior removeu, lidos do proprio relatorio.

    O relatorio e versionado, entao ele E o registro nominal do estado
    anterior -- nao ha artefato novo so para isto. Ausente ou ilegivel devolve
    None, e a guarda de contagem aborta com os numeros, sem o diff nominal.
    """
    caminho = f"{BASE}/relatorio_kingmaker.md"
    if not os.path.exists(caminho):
        return None
    ids = set()
    with open(caminho, encoding="utf-8") as fh:
        for linha in fh:
            m = _LINHA_ID.match(linha)
            if m:
                ids.add(m.group(1))
    return ids or None


def abortar(mensagem, detalhe=()):
    print(f"!! remover_kingmaker: {mensagem}", file=sys.stderr)
    for d in detalhe:
        print(f"   {d}", file=sys.stderr)
    print(f"   nada foi escrito. Ver {SPEC}.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# fragmento do portao 9
# ---------------------------------------------------------------------------

def fragmento_censo(base_antes, base_depois, alvos):
    """O que o portao 9 passa a acusar por causa desta remocao.

    DERIVADO DO CENSO, nao de `xref.aon`. Os dois conjuntos nao coincidem, e
    medi-los mostrou por que: 4 dos 125 nao tem `xref.aon`
    (`wb:feat/roll-with-it-kingmaker`, `wb:feat/the-harder-they-fall-kingmaker`,
    `wb:equipment/basic-ingredient`, `wb:equipment/special-ingredient`) e, na
    outra ponta, 3 docs do AoN que NAO sao xref de ninguem ficam descobertos
    quando o registro homonimo sai -- `equipment-1763-1558` (Energy-Absorbing),
    `equipment-1756-1553` (Giant-Killing) e `equipment-1750-1551` (Ring of the
    Tiger), graus de runa que o portao cobria por NOME. Emitir so os xrefs
    deixaria esses 3 quebrando o build.

    A medida e a mesma do portao: ausencia = doc vigente do censo que nenhum
    registro cita por id nem cobre por nome. Roda a medicao duas vezes, antes e
    depois, e o fragmento e a DIFERENCA -- ausencia que ja existia nao e desta
    remocao e continua sendo problema de quem a criou.

    `ids_aceitos` leva a UNIAO com os `xref.aon` dos 125, e nao so a diferenca,
    pela mesma razao que o verbete `action` registra 70 ids para 44 ausencias:
    os que hoje nao aparecem estao mascarados por colisao de nome, e registrar
    so os visiveis os deixa quebrando o build no dia em que a colisao mudar.
    """
    import portoes                                      # noqa: E402

    censo = portoes.censo_aon()
    if not censo:
        return None, ["sem dump do AoN em disco -- fragmento NAO emitido "
                      "(o portao 9 tambem fica NAO MEDIDO nesse estado)"]

    def ausentes(registros):
        citados = set()
        for r in registros:
            xr = r.get("xref") or {}
            for chave in ("aon", "legado_aon"):
                if xr.get(chave):
                    citados.add(str(xr[chave]))
        nomes = {portoes.norm(r.get("name")) for r in registros if r.get("name")}
        fora = {}
        for cat in censo:
            if cat in portoes.FORA_DE_ESCOPO:
                continue
            faltando = {i: n for i, n in censo[cat].items()
                        if i not in citados and portoes.norm(n) not in nomes}
            if faltando:
                fora[cat] = faltando
        return fora

    antes, depois = ausentes(base_antes), ausentes(base_depois)
    novas = {}
    for cat, faltando in depois.items():
        delta = {i: n for i, n in faltando.items() if i not in antes.get(cat, {})}
        if delta:
            novas[cat] = delta

    cat_de_id = {i: cat for cat, docs in censo.items() for i in docs}
    xrefs_por_cat = collections.defaultdict(set)
    xrefs_sem_categoria = []
    for r in alvos:
        aon = (r.get("xref") or {}).get("aon")
        if not aon:
            continue
        cat = cat_de_id.get(str(aon))
        if cat:
            xrefs_por_cat[cat].add(str(aon))
        else:
            # doc legado (declara `remaster_id`) ou categoria fora de escopo:
            # nao entra no censo, entao nunca vira ausencia.
            xrefs_sem_categoria.append(f"{r['id']} -> {aon}")

    # Categoria que o censo curado JA conhece tem de ser fundida por UNIAO, e
    # nao substituida. Medido: `feat` ja carrega 5 ausencias decididas de outro
    # assunto -- trocar o verbete inteiro pelo daqui as deixa sem decisao e o
    # portao 9 continua VERMELHO (simulado: 1 categoria sem decisao, 5 ids).
    # Este e um passo humano, e um passo humano sem aviso e um passo errado.
    ja_curadas = {}
    curado = f"{AQUI}/censo_ausencias.json"
    if os.path.exists(curado):
        with open(curado, encoding="utf-8") as fh:
            ja_curadas = json.load(fh).get("ausencias") or {}

    ausencias = {}
    for cat in sorted(set(novas) | set(xrefs_por_cat)):
        visiveis = novas.get(cat, {})
        ids_aceitos = sorted(set(visiveis) | xrefs_por_cat.get(cat, set()))
        verbete = {
            "motivo": MOTIVO_CENSO,
            "decisao": DECISAO_CENSO,
            "quantos": len(visiveis),
            "spec": SPEC,
            "ids_aceitos": ids_aceitos,
        }
        if cat in ja_curadas:
            n_existentes = len(ja_curadas[cat].get("ids_aceitos") or [])
            verbete["_fundir"] = (
                f"`{cat}` JA EXISTE em pipeline/censo_ausencias.json com "
                f"{n_existentes} id(s) aceito(s) por outro motivo. FUNDIR POR "
                f"UNIAO: acrescentar estes ids aos que ja estao la e juntar os "
                f"dois motivos. SUBSTITUIR o verbete deixa as ausencias "
                f"antigas sem decisao e o portao 9 segue vermelho.")
        if len(ids_aceitos) > len(visiveis):
            verbete["nota_ids_aceitos"] = (
                f"a lista tem {len(ids_aceitos)} ids e nao {len(visiveis)}: os "
                f"demais sao docs do AoN dos mesmos registros removidos que "
                f"HOJE nao aparecem como ausentes por colisao de nome com "
                f"registro que fica. A decisao e a mesma para todos; registrar "
                f"so os visiveis os deixa quebrando o build no dia em que a "
                f"colisao mudar.")
        if cat in novas:
            verbete["por_id"] = {i: novas[cat][i] for i in sorted(novas[cat])}
        ausencias[cat] = verbete

    resumo = [f"{cat}: {v['quantos']} ausencia(s), "
              f"{len(v['ids_aceitos'])} id(s) aceito(s)"
              + ("  <- FUNDIR POR UNIAO: a categoria ja existe no censo curado"
                 if "_fundir" in v else "")
              for cat, v in sorted(ausencias.items())]
    if xrefs_sem_categoria:
        resumo.append(f"{len(xrefs_sem_categoria)} xref(s) fora do censo "
                      f"(doc legado ou categoria fora de escopo): "
                      f"{', '.join(xrefs_sem_categoria[:5])}")
    return {
        "_doc": ("Fragmento para fundir em pipeline/censo_ausencias.json, sob "
                 "`ausencias`. GERADO por pipeline/remover_kingmaker.py -- a "
                 "fusao e feita uma vez, por gente, e o censo continua curado. "
                 "Categoria com `_fundir` JA existe la: unir os `ids_aceitos`, "
                 "nunca substituir o verbete."),
        "_derivacao": ("diferenca entre as ausencias do portao 9 medidas ANTES "
                       "e DEPOIS da remocao, com a mesma funcao do portao "
                       "(`portoes.censo_aon`). Nao vem de `xref.aon`: 4 dos 125 "
                       "nao tem xref e 3 docs de grau do AoN so eram cobertos "
                       "por nome."),
        "ausencias": ausencias,
    }, resumo


# ---------------------------------------------------------------------------

def relatorio(alvos, por_kind, por_livro, orfas_antes, orfas_depois,
              textos_removidos, resumo_censo):
    linhas = [
        "# Remocao do conteudo de Kingmaker",
        "",
        f"Removidos: **{len(alvos)}** registros. Criterio: `source.book` na "
        "lista fechada de tres livros de Kingmaker.",
        "",
        "Decisao do Igor em 2026-08-01, UNICA excecao ao principio 4 do README "
        f"(\"nada e descartado\"). Ver `{SPEC}` antes de reverter.",
        "",
        "Este relatorio existe porque **contagem sozinha nao prova nada**: 125 "
        "remocoes ERRADAS tambem batem 125. A lista abaixo e nominal.",
        "",
        f"- por kind: {dict(sorted(por_kind.items()))}",
        f"- por livro: {dict(sorted(por_livro.items()))}",
        f"- entradas de prosa removidas de `base/text/*.json`: "
        f"**{textos_removidos}**",
        f"- citacoes orfas (semantica do portao 3): {orfas_antes} antes, "
        f"{orfas_depois} depois",
        "",
    ]

    if resumo_censo:
        linhas += ["## Efeito no portao 9 (censo do AoN)", ""]
        linhas += [f"- {r}" for r in resumo_censo]
        linhas += ["", "Fragmento pronto em `base/_kingmaker_ausencias.json` "
                   "-- fundir a mao em `pipeline/censo_ausencias.json`.", ""]

    saiu = {r["id"] for r in alvos}
    generico = [(i, m) for i, m in sorted(VOCABULARIO_GENERICO.items()) if i in saiu]
    if generico:
        linhas += [
            "## Vocabulario generico que sai junto (spec, secao 3)", "",
            "O AoN atribui estes traits a Kingmaker porque o hardcover "
            "reimprime o glossario e o dump registra a pagina do hardcover "
            "como fonte unica. Nao ha segunda entrada para canonizar. Uso "
            "medido antes da remocao: zero, exceto `tech`, usado so pelas duas "
            "armas de Kingmaker removidas no mesmo ato.", "",
            "| id | o que e |", "|---|---|",
        ]
        linhas += [f"| `{i}` | {m} |" for i, m in generico]
        linhas.append("")
    ausentes = sorted(set(VOCABULARIO_GENERICO) - saiu)
    if ausentes:
        linhas += [f"> AVISO: `{i}` esta na lista de vocabulario generico da "
                   f"spec mas NAO saiu nesta rodada -- o criterio por livro "
                   f"deixou de alcanca-lo." for i in ausentes] + [""]

    for kind in sorted(por_kind):
        do_kind = sorted((r for r in alvos if r.get("kind") == kind),
                         key=lambda r: r["id"])
        linhas += [f"## {kind} ({len(do_kind)})", "",
                   "| id | nome | livro | pag. | doc do AoN |",
                   "|---|---|---|---|---|"]
        for r in do_kind:
            fonte = r.get("source") or {}
            aon = (r.get("xref") or {}).get("aon") or "--"
            pagina = fonte.get("page")
            linhas.append(f"| `{r['id']}` | {r.get('name')} | "
                          f"{fonte.get('book')} | {pagina if pagina is not None else '--'} | "
                          f"{aon} |")
        linhas.append("")
    return "\n".join(linhas) + "\n"


def main():
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        registros = json.load(fh)

    # guarda 1 -- livro que CONTEM "kingmaker" e nao esta na lista fechada.
    # Mesmo desenho de `aplicar_curadoria.py`: falhar alto em vez de decidir
    # sozinho. A lista fechada erra ALTO; a substring erraria em silencio.
    intrusos = collections.Counter(livro_de(r) for r in registros
                                   if "kingmaker" in comum.normalizar(livro_de(r))
                                   and livro_de(r) not in LIVROS)
    if intrusos:
        abortar("livro de Kingmaker fora da lista fechada -- decida a mao",
                [f"{livro!r}: {n} registro(s)" for livro, n in intrusos.most_common()]
                + [f"lista fechada atual: {sorted(LIVROS)}"])

    alvos = [r for r in registros if livro_de(r) in LIVROS]
    ids_alvo = {r["id"] for r in alvos}
    por_kind = collections.Counter(r.get("kind") for r in alvos)
    por_livro = collections.Counter(livro_de(r) for r in alvos)

    # guarda 2 -- contagem, com diff NOMINAL contra a rodada anterior
    divergencias = []
    if len(alvos) != ESPERADO:
        divergencias.append(f"total: esperado {ESPERADO}, achado {len(alvos)}")
    if dict(por_kind) != ESPERADO_POR_KIND:
        divergencias.append(f"por kind: esperado {ESPERADO_POR_KIND}, "
                            f"achado {dict(sorted(por_kind.items()))}")
    if dict(por_livro) != ESPERADO_POR_LIVRO:
        divergencias.append(f"por livro: esperado {ESPERADO_POR_LIVRO}, "
                            f"achado {dict(sorted(por_livro.items()))}")
    if divergencias:
        anteriores = ids_do_relatorio_anterior()
        if anteriores is None:
            divergencias.append("sem relatorio anterior legivel -- diff nominal "
                                "indisponivel")
        else:
            apareceram = sorted(ids_alvo - anteriores)
            sumiram = sorted(anteriores - ids_alvo)
            divergencias.append(f"apareceram ({len(apareceram)}): "
                                f"{', '.join(apareceram) or '--'}")
            divergencias.append(f"sumiram ({len(sumiram)}): "
                                f"{', '.join(sumiram) or '--'}")
        abortar("a base mudou a montante: a contagem nao bate com o ESPERADO",
                divergencias + ["conferir o diff e atualizar ESPERADO aqui e na "
                                "spec, no mesmo commit e com o motivo"])

    sobreviventes = [r for r in registros if r["id"] not in ids_alvo]

    # guarda 3 -- referencia orfa. A spec mediu ZERO citacao de id de Kingmaker
    # por registro que fica; o passo NAO reaponta nada, e se um dia houver o que
    # reapontar ele tem de abortar, nunca decidir em silencio.
    citam = citacoes_a(sobreviventes, ids_alvo)
    orfas_antes, _ = orfas(registros)
    orfas_depois, novas_orfas = orfas(sobreviventes)
    if orfas_depois > orfas_antes:
        _, antigas = orfas(registros)
        cresceram = [f"{i}: {n}x (era {antigas.get(i, 0)}x)"
                     for i, n in novas_orfas.most_common()
                     if n > antigas.get(i, 0)]
        abortar(f"a remocao criaria referencia orfa "
                f"({orfas_antes} -> {orfas_depois})",
                cresceram[:20] + [
                    f"citacoes diretas a id removido: {sum(citam.values())}",
                    "reapontar em silencio nao e opcao (spec, secao 5 item 6): "
                    "decida a mao e registre na spec"])
    if citam:
        abortar("registro que FICA cita id que SAI -- o conjunto deixou de ser "
                "fechado", [f"{onde} ({n}x)" for onde, n in citam.most_common(20)])

    # prosa: `emitir_textos.py` roda no passo 5, muito antes. Sem esta limpeza a
    # prosa dos 125 fica orfa no repo para sempre, e NAO ha portao que pegue.
    chaves_por_kind = collections.defaultdict(set)
    sem_chave = []
    for r in alvos:
        chave = r.get("text")
        if isinstance(chave, str) and chave.startswith("wb:text/"):
            chaves_por_kind[r["kind"]].add(chave)
        else:
            sem_chave.append(r["id"])
    textos_removidos, faltaram = 0, []
    novos_stores = {}
    for kind, chaves in chaves_por_kind.items():
        caminho = f"{BASE}/text/{kind}.json"
        if not os.path.exists(caminho):
            faltaram += sorted(chaves)
            continue
        with open(caminho, encoding="utf-8") as fh:
            store = json.load(fh)
        for chave in sorted(chaves):
            if store.pop(chave, None) is None:
                faltaram.append(chave)
            else:
                textos_removidos += 1
        novos_stores[caminho] = store
    if faltaram:
        abortar("prosa que devia sair nao esta no store de texto -- "
                "`emitir_textos.py` mudou de contrato?",
                faltaram[:20] + [f"({len(faltaram)} no total)"])

    fragmento, resumo_censo = fragmento_censo(registros, sobreviventes, alvos)

    # so agora escreve: as tres guardas passaram
    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(sobreviventes, fh, ensure_ascii=False)
    for caminho, store in novos_stores.items():
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(store, fh, ensure_ascii=False, separators=(",", ":"))
    with open(f"{BASE}/relatorio_kingmaker.md", "w", encoding="utf-8") as fh:
        fh.write(relatorio(alvos, por_kind, por_livro, orfas_antes,
                           orfas_depois, textos_removidos, resumo_censo))
    if fragmento:
        with open(f"{BASE}/_kingmaker_ausencias.json", "w", encoding="utf-8") as fh:
            json.dump(fragmento, fh, ensure_ascii=False, indent=1)

    print(f"removidos: {len(alvos)} registros "
          f"({len(registros)} -> {len(sobreviventes)})")
    print(f"por kind: {dict(sorted(por_kind.items()))}")
    print(f"por livro: {dict(sorted(por_livro.items()))}")
    print(f"prosa removida de base/text/: {textos_removidos} entradas em "
          f"{len(novos_stores)} arquivo(s)")
    if sem_chave:
        print(f"sem chave de prosa: {len(sem_chave)} ({', '.join(sem_chave[:5])})")
    print(f"citacoes orfas: {orfas_antes} -> {orfas_depois}")
    for r in (resumo_censo or []):
        print(f"portao 9  {r}")
    print(f"-> {BASE}/relatorio_kingmaker.md")
    if fragmento:
        print(f"-> {BASE}/_kingmaker_ausencias.json  "
              f"(fundir a mao em pipeline/censo_ausencias.json)")


if __name__ == "__main__":
    main()
