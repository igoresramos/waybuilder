#!/usr/bin/env python3
"""
Os 7 portoes de qualidade da spec (specs/2026-07-26-schema-base.md).

Antes desta implementacao so o portao 5 existia, dentro do reconciliador, e o
portao 7 era **tautologico**: perguntava por nome duplicado no mesmo kind
*depois* de a fusao ter unido as duplicatas. Era exatamente a fresta por onde
`death-from-above` passou -- dois feats distintos virando um registro quimera.
Por isso o portao 7 roda na fase `pre-fusao`, nao no fim.

Fases:
  pre-fusao  base recem-reconciliada, antes de fundir_renomeados.py
  final      base pronta para emitir

Uso:
    python3 portoes.py --fase pre-fusao
    python3 portoes.py --fase final
    python3 portoes.py --fase final --gravar-cobertura   # fixa a linha de base

Saida: relatorio em base/relatorio_portoes.md, codigo 1 se algum portao falha.
"""
import json, os, re, sys, glob, collections, subprocess, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comum                                          # noqa: E402
RAIZ = os.path.dirname(AQUI)
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"
AON_DUMP = f"{BRUTOS}/aon_dump"
COBERTURA = f"{BASE}/_cobertura.json"

# Raizes que um script reconstroi a partir de um pin: buscar_fontes.sh traz o
# clone do Foundry, dump_aon.py traz o dump do AoN. Sumir daqui nao e perda.
# Qualquer outro caminho citado precisa existir -- ver portao 8.
RECONSTRUIVEL = ("pipeline/dados_brutos/foundry",
                 "pipeline/dados_brutos/aon",
                 "pipeline/dados_brutos/pf2etools")

# Campos cujo preenchimento exige `prov`. `mechanized`, `kind` e `id` sao
# derivados do proprio pipeline, nao vieram de fonte -- nao entram.
CAMPOS_COM_PROV = ["name", "level", "traits", "rarity", "source",
                   "requires", "grants", "text"]

# Sufixos de variante legitima: -greater/-major/-true sao itens distintos por
# design da Paizo, nao colisao de identidade. Falso positivo conhecido.
SUFIXO_VARIANTE = re.compile(
    r"-(greater|lesser|major|minor|true|moderate|supreme|standard"
    r"|mk-?\d+|type-?[ivx]+|\d+)$")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def preenchido(v):
    return v not in (None, "", [], {})


# ---------------------------------------------------------------------------
# Indices das fontes, para os portoes que precisam comparar valor por fonte
# ---------------------------------------------------------------------------

def indice_aon():
    """id do AoN -> registro. Usa o dump completo; sem ele, cai nos apelidos.

    `dump_aon.py` grava o dump por categoria em `aon_dump/` e copia cada
    categoria para `dados_brutos/aon_<apelido>.json`. So os apelidos ficam
    versionados -- entao numa maquina que nunca rodou o dump o indice vinha
    vazio e os portoes 2 e 7 se desligavam sozinhos, passando por ausencia de
    dado. Os apelidos cobrem os kinds de jogador e chegam para os dois.
    """
    arquivos = [f for f in glob.glob(f"{AON_DUMP}/*.json")
                if not os.path.basename(f).startswith("_")]
    if not arquivos:
        arquivos = sorted(glob.glob(f"{BRUTOS}/aon_*.json"))
    idx = {}
    for f in arquivos:
        try:
            docs = json.load(open(f))
        except Exception:
            continue
        if not isinstance(docs, list):
            continue                       # aon_censo.json e um mapa, nao docs
        for r in docs:
            if not isinstance(r, dict) or not r.get("id"):
                continue
            chave = str(r["id"])
            # o mesmo doc aparece em mais de um arquivo com recortes de campo
            # diferentes (a ponte remaster traz `category` e `trait`, o dump por
            # categoria traz `pfs` e `legacy_id`). Sobrescrever perderia campo,
            # entao completa em vez de trocar.
            anterior = idx.get(chave)
            if anterior:
                for k, v in anterior.items():
                    if r.get(k) in (None, "", [], {}):
                        r[k] = v
            idx[chave] = r
    return idx


