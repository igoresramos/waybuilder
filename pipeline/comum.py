#!/usr/bin/env python3
"""
Camada compartilhada do pipeline do Waybuilder.

Existe por causa de um achado da auditoria de 2026-07-26: a escolha por
precedencia estava replicada em 7 extratores, cada um com uma regra propria, e
por isso "divergencia nunca silenciada" nao era verificavel -- 6 kinds inteiros
(1.618 registros com 2+ fontes) sairam do build com ZERO conflitos registrados,
enquanto 145 divergencias reais de `source.book` eram comprovaveis contra o
Foundry.

Regra: escolher por precedencia e registrar divergencia sao a MESMA operacao, e
ela mora aqui. Ver specs/2026-07-26-schema-base.md (v2).

So stdlib. Sem efeito colateral no import.
"""
import json
import os
import re
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))

FONTES = ("aon", "foundry", "pf2etools", "waybuilder")

# Precedencia por campo, conforme a spec. Unica copia no projeto.
PRECEDENCIA = {
    "grants":   ["foundry", "pf2etools", "aon"],
    "requires": ["pf2etools", "foundry", "aon"],
    "name":     ["aon", "foundry", "pf2etools"],
    "rarity":   ["aon", "foundry", "pf2etools"],
    "text":     ["aon", "foundry", "pf2etools"],
    "source":   ["aon", "foundry", "pf2etools"],
    "level":    ["foundry", "pf2etools", "aon"],
    "rank":     ["foundry", "aon", "pf2etools"],
    # `traits` NAO entra aqui: e uniao, nao precedencia (ver uniao_traits).
}
PADRAO = ["foundry", "aon", "pf2etools"]

# Kinds que nao produzem `grants` por natureza: respondem null (nao se aplica),
# nunca false. Medido na v1: `false` distribuido por kind inteiro denunciava
# propriedade do extrator, nao do dado.
#
# `deity` fica aqui apesar de alimentar o build do Cleric: o que ele da
# (favored weapon, divine font, dominios) sao campos proprios, nao `grants`.
# `archetype` e container -- quem concede mecanica sao os feats dele.
KINDS_SEM_GRANTS = {"trait", "skill", "deity", "domain", "language", "archetype"}

# Kinds onde pre-requisito nao existe por natureza: `requires_parseado` e null.
# Sem esta lista, "kind que nao produz o campo responde null" e "registro sem
# pre-requisito responde true" mandavam valores diferentes para o mesmo
# registro.
KINDS_SEM_REQUISITO = {"trait", "skill", "language", "domain", "deity",
                       "spell", "ancestry", "background"}

# Regras de inferencia aceitas em `prov`. Lista fechada -- entrada nova so com
# registro na spec.
REGRAS_INFERENCIA = {"livro", "remaster_id", "traits", "nome-aproximado",
                     "diretorio", "espelho-rank"}


# --------------------------------------------------------------------------
# normalizacao de texto
# --------------------------------------------------------------------------

