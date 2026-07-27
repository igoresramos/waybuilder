#!/usr/bin/env python3
"""
Camada de reconciliacao da base canonica do Waybuilder.

Os extratores rodam em paralelo e cada um so enxerga a propria familia de
entidade. Esta camada e serial de proposito: ela e a unica que ve a base
inteira, e por isso e a unica que consegue

  1. detectar duas entidades distintas colidindo no mesmo id -- ANTES de fundir
  2. fundir registros que colidem no mesmo id canonico, registrando divergencia
  3. normalizar a grafia do livro no valor emitido, nao so na comparacao
  4. registrar toda divergencia em `conflitos`, nunca escolher em silencio

A ordem de (1) importa: na v1 a fusao de id acontecia antes de qualquer
verificacao, e o portao que procurava duplicata rodava depois -- perguntava se
existia duplicata depois de a duplicata ter sido eliminada. Foi por essa fresta
que `death-from-above` (dois feats distintos) virou uma quimera.

Entrada: pipeline/saida/*.json
Saida:   pipeline/base/index.json + pipeline/base/relatorio_reconciliacao.md
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comum  # noqa: E402

ENTRADA = ["classes.json", "feats.json", "magias.json", "ancestrias.json",
           "equipamento.json", "companheiros.json", "referencia.json",
           "rituais.json", "relicos_idiomas.json"]

LIVROS_ORC = {"player core", "player core 2", "gm core", "monster core",
              "npc core", "war of immortals", "battlecry", "shining kingdoms",
              "howl of the wild", "rage of elements", "divine mysteries"}

CAMPOS_IGNORADOS = ("conflitos", "prov", "xref", "traits", "aliases_traits")


def carregar():
    regs = []
    for arq in ENTRADA:
        caminho = f"{AQUI}/saida/{arq}"
        if not os.path.exists(caminho):
            print(f"  ! ausente: {arq}", file=sys.stderr)
            continue
        d = json.load(open(caminho))
        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
        for r in lista:
            if isinstance(r, dict) and r.get("id"):
                r.setdefault("_origem", arq)
                regs.append(r)
    return regs


def fonte_do_campo(reg, campo):
    """De qual fonte veio este campo neste registro.

    Preferencia: o proprio `prov`. Sem prov, cai para a unica fonte do `xref`
    -- e quando nem isso decide, o campo e do proprio pipeline. Nunca
    'desconhecida': a spec v2 proibiu o valor.
    """
    p = (reg.get("prov") or {}).get(campo)
    if p:
        f = comum.fonte_de(p)
        if f in comum.FONTES:
            return f
    fontes = [k for k in (reg.get("xref") or {})
              if k in ("aon", "foundry", "pf2etools")]
    if len(fontes) == 1:
        return fontes[0]
    return "waybuilder"


def fundir(grupo):
    """Funde N registros do mesmo id canonico usando a escolha compartilhada.

    Divergencia entre fontes vira `conflitos` sempre -- e a mesma operacao da
    escolha, nao um passo opcional depois dela.
    """
    campos = []
    for r in grupo:
        for k in r:
            if not k.startswith("_") and k not in CAMPOS_IGNORADOS and k not in campos:
                campos.append(k)

    base, prov, conflitos = {}, {}, []
    for k in campos:
        # `source` e composto: comparar o dict inteiro transforma diferenca de
        # grafia do livro em conflito falso (era boa parte dos 72 conflitos de
        # source) e faz um lado com pagina perder para outro sem. Vai por
        # subcampo.
        if k == "source":
            subcampos, fontes_src = {}, {}
            for r in grupo:
                src = r.get(k) or {}
                f = fonte_do_campo(r, k)
                for sub, v in src.items():
                    if not comum.vazio(v):
                        subcampos.setdefault(sub, {}).setdefault(f, v)
            novo = {}
            for sub, por_fonte_sub in subcampos.items():
                valor, p, confs = comum.escolher(f"source.{sub}", por_fonte_sub)
                if valor is not None:
                    novo[sub] = valor
                    fontes_src[sub] = p
                    conflitos += confs
            if novo:
                base[k] = novo
                for sub, p in fontes_src.items():
                    prov[f"source.{sub}"] = p
                prov[k] = fontes_src.get("book") or next(iter(fontes_src.values()))
            continue

        por_fonte = {}
        for r in grupo:
            v = r.get(k)
            if comum.vazio(v):
                continue
            f = fonte_do_campo(r, k)
            # duas entradas da mesma fonte: a primeira ja e a boa
            por_fonte.setdefault(f, v)
        valor, p, confs = comum.escolher(k, por_fonte)
        if valor is not None:
            base[k] = valor
            # `prov` do registro original tem mais detalhe (marca de inferencia)
            origem = next((r for r in grupo
                           if not comum.vazio(r.get(k)) and fonte_do_campo(r, k) == comum.fonte_de(p)),
                          None)
            detalhado = (origem.get("prov") or {}).get(k) if origem else None
            prov[k] = detalhado if comum.prov_valido(detalhado or "") else p
            conflitos += confs

    # traits e uniao das fontes, nao escolha
    por_fonte_traits = {}
    for r in grupo:
        if r.get("traits"):
            por_fonte_traits.setdefault(fonte_do_campo(r, "traits"), []).extend(r["traits"])
    traits, aliases_traits, contribuiram = comum.uniao_traits(por_fonte_traits)
    base["traits"] = traits          # sempre lista: nunca null (achado A13)
    if aliases_traits:
        base["aliases_traits"] = aliases_traits
    if contribuiram:
        # `traits` e o unico campo cuja prov e lista: ele nao tem vencedora,
        # tem contribuintes (spec v2, "`traits` e uniao, nao precedencia").
        prov["traits"] = [comum.prov_lido(f) for f in sorted(contribuiram)
                          if f in comum.FONTES]

    # xref tem um slot por fonte, e homonimo declarado ocupa dois: o doc legado
    # e o vigente tem o MESMO nome (5.599 pares no AoN -- `Tusks` feat-1286 ->
    # `Tusks` feat-4519), entao caem no mesmo slug e disputam o slot. Na v1 o
    # `update` sobrescrevia um deles em silencio. Agora o vigente fica em
    # `aon` e o substituido em `legado_aon`.
    ponte = comum.carregar_ponte()
    xref = {}
    for r in grupo:
        for fonte, valor in (r.get("xref") or {}).items():
            atual = xref.get(fonte)
            if atual is None or atual == valor:
                xref[fonte] = valor
            elif fonte == "aon":
                novo_legado = comum.e_legado(valor, ponte)
                atual_legado = comum.e_legado(atual, ponte)
                if novo_legado and not atual_legado:
                    xref["legado_aon"] = valor
                elif atual_legado and not novo_legado:
                    xref["legado_aon"], xref["aon"] = atual, valor
                else:
                    xref.setdefault(f"{fonte}_alt", valor)
            else:
                xref.setdefault(f"{fonte}_alt", valor)
    base["xref"] = xref
    base["prov"] = prov
    for r in grupo:
        conflitos += list(r.get("conflitos") or [])
    if conflitos:
        base["conflitos"] = conflitos
    base.pop("_origem", None)
    return base


def carregar_curadoria():
    caminho = f"{AQUI}/colisoes_identidade.json"
    if not os.path.exists(caminho):
        return {}
    with open(caminho) as fh:
        return {k: v for k, v in json.load(fh).items() if not k.startswith("_")}


def aplicar_correcoes(reg, correcoes):
    for campo, valor in (correcoes or {}).items():
        if "." in campo:
            pai, filho = campo.split(".", 1)
            reg.setdefault(pai, {})[filho] = valor
        else:
            reg[campo] = valor
        reg.setdefault("prov", {})[campo] = comum.prov_lido("aon")


def desmembrar_curado(grupo, curadoria):
    """Separa homonimos usando o xref que cada fonte declara.

    Nao e heuristica: cada entidade da curadoria diz por qual id de fonte ela
    e reconhecida, verificado caso a caso contra o AoN e o checkout do Foundry
    (docs/2026-07-26_colisoes-identidade.md).
    """
    entrada = curadoria.get(grupo[0]["id"])
    if not entrada:
        return None
    saida = []
    for reg in grupo:
        xref = reg.get("xref") or {}
        destino = None
        for ent in entrada["entidades"]:
            if any(xref.get(fonte) == valor for fonte, valor in ent["xref"].items()):
                destino = ent
                break
        novo = dict(reg)
        if destino and destino["id"] != reg["id"]:
            novo["id"] = destino["id"]
            novo["desmembrado_de"] = reg["id"]
            novo.setdefault("prov", {})["id"] = comum.prov_lido("aon")
        if destino:
            aplicar_correcoes(novo, destino.get("correcoes"))
        saida.append(novo)
    return saida if len({r["id"] for r in saida}) > 1 else None


def desmembrar(grupo):
    """Duas entidades distintas no mesmo id: cada uma ganha slug proprio.

    Detector (spec): conflito com valores categoricamente disjuntos nao e
    divergencia de fonte, e sinal de fusao indevida. Roda ANTES de fundir.
    """
    if len(grupo) < 2:
        return None
    for i, a in enumerate(grupo):
        for b in grupo[i + 1:]:
            if not comum.traits_disjuntos(a.get("traits"), b.get("traits")):
                continue
            saida = []
            for reg in grupo:
                outro = b if reg is a else a
                sufixo = comum.sufixo_desambiguador(reg, outro)
                novo = dict(reg)
                if sufixo:
                    novo["id"] = f"{reg['id']}-{comum.slug_trait(sufixo)}"
                    novo.setdefault("prov", {})["id"] = comum.prov_lido("waybuilder")
                    novo["desmembrado_de"] = reg["id"]
                saida.append(novo)
            if len({r["id"] for r in saida}) > 1:
                return saida
    return None


def preferir_doc_vigente(base):
    """Registro casado com o doc LEGADO do AoN passa a apontar para o vigente.

    O AoN publica dois docs para a mesma entidade quando ela sobreviveu ao
    remaster com o mesmo nome (`Acrobat` archetype-4 e archetype-236). Quando o
    extrator casa com o legado, o registro fica preso a versao antiga e a fusao
    depois reporta o vigente como "alvo declarado ausente da base" -- que e
    falso: ele esta la, so ligado ao doc errado.

    So troca quando o alvo tem o mesmo nome normalizado e nenhum outro registro
    ja o ocupa. O id legado nao some: vai para `xref.legado_aon`.
    """
    ponte = comum.carregar_ponte()
    ocupados = {(r.get("xref") or {}).get("aon") for r in base}
    trocados = 0
    for r in base:
        aon = (r.get("xref") or {}).get("aon")
        doc = ponte.get(aon) if aon else None
        if not doc or not doc.get("remaster_id"):
            continue
        for alvo in comum.como_lista(doc["remaster_id"]):
            doc_alvo = ponte.get(alvo)
            if not doc_alvo or alvo in ocupados:
                continue
            if doc_alvo.get("category") != doc.get("category"):
                continue
            if comum.normalizar(doc_alvo.get("name")) != comum.normalizar(r.get("name")):
                continue
            r["xref"]["legado_aon"] = aon
            r["xref"]["aon"] = alvo
            ocupados.add(alvo)
            r.setdefault("prov", {})["xref.aon"] = comum.prov_inferido("aon", "remaster_id")
            trocados += 1
            break
    return trocados


def resolver_referencias(base):
    """Conserta referencia `wb:` quebrada quando o alvo existe com outro nome.

    O parser de pre-requisito cita o nome que leu na fonte e monta o id a
    partir dele. Quando a fonte usa o nome LEGADO (`Mage Hand`, que no remaster
    e `Telekinetic Hand`; `Sweetbreath Gnoll` -> `Sweetbreath Kholo`), o id
    nasce apontando para coisa que nao existe. Duas tentativas, nesta ordem:
    nome normalizado do proprio slug, e o nome resolvido pela ponte do AoN.

    Devolve (corrigidas, ainda_quebradas).
    """
    ids = {r["id"] for r in base}
    por_nome = {}
    for r in base:
        for nome in [r.get("name")] + list(r.get("aliases") or []):
            if nome:
                por_nome.setdefault((r.get("kind"), comum.normalizar(nome)), r["id"])

    curado = {}
    caminho = f"{AQUI}/aliases_referencias.json"
    if os.path.exists(caminho):
        with open(caminho) as fh:
            curado = json.load(fh)
    mapear = {k: v["para"] for k, v in (curado.get("mapear") or {}).items()}
    ignorar = set(curado.get("ignorar") or {})

    ponte = comum.carregar_ponte()
    por_nome_aon = {}
    for doc in ponte.values():
        if doc.get("name"):
            por_nome_aon.setdefault(comum.normalizar(doc["name"]), []).append(doc)
    aon_para_wb = {}
    for r in base:
        aon = (r.get("xref") or {}).get("aon")
        if aon:
            aon_para_wb[aon] = r["id"]

    # Sufixo que nomeia a FAMILIA da sub-escolha. O parser de pre-requisito le
    # "Enigma Muse" na prosa e monta `wb:class-feature/enigma-muse`, mas o
    # registro vindo do Foundry se chama so "Enigma"; e ha o caso inverso
    # ("Empiricism" contra "Empiricism Methodology"). Sao os dois lados da
    # mesma escolha de segundo nivel.
    SUFIXOS_FAMILIA = ("muse", "racket", "cause", "calling", "methodology",
                       "school", "doctrine", "instinct", "thesis", "field",
                       "study", "implement", "ikon", "gate", "order", "style",
                       "mystery", "patron", "bloodline", "conscious mind",
                       "subconscious mind", "wizard", "specialty")

    def variacoes(nome):
        yield nome
        for suf in SUFIXOS_FAMILIA:
            if nome.endswith(" " + suf):
                yield nome[: -len(suf) - 1]
            else:
                yield f"{nome} {suf}"

    def resolver(alvo):
        if alvo in ids or not alvo.startswith("wb:") or alvo.startswith("wb:text/"):
            return None
        if alvo in mapear and mapear[alvo] in ids:
            return mapear[alvo]
        kind, _, slug = alvo[3:].partition("/")
        nome = comum.normalizar(slug.replace("-", " "))
        for tentativa in variacoes(nome):
            achado = por_nome.get((kind, tentativa))
            if achado:
                return achado
        for doc in por_nome_aon.get(nome, []):
            for destino in comum.como_lista(doc.get("remaster_id")):
                if destino in aon_para_wb:
                    return aon_para_wb[destino]
        return None

    corrigidas, quebradas = 0, set()

    def anda(v):
        nonlocal corrigidas
        if isinstance(v, dict):
            for k, x in list(v.items()):
                if isinstance(x, str) and x.startswith("wb:"):
                    novo = resolver(x)
                    if novo:
                        v[k] = novo
                        corrigidas += 1
                    elif x not in ids and not x.startswith("wb:text/"):
                        quebradas.add(x)
                else:
                    anda(x)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                if isinstance(x, str) and x.startswith("wb:"):
                    novo = resolver(x)
                    if novo:
                        v[i] = novo
                        corrigidas += 1
                    elif x not in ids and not x.startswith("wb:text/"):
                        quebradas.add(x)
                else:
                    anda(x)

    def poda(no):
        """Tira do predicado o termo que nao e entidade (prosa que virou id).

        Devolve o no limpo ou None quando o termo inteiro deve sair. O texto
        original nao se perde: continua em `requires_texto`.
        """
        if isinstance(no, dict):
            if isinstance(no.get("has"), str) and no["has"] in ignorar:
                return None
            limpo = {}
            for k, v in no.items():
                if k in ("all", "any", "not") and isinstance(v, list):
                    itens = [x for x in (poda(i) for i in v) if x is not None]
                    if not itens:
                        continue
                    limpo[k] = itens
                else:
                    limpo[k] = v
            return limpo or None
        if isinstance(no, list):
            itens = [x for x in (poda(i) for i in no) if x is not None]
            return itens or None
        return no

    podados = 0
    for r in base:
        if ignorar and r.get("requires"):
            limpo = poda(r["requires"])
            if limpo != r["requires"]:
                podados += 1
                if limpo is None:
                    r.pop("requires", None)
                    (r.get("prov") or {}).pop("requires", None)
                else:
                    r["requires"] = limpo
        for campo in ("requires", "grants", "progressao"):
            if r.get(campo):
                anda({campo: r[campo]} if isinstance(r[campo], str) else r[campo])
    if podados:
        print(f"predicados podados de referencia que nao e entidade: {podados}")
    return corrigidas, sorted(quebradas)


def main():
    regs = carregar()
    print(f"carregados: {len(regs)} registros de {len(ENTRADA)} familias")

    # --- 1. PORTAO 7 (pre-fusao): duas entidades no mesmo id ---------------
    por_id = collections.defaultdict(list)
    for r in regs:
        por_id[r["id"]].append(r)

    curadoria = carregar_curadoria()
    desmembrados = []
    regs2 = []
    for ident, grupo in por_id.items():
        novo = None
        if len(grupo) > 1:
            novo = desmembrar_curado(grupo, curadoria) or desmembrar(grupo)
        if novo:
            desmembrados.append((ident, sorted({r["id"] for r in novo})))
            regs2 += novo
        else:
            regs2 += grupo

    # consolidar duplicado declarado na curadoria (mesma entidade em dois ids)
    consolida = {}
    for entrada in curadoria.values():
        consolida.update(entrada.get("consolidar") or {})
    if consolida:
        for r in regs2:
            if r["id"] in consolida:
                r["id"] = consolida[r["id"]]
        print(f"ids consolidados por curadoria: {len(consolida)}")
    print(f"colisoes de identidade desmembradas: {len(desmembrados)}")

    # --- 2. fundir colisoes de id que sobraram ----------------------------
    por_id = collections.defaultdict(list)
    for r in regs2:
        por_id[r["id"]].append(r)
    colisoes = {k: v for k, v in por_id.items() if len(v) > 1}
    base = [fundir(v) if len(v) > 1 else fundir([v[0]]) for v in por_id.values()]
    print(f"colisoes de id fundidas: {len(colisoes)}  ->  base com {len(base)} registros")

    # --- 3. source.book na forma canonica, com a grafia crua preservada ----
    canon = comum.eleger_canonicos(
        (r.get("source") or {}).get("book") for r in base)
    normalizados = 0
    for r in base:
        src = r.get("source") or {}
        r["source"] = src
        bruto = comum.limpar_livro(src.get("book"))
        if not bruto:
            continue
        forma = canon.get(comum.chave_livro(bruto), bruto)
        if forma != src.get("book"):
            if forma != bruto or bruto != src.get("book"):
                src["book_raw"] = src.get("book")
            src["book"] = forma
            r.setdefault("prov", {})["source.book"] = comum.prov_lido(
                comum.fonte_de((r.get("prov") or {}).get("source") or "aon"))
            normalizados += 1
    print(f"source.book normalizado na escrita: {normalizados}")

    # --- 4. inferir license ausente, marcando a inferencia -----------------
    inferidas = 0
    for r in base:
        src = r["source"]
        if src.get("license"):
            continue
        livro = comum.chave_livro(src.get("book") or "")
        if src.get("remaster") is True or livro in LIVROS_ORC:
            src["license"] = "ORC"
        elif livro:
            src["license"] = "OGL"
        else:
            continue
        src["license_inferida"] = True      # visivel no registro, nao so em prov
        r.setdefault("prov", {})["source.license"] = comum.prov_inferido("waybuilder", "livro")
        inferidas += 1
    print(f"license inferida a partir do livro: {inferidas}")

    # --- 5. descartar artefato organizacional (pasta do Foundry) -----------
    def e_artefato(r):
        return (not (r.get("source") or {}).get("book")
                and not r.get("traits")
                and r.get("level") is None
                and not r.get("grants"))
    descartados = [r["id"] for r in base if e_artefato(r)]
    base = [r for r in base if not e_artefato(r)]
    if descartados:
        print(f"artefatos organizacionais descartados: {len(descartados)} -> {descartados}")

    # --- 6. referencia citando nome legado aponta para o registro certo -----
    corrigidas, quebradas = resolver_referencias(base)
    print(f"referencias wb: corrigidas por nome/ponte: {corrigidas}  "
          f"(seguem quebradas: {len(quebradas)})")

    os.makedirs(f"{AQUI}/base", exist_ok=True)
    with open(f"{AQUI}/base/index.json", "w") as fh:
        json.dump(base, fh, ensure_ascii=False, separators=(",", ":"))

    kinds = collections.Counter(r.get("kind") for r in base)
    com_conf = sum(1 for r in base if r.get("conflitos"))
    linhas = ["# Relatorio de reconciliacao", "",
              f"- registros de entrada: **{len(regs)}**",
              f"- colisoes de identidade desmembradas: **{len(desmembrados)}**",
              f"- colisoes de id fundidas: **{len(colisoes)}**",
              f"- base final: **{len(base)}** registros",
              f"- registros com divergencia registrada: **{com_conf}**",
              f"- source.book normalizado: **{normalizados}**",
              f"- license inferida: **{inferidas}**", "",
              "## Por kind", ""]
    linhas += [f"- `{k}`: {n}" for k, n in kinds.most_common()]
    if desmembrados:
        linhas += ["", "## Colisoes de identidade desmembradas", ""]
        for ident, novos in desmembrados:
            linhas.append(f"- `{ident}` -> {', '.join('`%s`' % n for n in novos)}")
    open(f"{AQUI}/base/relatorio_reconciliacao.md", "w").write("\n".join(linhas) + "\n")

    print(f"kinds: {dict(kinds)}")
    print(f"-> base/index.json  ({os.path.getsize(f'{AQUI}/base/index.json')/1e6:.1f} MB)")
    print("portoes de qualidade: rodar pipeline/portoes.py depois de emitir_textos e fundir")
    return 0


if __name__ == "__main__":
    sys.exit(main())