def indice_foundry():
    """_id do Foundry -> registro, com cache em disco (28k arquivos)."""
    cache = f"{BRUTOS}/_idx_foundry_campos.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    raiz = comum.packs_foundry(BRUTOS)
    if not raiz:
        return {}
    idx = {}
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("_id"):
            continue
        sistema = d.get("system") or {}
        pub = sistema.get("publication") or sistema.get("source") or {}
        idx[d["_id"]] = {
            "name": d.get("name"),
            "level": (sistema.get("level") or {}).get("value"),
            "book": (pub.get("title") if isinstance(pub, dict) else None)
                    or (pub.get("value") if isinstance(pub, dict) else None),
            "rarity": (sistema.get("traits") or {}).get("rarity"),
        }
    json.dump(idx, open(cache, "w"), separators=(",", ":"))
    return idx


# ---------------------------------------------------------------------------
# Os portoes
# ---------------------------------------------------------------------------

def portao_1_prov(base, ctx):
    """Todo campo preenchido tem `prov`."""
    faltas = collections.Counter()
    exemplos = collections.defaultdict(list)
    for r in base:
        prov = r.get("prov") or {}
        for c in CAMPOS_COM_PROV:
            if preenchido(r.get(c)) and c not in prov:
                faltas[c] += 1
                if len(exemplos[c]) < 5:
                    exemplos[c].append(r["id"])
    return sum(faltas.values()), [
        f"`{c}`: {n} sem prov (ex.: {', '.join(exemplos[c])})"
        for c, n in faltas.most_common()]


def portao_2_level(base, ctx):
    """`level` divergente entre fontes sem entrada em `conflitos`."""
    aon, foundry = ctx["aon"], ctx["foundry"]
    if not aon and not foundry:
        return None, ["DESLIGADO: sem dump do AoN nem clone do Foundry em disco"]
    achados = []
    for r in base:
        if r.get("kind") == "class-feature":
            continue          # level de class-feature vive na progressao da classe
        xr = r.get("xref") or {}
        niveis = {}
        a = aon.get(str(xr.get("aon", "")))
        if a and a.get("level") is not None:
            niveis["aon"] = a["level"]
        fid = str(xr.get("foundry", "")).split(".")[-1]
        f = foundry.get(fid)
        if f and f.get("level") is not None:
            niveis["foundry"] = f["level"]
        if len(set(niveis.values())) > 1:
            ja = any(c.get("campo") == "level" for c in (r.get("conflitos") or []))
            if not ja:
                achados.append(f"`{r['id']}`: {niveis} sem conflito registrado")
    return len(achados), achados[:40]