def normalizar(s):
    """Nome comparavel: sem acento, sem pontuacao, caixa baixa, espaco unico."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[-‐-―_/]+", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def chave_livro(b):
    """'Pathfinder Dark Archive (Remastered)' e 'Dark Archives (Remastered)'
    caem na mesma chave. Chave e para COMPARAR; para emitir use canonizar_livro."""
    n = normalizar(b)
    n = re.sub(r"^pathfinder ", "", n)
    n = re.sub(r"\bremastered\b", "remaster", n)
    n = re.sub(r"\barchives\b", "archive", n)
    n = re.sub(r"\bcores?\b", "core", n)
    return n.strip()


# compatibilidade com o codigo antigo, que chamava assim
normalizar_livro = chave_livro


def limpar_livro(b):
    """Tira o lixo bruto que vaza da fonte: \\r\\n literal, espaco duplo, borda."""
    if not b:
        return b
    s = str(b).replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def eleger_canonicos(grafias):
    """Dado um iteravel de grafias cruas de livro, devolve {chave: grafia canonica}.

    Canonica = a mais frequente; empate resolve pela mais curta, depois
    alfabetica. Deterministico e nao inventa nome que nenhuma fonte usou.
    """
    contagem = {}
    for g in grafias:
        g = limpar_livro(g)
        if not g:
            continue
        contagem.setdefault(chave_livro(g), {}).setdefault(g, 0)
        contagem[chave_livro(g)][g] += 1
    canon = {}
    for k, formas in contagem.items():
        canon[k] = sorted(formas.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0][0]
    return canon


# --------------------------------------------------------------------------
# proveniencia
# --------------------------------------------------------------------------

def prov_lido(fonte):
    assert fonte in FONTES, f"fonte fora do vocabulario: {fonte}"
    return fonte


def prov_inferido(fonte, regra):
    assert fonte in FONTES, f"fonte fora do vocabulario: {fonte}"
    assert regra in REGRAS_INFERENCIA, f"regra de inferencia nao registrada: {regra}"
    return f"{fonte}~inferido:{regra}"


def prov_valido(valor):
    """A spec proibe `prov` sem fonte identificavel (era 'desconhecida' na v1).

    `traits` e uniao, entao a prov dele e a LISTA de fontes que contribuiram --
    unico campo onde o valor nao e escalar.
    """
    if isinstance(valor, list):
        return bool(valor) and all(prov_valido(v) for v in valor)
    if not isinstance(valor, str) or not valor:
        return False
    fonte, _, sufixo = valor.partition("~")
    if fonte not in FONTES:
        return False
    if not sufixo:
        return True
    if not sufixo.startswith("inferido:"):
        return False
    return sufixo.split(":", 1)[1] in REGRAS_INFERENCIA


def fonte_de(prov_valor):
    """Fonte crua de um valor de prov, ignorando a marca de inferencia.

    Aceita lista (o caso de `traits`, que e uniao) devolvendo a primeira fonte.
    """
    if isinstance(prov_valor, list):
        prov_valor = prov_valor[0] if prov_valor else ""
    s = str(prov_valor or "")
    # tolerante na ENTRADA (os extratores ainda produzem formatos antigos como
    # "foundry:none" ou "aon (nome aproximado)"), estrito na SAIDA -- o valor
    # emitido passa por prov_valido.
    m = re.match(r"^(aon|foundry|pf2etools|waybuilder)\b", s)
    return m.group(1) if m else s.split("~", 1)[0]


# --------------------------------------------------------------------------
# escolha por precedencia + registro de divergencia (a mesma operacao)
# --------------------------------------------------------------------------

def _iguais(campo, a, b):
    """Dois valores sao o MESMO valor?

    Normalizacao agressiva so vale para nome de livro, onde a diferenca de
    grafia entre fontes e ruido conhecido. Para o resto a comparacao e
    literal: a spec diz que `"God's"` contra `"Gods'"` **e** divergencia real,
    e normalizar mascarava 46 pares assim (`Needle In The God's Eyes` contra
    `Needle in the Gods' Eyes`, `Advanced Runic Mind Smithing` contra
    `Mind-Smithing`).
    """
    if campo in ("source.book", "book"):
        return chave_livro(a) == chave_livro(b)
    return json.dumps(a, sort_keys=True, default=str) == \
           json.dumps(b, sort_keys=True, default=str)


def vazio(v):
    return v is None or v == "" or v == [] or v == {}


def escolher(campo, por_fonte):
    """Escolhe o valor de um campo entre fontes e registra a divergencia.

    por_fonte: {"foundry": valor, "aon": valor, ...} -- fontes sem o campo podem
    ser omitidas ou vir vazias.

    Devolve (valor, prov, conflitos) onde conflitos e lista (vazia se as fontes
    concordam). Divergencia e SEMPRE registrada: nao existe caminho que escolha
    em silencio.
    """
    candidatos = {f: v for f, v in por_fonte.items() if not vazio(v)}
    if not candidatos:
        return None, None, []

    # subcampo herda a precedencia do pai: `source.page` segue `source`
    ordem = PRECEDENCIA.get(campo) or PRECEDENCIA.get(campo.split(".")[0]) or PADRAO

    def fonte_base(f):
        """`aon_2` (segunda entrada da mesma fonte) ordena como `aon`."""
        raiz = f.rsplit("_", 1)[0]
        return raiz if raiz in FONTES else f

    def rank(f):
        b = fonte_base(f)
        return ordem.index(b) if b in ordem else len(ordem)
    vencedora = sorted(candidatos, key=lambda f: (rank(f), f))[0]
    valor = candidatos[vencedora]

    conflitos = []
    divergentes = {f: v for f, v in candidatos.items()
                   if f != vencedora and not _iguais(campo, v, valor)}
    if divergentes:
        registro = {"campo": campo, "escolhido": vencedora, vencedora: valor}
        registro.update(divergentes)
        conflitos.append(registro)
    return valor, prov_lido(fonte_base(vencedora)), conflitos


# --------------------------------------------------------------------------
# traits: uniao, nao precedencia
# --------------------------------------------------------------------------

_MAPA = None


def mapa_traits():
    global _MAPA
    if _MAPA is None:
        with open(os.path.join(AQUI, "normalizacao_traits.json")) as fh:
            _MAPA = json.load(fh)
    return _MAPA


def slug_trait(t):
    return re.sub(r"\s+", "-", normalizar(t))


_PARAM = re.compile(r"^(?P<base>.+?)-(?:d\d+|\d+(?:-min)?|min)$")


def base_parametrizada(t):
    """'two-hand-d12' -> 'two-hand'; 'thrown-20' -> 'thrown'; senao None."""
    m = _PARAM.match(t)
    if not m:
        return None
    base = m.group("base")
    fam = mapa_traits().get("familias_parametrizadas", {})
    return base if base in fam else None


def uniao_traits(por_fonte):
    """Uniao das tres fontes, nesta ordem: mapa legado->remaster, absorcao por
    granularidade, uniao ordenada.

    Devolve (traits, aliases_traits, fontes_que_contribuiram).
    """
    m = mapa_traits()
    renom, removidos = m["renomeados"], set(m["removidos_sem_sucessor"])

    juntos, aliases, contribuiram = set(), set(), []
    for fonte, traits in (por_fonte or {}).items():
        if not traits:
            continue
        contribuiram.append(fonte)
        for t in traits:
            s = slug_trait(t)
            if not s:
                continue
            if s in renom:
                aliases.add(s)
                s = renom[s]
            elif s in removidos:
                aliases.add(s)
                continue
            juntos.add(s)

    # absorcao por granularidade: o parametrizado engole o base
    bases_cobertas = {b for b in (base_parametrizada(t) for t in juntos) if b}
    traits = sorted(juntos - bases_cobertas)
    return traits, sorted(aliases), sorted(set(contribuiram))


# --------------------------------------------------------------------------
# localizacao das fontes em disco
# --------------------------------------------------------------------------

def packs_foundry(brutos=None):
    """Raiz dos packs do Foundry, ou None se o clone nao esta em disco.

    O clone chega com dois nomes conforme quem o baixou (`buscar_fontes.sh`
    grava em `foundry/`, o tarball do pin grava em `foundry_repo/`). Os
    extratores ja tentavam os dois; portoes, emitir_textos, aplicar_subclasses
    e converter_rule_elements so conheciam um -- e nesta maquina caiam no lado
    errado, desligando o portao 2 e pulando a conversao de rule elements sem
    que nada acusasse.
    """
    brutos = brutos or os.path.join(AQUI, "dados_brutos")
    for c in (os.environ.get("WB_FOUNDRY_PACKS", ""),
              os.path.join(brutos, "foundry_repo", "packs", "pf2e"),
              os.path.join(brutos, "foundry", "packs", "pf2e")):
        if c and os.path.isdir(c):
            return c
    return None


# --------------------------------------------------------------------------
# ponte legado <-> remaster (a chave que o AoN publica)
# --------------------------------------------------------------------------

_PONTE = None


def carregar_ponte(brutos=None):
    """id do doc AoN -> doc, para todo doc que declara remaster_id ou legacy_id.

    Le o dump dedicado quando existe e completa com os dumps por categoria:
    nenhum dos dois sozinho cobre todos os kinds.
    """
    global _PONTE
    if _PONTE is not None:
        return _PONTE
    import glob
    brutos = brutos or os.path.join(AQUI, "dados_brutos")
    docs = {}
    arquivos = ([os.path.join(brutos, "aon_ponte_remaster.json")]
                + sorted(glob.glob(os.path.join(brutos, "aon_*.json")))
                + sorted(glob.glob(os.path.join(brutos, "aon", "*.json"))))
    for arq in arquivos:
        if not os.path.exists(arq) or arq.endswith("aon_censo.json"):
            continue
        try:
            with open(arq) as fh:
                d = json.load(fh)
        except Exception:  # noqa: BLE001 -- dump quebrado nao derruba o build
            continue
        if not isinstance(d, list):
            continue
        for x in d:
            if isinstance(x, dict) and x.get("id") and (
                    x.get("remaster_id") or x.get("legacy_id")):
                docs.setdefault(x["id"], x)
    _PONTE = docs
    return docs


def como_lista(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def e_legado(aon_id, ponte=None):
    """O AoN declara que este doc foi substituido por outro."""
    p = ponte if ponte is not None else carregar_ponte()
    return bool((p.get(aon_id) or {}).get("remaster_id"))


# --------------------------------------------------------------------------
# colisao de identidade
# --------------------------------------------------------------------------

# Sufixo de grau em item e variante legitima, nao colisao (falso positivo
# conhecido, registrado na spec).
SUFIXOS_DE_GRAU = ("greater", "major", "true", "lesser", "moderate", "minor",
                   "supreme")

CATEGORIAS_DISJUNTAS = ("mythic", "archetype", "class", "ancestry", "skill",
                        "general", "bonus")


def traits_disjuntos(a, b):
    """True quando dois conjuntos de traits nao tem intersecao e ambos tem
    algum trait de categoria -- sinal de que sao duas entidades, nao uma
    divergencia de fonte."""
    sa, sb = set(a or []), set(b or [])
    if not sa or not sb or (sa & sb):
        return False
    return bool((sa & set(CATEGORIAS_DISJUNTAS)) or (sb & set(CATEGORIAS_DISJUNTAS)))


def sufixo_desambiguador(reg, outro):
    """Sufixo deterministico para desmembrar homonimos. Primeira regra que
    distingue vence: trait de categoria, classe/arquetipo dono, livro, nivel."""
    ta, tb = set(reg.get("traits") or []), set(outro.get("traits") or [])
    so_meu = sorted((ta - tb) & set(CATEGORIAS_DISJUNTAS))
    if so_meu:
        return so_meu[0]
    dono = reg.get("class") or reg.get("archetype")
    outro_dono = outro.get("class") or outro.get("archetype")
    if dono and dono != outro_dono:
        return re.sub(r"^wb:[^/]+/", "", str(dono))
    livro = (reg.get("source") or {}).get("book")
    outro_livro = (outro.get("source") or {}).get("book")
    if livro and chave_livro(livro) != chave_livro(outro_livro or ""):
        return "-".join(normalizar(livro).split())[:24]
    if reg.get("level") is not None and reg.get("level") != outro.get("level"):
        return f"nv{reg['level']}"
    return None


# --------------------------------------------------------------------------
# camadas de mecanizacao
# --------------------------------------------------------------------------

def mecanizacao(kind, tinha_mecanica, perdeu_mecanica,
                tem_requires_texto, requires_saiu):
    """(grants_completos, requires_parseado) conforme a spec v2.

    null = nao se aplica. false so quando houve perda real.
    """
    if kind in KINDS_SEM_GRANTS:
        grants_completos = None
    elif not tinha_mecanica:
        grants_completos = True          # nada a converter e sucesso
    else:
        grants_completos = not perdeu_mecanica

    if kind in KINDS_SEM_REQUISITO and not tem_requires_texto:
        requires_parseado = None
    else:
        requires_parseado = True if not tem_requires_texto else bool(requires_saiu)
    return grants_completos, requires_parseado