def portao_3_requires(base, ctx):
    """Nenhum `requires` cita id `wb:` inexistente."""
    ids = {r["id"] for r in base}
    alias = {}
    for r in base:
        for a in (r.get("aliases") or []):
            alias[f"wb:{r['kind']}/{norm(a).replace(' ', '-')}"] = r["id"]

    def refs(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "has" and isinstance(v, str):
                    yield v
                else:
                    yield from refs(v)
        elif isinstance(o, list):
            for x in o:
                yield from refs(x)

    orfaos = collections.Counter()
    for r in base:
        for ref in refs(r.get("requires")):
            if ref.startswith("wb:") and ref not in ids and ref not in alias:
                orfaos[ref] += 1
    return sum(orfaos.values()), [f"`{i}` citado {n}x" for i, n in orfaos.most_common(30)]


def portao_4_cobertura(base, ctx):
    """Cobertura por kind nao cai em relacao ao build anterior."""
    if not os.path.exists(COBERTURA):
        return None, ["linha de base ausente -- grave com --gravar-cobertura"]
    ant = json.load(open(COBERTURA))
    atual = collections.Counter(r.get("kind") for r in base)
    quedas = []
    for kind, n in (ant.get("por_kind") or {}).items():
        if atual.get(kind, 0) < n:
            quedas.append(f"`{kind}`: {n} -> {atual.get(kind, 0)}")
    total_ant = ant.get("total", 0)
    if len(base) < total_ant:
        quedas.append(f"**total**: {total_ant} -> {len(base)}")
    return len(quedas), quedas


def portao_5_license(base, ctx):
    """Todo registro emitido tem `license`."""
    sem = [r["id"] for r in base if not (r.get("source") or {}).get("license")]
    return len(sem), [f"`{i}`" for i in sem[:30]]


def portao_6_traits(base, ctx):
    """Sobra `traits` categoricamente disjunto depois da uniao -- suspeita de colisao."""
    achados = []
    for r in base:
        for c in (r.get("conflitos") or []):
            if c.get("campo") != "traits":
                continue
            conjuntos = [set(v) for k, v in c.items()
                         if k not in ("campo", "escolhido") and isinstance(v, list)]
            # conjunto vazio e disjunto de tudo por vacuidade -- ausencia de
            # informacao, nao evidencia de que sao duas entidades
            conjuntos = [s for s in conjuntos if s]
            if len(conjuntos) >= 2 and not set.intersection(*conjuntos):
                achados.append(f"`{r['id']}`: {[sorted(s) for s in conjuntos]}")
    return len(achados), achados[:40]


def _grupos_de_identidade(docs):
    """Agrupa docs do AoN que sao o mesmo conteudo em edicoes diferentes.

    `remaster_id`/`legacy_id` ligam a versao legada a sua sucessora. Dois docs
    ligados assim nao sao ambiguidade -- sao o mesmo feat antes e depois do
    Remaster. O que sobra depois de agrupar e que e homonimo de verdade.
    """
    pai = {str(d.get("id")): str(d.get("id")) for d in docs}

    def raiz(x):
        while pai.get(x, x) != x:
            pai[x] = pai.get(pai[x], pai[x])
            x = pai[x]
        return x

    def unir(x, y):
        rx, ry = raiz(x), raiz(y)
        if rx != ry:
            pai[rx] = ry

    # dois docs que apontam para o MESMO alvo sao a mesma entidade, mesmo que o
    # alvo nao esteja no grupo: `Temporal Distortion` tem um doc em Divine
    # Mysteries e outro em Dark Archives (Remastered), e os dois declaram
    # `legacy_id: [spell-1195]` -- e a mesma magia reimpressa, nao duas.
    por_alvo = collections.defaultdict(list)
    for d in docs:
        i = str(d.get("id"))
        for chave in ("remaster_id", "legacy_id"):
            # o AoN emite esses campos como LISTA ('remaster_id': ['feat-4388']),
            # nao como escalar -- tratar como string casa zero pares
            alvo = d.get(chave)
            for a in (alvo if isinstance(alvo, list) else [alvo]):
                if a is None:
                    continue
                a = str(a)
                por_alvo[a].append(i)
                if a in pai:
                    unir(i, a)
    for irmaos in por_alvo.values():
        for outro in irmaos[1:]:
            unir(irmaos[0], outro)
    grupos = collections.defaultdict(list)
    for d in docs:
        grupos[raiz(str(d.get("id")))].append(d)
    return list(grupos.values())


def portao_7_homonimo(base, ctx):
    """Casamento ambiguo: a fonte tem N entidades para o nome que a base casou com 1.

    A versao anterior deste portao perguntava se dois registros da base tinham o
    mesmo nome no mesmo kind. Nunca disparava -- em nenhuma fase -- porque a
    ambiguidade nunca chega a produzir dois registros: o extrator casa por nome,
    escolhe **um** candidato entre os N da fonte, e os outros somem sem rastro.

    Medido em 2026-07-26: `Death from Above` tem 1 doc no Foundry (nivel 8,
    archetype) e 2 no AoN (feat-7610 archetype nivel 8; feat-7380 mitico nivel
    16). A base emitiu nivel 8 com traits `mythic` -- cruzou o Foundry com o
    doc errado do AoN e perdeu o outro feat inteiro. Idem `Reckless Abandon`,
    com 4 docs no AoN formando 2 pares legacy/remaster distintos.
    """
    aon = ctx["aon"]
    if not aon:
        return None, ["DESLIGADO: sem dump do AoN em disco (rode dump_aon.py)"]

    por_nome = collections.defaultdict(list)
    for d in aon.values():
        cat = str(d.get("category") or "")
        # doc que declara `remaster_id` e a versao LEGADO de outra coisa, nao
        # uma entidade a distinguir. Sem isto o portao acusa homonimo sempre
        # que o remaster renomeia: `Hellknight Dedication` (feat-1078, nv6) e
        # o legado de `Hellknight Preferment`, que ja esta na base com o nome
        # novo -- nada colidiu. Os dois `Death from Above` nao declaram
        # remaster_id nenhum, entao o caso real continua passando pelo filtro.
        if cat and not d.get("remaster_id"):
            por_nome[(cat, norm(d.get("name")))].append(d)

    # casos ja resolvidos por desmembrar_colisoes.py: o irmao existe, entao a
    # multiplicidade na fonte deixou de ser ambiguidade nao tratada
    ja_desmembrados = {r["desmembrado_de"] for r in base if r.get("desmembrado_de")}

    achados = []
    for r in base:
        if r.get("desmembrado_de") or r["id"] in ja_desmembrados:
            continue
        # class-feature e UM registro compartilhado por N classes, por decisao da
        # spec ("nivel de class-feature pertence a classe"). O AoN indexa um doc
        # por classe concedente -- `Alertness` tem 12 --, entao multiplicidade
        # ali e o modelo funcionando, nao colisao.
        if r.get("kind") == "class-feature":
            continue
        chave = (r.get("kind"), norm(r.get("name")))
        candidatos = por_nome.get(chave)
        if not candidatos or len(candidatos) < 2:
            continue
        grupos = _grupos_de_identidade(candidatos)
        if len(grupos) < 2:
            continue          # so pares legacy/remaster: fusao legitima
        slug = r["id"].split("/", 1)[-1]
        if SUFIXO_VARIANTE.search(slug):
            continue          # ja desmembrado com sufixo

        # Criterio da propria spec: "conflito com valores categoricamente
        # disjuntos nao e divergencia de fonte -- e sinal de que duas entidades
        # foram fundidas". Grupos que batem em level E traits sao a mesma coisa
        # em duas edicoes (par legacy/remaster que o AoN nao declarou); grupos
        # que divergem sao entidades diferentes disputando o mesmo slug.
        assinaturas = {(g[0].get("level"),
                        tuple(sorted(map(str, g[0].get("trait") or []))))
                       for g in grupos}
        casado = str((r.get("xref") or {}).get("aon") or "")
        resumo = "; ".join(
            f"{g[0].get('id')}(nv{g[0].get('level')},"
            f"{','.join(map(str, g[0].get('trait') or []))[:28]})"
            for g in grupos[:4])
        linha = (f"`{r['id']}` casou com `{casado or '-'}` mas o AoN tem "
                 f"{len(grupos)} entidades: {resumo}")
        if len(assinaturas) > 1:
            achados.append(("colisao", linha))
        else:
            achados.append(("par-nao-declarado", linha))

    graves = [l for t, l in achados if t == "colisao"]
    brandos = [l for t, l in achados if t == "par-nao-declarado"]
    detalhe = [f"**COLISAO** {l}" for l in graves[:40]]
    if brandos:
        detalhe.append(f"")
        detalhe.append(f"_Alem disso, {len(brandos)} casos de mesmo level e mesmos "
                       f"traits -- par legacy/remaster que o AoN nao declarou via "
                       f"`remaster_id`. Fusao legitima, nao bloqueia o build._")
        detalhe += [f"- {l}" for l in brandos[:15]]
    return len(graves), detalhe


def _arquivos_versionados():
    """Arquivos de texto versionados do projeto, sem os dumps de fonte.

    Os 3.610 arquivos sob dados_brutos/ sao dump de fonte -- varrer citacao
    dentro deles nao diz nada e custa caro.
    """
    r = subprocess.run(["git", "-C", RAIZ, "ls-files"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return [f for f in r.stdout.split()
            if f.endswith((".md", ".py", ".sh", ".json"))
            and "/dados_brutos/" not in f]


def portao_8_artefato_citado(base, ctx):
    """Caminho citado em documento versionado que nao existe no disco.

    O portao que faltava quando `dados_brutos/tabelas_conjuracao_pdf.json`
    sumiu. Aquele arquivo tinha as tabelas de conjuracao lidas dos PDFs
    oficiais -- o War of Immortals e imagem pura, entao as paginas foram
    renderizadas e lidas a olho, sem script que refaca. Ele nasceu em
    `dados_brutos/`, que o .gitignore exclui alegando "reconstruivel pelos
    pins": verdade para o clone do Foundry e o dump do AoN, falso para ele.
    Sumiu sem ruido, o TODO seguiu dizendo CONCLUIDO e o relatorio seguiu
    citando o caminho -- nada no build reclamou.

    Fonte bruta sob uma raiz reconstruivel nao entra: `buscar_fontes.sh` e
    `dump_aon.py` a trazem de volta. Todo o resto tem que existir.

    Perda ja conhecida vive em `artefatos_perdidos.json` com motivo e decisao;
    ela aparece no relatorio mas nao quebra o build. Perda NOVA quebra.
    """
    versionados = _arquivos_versionados()
    if versionados is None:
        return None, ["git indisponivel -- portao desligado"]

    pat_arquivo = re.compile(
        r"(?:pipeline|motor|docs|specs)/[A-Za-z0-9_./-]+\.[a-z]{2,6}")
    pat_diretorio = re.compile(
        r"(?:pipeline|motor|docs|specs)/[A-Za-z0-9_./-]+/")
    # LESSONS e LOG citam o diretorio de brutos sem o `pipeline/` na frente
    pat_solto = re.compile(r"(?<![A-Za-z0-9_/-])dados_brutos/[A-Za-z0-9_./-]+")

    citados = collections.defaultdict(set)
    for rel in versionados:
        try:
            txt = open(os.path.join(RAIZ, rel), encoding="utf-8",
                       errors="ignore").read()
        except OSError:
            continue
        curto = rel.split("waybuilder/")[-1]
        achados = set(pat_arquivo.findall(txt)) | set(pat_diretorio.findall(txt))
        achados |= {f"pipeline/{c}" for c in pat_solto.findall(txt)}
        for c in achados:
            c = c.rstrip(".")
            if not c.startswith(RECONSTRUIVEL):
                citados[c].add(curto)

    conhecidos = {}
    try:
        reg = json.load(open(f"{AQUI}/artefatos_perdidos.json"))
        conhecidos = {p["caminho"]: p for p in reg.get("perdidos", [])}
    except (OSError, ValueError, KeyError):
        pass

    novos, sabidos = [], []
    for c in sorted(citados):
        if os.path.exists(os.path.join(RAIZ, c)):
            continue
        onde = ", ".join(sorted(citados[c])[:3])
        # Subcaminho de um diretorio ja registrado herda o registro: perder
        # `pdfs/` perde `pdfs/PF2e/DM/` junto, e sao a mesma decisao.
        chave = next((k for k in conhecidos
                      if c == k or (k.endswith("/") and c.startswith(k))), None)
        if chave:
            k = conhecidos[chave]
            sabidos.append(f"`{c}` -- {k.get('decisao', '?')} "
                           f"(reproduzivel: {k.get('reproduzivel')})")
        else:
            novos.append(f"`{c}` citado em {onde} e **nao existe no disco**. "
                         f"Se foi derivado a mao, ele nunca deveria ter vivido "
                         f"fora de dados_derivados/; registre em "
                         f"artefatos_perdidos.json com motivo e decisao.")

    detalhe = novos[:30]
    if sabidos:
        detalhe.append("")
        detalhe.append(f"_Perdas ja registradas em `artefatos_perdidos.json` "
                       f"({len(sabidos)}) -- visiveis, nao bloqueiam:_")
        detalhe += [f"- {s}" for s in sabidos]
    return len(novos), detalhe


# ---------------------------------------------------------------------------
# Portao 9: censo do AoN por categoria -- o unico gabarito EXTERNO
# ---------------------------------------------------------------------------

# Categoria implicita de cada dump por apelido: os arquivos por categoria nao
# gravam o campo `category` (so a ponte remaster grava), entao sem isto 8.303
# docs caem num balde sem categoria e o censo mede errado.
CENSO_APELIDO = {
    "aon_feats.json": "feat", "aon_spells.json": "spell",
    "aon_traits.json": "trait", "aon_deities.json": "deity",
    "aon_domains.json": "domain", "aon_skills.json": "skill",
    "aon_archetypes.json": "archetype", "aon_ancestries.json": "ancestry",
    "aon_heritages.json": "heritage", "aon_backgrounds.json": "background",
    "aon_rituals.json": "ritual", "aon_relics.json": "relic",
    "aon_languages.json": "language", "aon_companheiros.json": "animal-companion",
    "aon_equipment_equipment.json": "equipment", "aon_equipment_weapon.json": "weapon",
    "aon_equipment_armor.json": "armor", "aon_equipment_shield.json": "shield",
    "aon_tactics.json": "tactic", "aon_class_kits.json": "class-kit",
}

# Nao e conteudo de personagem jogavel: monstro, perigo, veiculo, texto de
# regra, barra lateral, pagina de indice. Fora do escopo do construtor.
FORA_DE_ESCOPO = {
    "action", "category-page", "condition", "creature", "creature-ability",
    "creature-adjustment", "creature-family", "curse", "hazard", "item-bonus",
    "plane", "rules", "sidebar", "skill-general-action", "vehicle",
    "siege-weapon", "kingdom-structure", "class-sample", "source", "article",
    "trap", "npc", "spell-effect", "creature-theme-template",
}

def censo_aon():
    """categoria -> {id do AoN: nome} dos docs VIGENTES.

    Vigente = nao declara `remaster_id`. O doc legado que aponta sucessor nao
    e entidade a cobrir: ele vira alias do sucessor na base.

    Por ID, nao por contagem: contar deixa registro extra mascarar ausencia --
    20 itens que so o pf2etools tem escondem 20 itens do AoN que faltam, e o
    portao passa com o total batendo.
    """
    docs = {}
    for f in sorted(glob.glob(f"{BRUTOS}/aon_*.json")):
        implicita = CENSO_APELIDO.get(os.path.basename(f))
        try:
            lista = json.load(open(f))
        except Exception:
            continue
        if not isinstance(lista, list):
            continue
        for r in lista:
            if not isinstance(r, dict) or not r.get("id"):
                continue
            d = docs.setdefault(str(r["id"]), {"cat": None, "rid": None, "nome": None})
            d["cat"] = d["cat"] or r.get("category") or implicita
            d["rid"] = d["rid"] or r.get("remaster_id")
            d["nome"] = d["nome"] or r.get("name")
    censo = collections.defaultdict(dict)
    for i, d in docs.items():
        if not d["rid"] and d["cat"]:
            censo[str(d["cat"])][i] = d["nome"]
    return censo


def portao_9_censo(base, ctx):
    """Kind inteiro ausente, medido contra o censo do AoN por categoria.

    Os outros portoes comparam a base com ela mesma (o build anterior) ou com
    o que ela ja cita. Nenhum responde "existe conteudo la fora que nunca
    entrou". Foi assim que `tactic` (as tacticas do Commander, Battlecry!) e
    `class-kit` ficaram de fora sem nada reclamar: nao houve queda, nao houve
    referencia orfa -- eles simplesmente nunca existiram aqui.

    Ausencia ja decidida vive em `censo_ausencias.json` com motivo, igual ao
    portao 8 faz com perda de artefato. Ausencia NOVA quebra.
    """
    censo = censo_aon()
    if not censo:
        return None, ["DESLIGADO: sem dump do AoN em disco (rode dump_aon.py)"]

    conhecidas = {}
    caminho = f"{AQUI}/censo_ausencias.json"
    if os.path.exists(caminho):
        conhecidas = json.load(open(caminho)).get("ausencias") or {}

    # todo id do AoN que a base cita, em qualquer kind e em qualquer papel:
    # `xref.aon` (vigente) e `xref.legado_aon` (absorvido pela fusao)
    citados = set()
    for r in base:
        xr = r.get("xref") or {}
        for chave in ("aon", "legado_aon"):
            if xr.get(chave):
                citados.add(str(xr[chave]))
    # o AoN publica a mesma entidade em mais de um doc quando ela reaparece em
    # outro livro (`Aldori Dueling Sword` tem 3 docs, sem legacy_id ligando os
    # tres). Cobrir por id sozinho acusaria isso como ausencia, entao o nome
    # tambem cobre: a pergunta deste portao e "esse conteudo entrou?", nao
    # "esse doc foi citado?". Quem cita doc legado no lugar do vigente e outro
    # defeito, medido a parte.
    nomes = {norm(r.get("name")) for r in base if r.get("name")}

    novas, ja_sabidas = [], []
    for cat in sorted(censo):
        if cat in FORA_DE_ESCOPO:
            continue
        faltando = {i: n for i, n in censo[cat].items()
                    if i not in citados and norm(n) not in nomes}
        if not faltando:
            continue
        registro = conhecidas.get(cat) or {}
        aceito = set(registro.get("ids_aceitos") or [])
        novos = {i: n for i, n in faltando.items() if i not in aceito}
        amostra = ", ".join(f"{n or i}" for i, n in list(sorted(
            faltando.items(), key=lambda x: str(x[1])))[:6])
        linha = (f"`{cat}`: {len(faltando)} de {len(censo[cat])} vigentes do AoN "
                 f"nao estao na base -- {amostra}")
        if novos:
            novas.append(f"{linha} ({len(novos)} sem decisao registrada)")
        else:
            ja_sabidas.append(f"{linha} -- {registro.get('motivo', 'sem motivo')}")

    detalhe = list(novas)
    if ja_sabidas:
        detalhe.append(f"\n_Ausencias ja decididas ({len(ja_sabidas)} categorias) -- "
                       f"visiveis, nao bloqueiam:_")
        detalhe += [f"- {x}" for x in ja_sabidas]
    return len(novas), detalhe


PORTOES = [
    (1, "prov por campo preenchido", portao_1_prov, ("pre-fusao", "final")),
    (2, "level divergente sem conflito", portao_2_level, ("pre-fusao", "final")),
    (3, "requires citando id inexistente", portao_3_requires, ("final",)),
    (4, "cobertura caindo vs build anterior", portao_4_cobertura, ("final",)),
    (5, "license ausente", portao_5_license, ("pre-fusao", "final")),
    (6, "traits disjunto apos uniao", portao_6_traits, ("pre-fusao", "final")),
    (7, "homonimo no mesmo kind", portao_7_homonimo, ("pre-fusao",)),
    (8, "artefato citado que sumiu do disco", portao_8_artefato_citado, ("final",)),
    (9, "kind ausente vs censo do AoN", portao_9_censo, ("final",)),
]


def main():
    fase = "final"
    if "--fase" in sys.argv:
        fase = sys.argv[sys.argv.index("--fase") + 1]
    if fase not in ("pre-fusao", "final"):
        print(f"fase invalida: {fase}", file=sys.stderr)
        return 2

    base = json.load(open(f"{BASE}/index.json"))
    ctx = {"aon": indice_aon(), "foundry": indice_foundry()}
    print(f"fase {fase}: {len(base)} registros  "
          f"(indices: aon={len(ctx['aon'])}, foundry={len(ctx['foundry'])})")

    linhas = [f"# Portoes de qualidade -- fase `{fase}`", "",
              f"- registros avaliados: **{len(base)}**", ""]
    falhou = 0
    desligados = []
    for num, nome, fn, fases in PORTOES:
        if fase not in fases:
            linhas.append(f"## Portao {num} -- {nome}\n\nNAO SE APLICA nesta fase.\n")
            print(f"  portao {num}  n/a   {nome}")
            continue
        n, detalhe = fn(base, ctx)
        # `None` = o portao nao rodou por falta de fonte. Nao e aprovacao: um
        # portao que se desliga sozinho e devolve zero passa por ausencia de
        # dado, que e o defeito que estes portoes existem para pegar.
        if n is None:
            desligados.append(num)
            print(f"  portao {num}  ??    {nome}: NAO MEDIDO")
            linhas.append(f"## Portao {num} -- {nome}\n")
            linhas.append("**NAO MEDIDO** -- fonte ausente, nao conta como aprovacao.\n")
            linhas += [f"- {d}" for d in detalhe]
            linhas.append("")
            continue
        ok = n == 0
        falhou += 0 if ok else 1
        print(f"  portao {num}  {'OK  ' if ok else 'FALHA'}  {nome}: {n}")
        linhas.append(f"## Portao {num} -- {nome}\n")
        linhas.append(f"**{'PASSOU' if ok else 'FALHOU'}** -- {n} ocorrencia(s).\n")
        linhas += [f"- {d}" for d in detalhe]
        linhas.append("")

    if desligados:
        linhas.insert(3, f"- portoes NAO MEDIDOS (fonte ausente): "
                         f"**{', '.join(str(d) for d in desligados)}**\n")

    if "--gravar-cobertura" in sys.argv:
        # so fixa a linha de base a partir de um build limpo: gravar depois de
        # falhar rebaixa a referencia e a regressao e acusada uma vez so
        if falhou or desligados:
            motivo = (f"{falhou} portao(es) falhando" if falhou
                      else f"portao(es) {desligados} nao medido(s)")
            print(f"  linha de base NAO gravada -- {motivo}")
        else:
            json.dump({"total": len(base),
                       "por_kind": dict(collections.Counter(r.get("kind") for r in base))},
                      open(COBERTURA, "w"), indent=1)
            print(f"  linha de base de cobertura gravada em {COBERTURA}")

    open(f"{BASE}/relatorio_portoes_{fase}.md", "w").write("\n".join(linhas) + "\n")
    print(f"-> base/relatorio_portoes_{fase}.md   "
          f"({'todos passaram' if not falhou else str(falhou) + ' portao(es) falhando'})")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
