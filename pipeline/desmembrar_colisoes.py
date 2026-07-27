#!/usr/bin/env python3
"""
Desmembra registros que fundiram duas entidades distintas sob o mesmo slug.

`wb:<kind>/<slug>` assume nome unico por kind. Nao e. Ha homonimo legitimo, as
vezes no mesmo livro:

  `Death from Above` sao dois feats. O Foundry tem so um (nivel 8, archetype,
  Pactbreaker); o AoN tem os dois (feat-7610 archetype nivel 8 e feat-7380
  mitico nivel 16, War of Immortals p.128). O extrator casou o Foundry com o
  doc errado do AoN e emitiu nivel 8 com traits `mythic` -- uma quimera --,
  perdendo o outro feat inteiro.

  > A spec dizia "o Foundry separa os dois; o AoN indexa so o mitico".
  > Verificado em 2026-07-26: e o contrario nos dois lados.

O detector (portao 7) acha o caso comparando a base contra o censo do AoN:
registro cujo nome tem N entidades na fonte, com assinatura (level, traits)
divergente entre elas. Aqui cada entidade orfa vira registro proprio, com sufixo
derivado do que a distingue, e `xref` apontando so para o doc correspondente.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_colisoes.md
"""
import json, os, sys, re, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "extratores"))
import portoes                                     # noqa: E402
import aon_kinds                                   # noqa: E402
from reconciliar import normalizar_livro, LIVROS_ORC   # noqa: E402
import traits_uniao                                    # noqa: E402

BASE = f"{AQUI}/base"

# Traits que distinguem bem uma entidade da outra quando o nome colide.
# Sao os eixos que a Paizo usa para reaproveitar nome: camada de regra (mythic),
# origem (ancestria/classe) e tipo de opcao (archetype).
TRAITS_DISTINTIVOS = ("mythic", "archetype", "rare", "uncommon")


CURADORIA = f"{AQUI}/colisoes_identidade.json"


def _fixar(reg, campo, valor):
    """Escreve campo simples ou aninhado (`source.page`), com prov de curadoria."""
    if "." in campo:
        pai, filho = campo.split(".", 1)
        reg.setdefault(pai, {})[filho] = valor
    else:
        reg[campo] = valor
    reg.setdefault("prov", {})[campo] = "curadoria"


def aplicar_curadoria(base, aon, ids, relatorio):
    """Aplica `colisoes_identidade.json` ANTES do detector automatico.

    O arquivo existia com 6 colisoes verificadas a mao contra o AoN e o
    checkout do Foundry -- e **nenhum script o lia**. O detector automatico
    resolvia os mesmos casos por heuristica e chegava a outro resultado: em
    `death-from-above` ele deixou o registro canonico no doc mitico e parkeou o
    id do Foundry do arquetipo como `foundry_ambiguo` no registro errado, alem
    de criar um terceiro registro. A curadoria e mais confiavel que a
    heuristica porque cada par foi conferido doc a doc; ela vem primeiro, e o
    detector so cuida do que ela nao cobre.

    Devolve (novos_registros, ids_tratados).
    """
    if not os.path.exists(CURADORIA):
        return [], set()
    curada = json.load(open(CURADORIA))
    por_id = {r["id"]: r for r in base}
    novos, tratados = [], set()

    for chave, caso in curada.items():
        if chave.startswith("_"):
            continue
        entrada = por_id.get(chave)
        if not entrada:
            relatorio.append(f"- CURADORIA `{chave}`: nao existe na base -- pulado")
            continue
        tratados.add(chave)
        for i, ent in enumerate(caso.get("entidades") or []):
            alvo = por_id.get(ent["id"])
            if alvo is None:
                doc = aon.get(str((ent.get("xref") or {}).get("aon") or ""))
                alvo = aon_kinds.converter(doc, entrada.get("kind")) if doc else None
                if alvo is None:
                    relatorio.append(f"- CURADORIA `{ent['id']}`: sem doc do AoN "
                                     f"para criar o irmao -- pulado")
                    continue
                alvo["id"] = ent["id"]
                alvo["text"] = f"wb:text/{entrada.get('kind')}/{ent['id'].split('/', 1)[-1]}"
                alvo["desmembrado_de"] = chave
                src = alvo.setdefault("source", {})
                if not src.get("license"):
                    livro = normalizar_livro(src.get("book") or "")
                    if src.get("remaster") is True or livro in LIVROS_ORC:
                        src["license"] = "ORC"
                    elif livro:
                        src["license"] = "OGL"
                    if src.get("license"):
                        alvo.setdefault("prov", {})["source.license"] = "inferida:livro"
                ids.add(alvo["id"])
                por_id[alvo["id"]] = alvo
                novos.append(alvo)
            # o xref curado MANDA: e ele que diz qual doc descreve qual entidade
            alvo["xref"] = dict(ent.get("xref") or {})
            # ...e os traits tem de seguir o xref. Sem realinhar, o registro
            # canonico fica com o trait da OUTRA entidade: `death-from-above`
            # ficava `['archetype', 'mythic']` -- o `mythic` era do irmao, e a
            # quimera que o desmembramento existe para desfazer sobrevivia
            # dentro do proprio caso curado.
            doc_curado = aon.get(str((ent.get("xref") or {}).get("aon") or ""))
            if doc_curado and doc_curado.get("trait"):
                antes_tr = list(alvo.get("traits") or [])
                finais, aliases, _ = traits_uniao.unir(
                    {"aon": [str(t) for t in doc_curado["trait"]]})
                if finais and sorted(antes_tr) != finais:
                    alvo["traits"] = finais
                    alvo.setdefault("prov", {})["traits"] = ["aon"]
                    alvo.setdefault("conflitos", []).append(
                        {"campo": "traits", "antes": antes_tr,
                         "aon": finais, "escolhido": "aon"})
                if aliases:
                    alvo["aliases_traits"] = sorted(
                        set(alvo.get("aliases_traits") or []) | set(aliases))
            for campo, valor in (ent.get("correcoes") or {}).items():
                _fixar(alvo, campo, valor)
            # o irmao aponta de volta para o id que colidiu, tenha ele sido
            # criado agora ou ja existisse na base -- e por este campo que o
            # portao 7 sabe que o caso foi tratado
            if alvo["id"] != chave:
                alvo["desmembrado_de"] = chave
            tratados.add(alvo["id"])
            relatorio.append(
                f"- CURADORIA `{alvo['id']}`{' (criado)' if i and alvo in novos else ''}: "
                f"xref {alvo['xref']}, correcoes {ent.get('correcoes') or {}}")
    return novos, tratados


def sufixo_de(doc, irmaos):
    """Sufixo que separa este doc dos irmaos: trait exclusivo, senao o nivel."""
    meus = {str(t).lower() for t in (doc.get("trait") or [])}
    dos_outros = set()
    for o in irmaos:
        if str(o.get("id")) != str(doc.get("id")):
            dos_outros |= {str(t).lower() for t in (o.get("trait") or [])}
    exclusivos = meus - dos_outros
    for preferido in TRAITS_DISTINTIVOS:
        if preferido in exclusivos:
            return preferido
    if exclusivos:
        return sorted(exclusivos)[0]
    if doc.get("level") is not None:
        return f"nv{doc['level']}"
    return str(doc.get("id"))


def main():
    base = json.load(open(f"{BASE}/index.json"))
    aon = portoes.indice_aon()
    if not aon:
        print("ERRO: sem dump do AoN em disco", file=sys.stderr)
        return 1

    por_nome = collections.defaultdict(list)
    for d in aon.values():
        cat = str(d.get("category") or "")
        # mesma regra do portao 7: doc com `remaster_id` e a versao LEGADO de
        # outra coisa, nao uma entidade a desmembrar. Sem isto o passo cria
        # irmao para cada nome que o remaster renomeou -- `Hellknight
        # Dedication` (feat-1078) viraria um registro proprio embora seu
        # sucessor `Hellknight Preferment` ja esteja na base.
        if cat and not d.get("remaster_id"):
            por_nome[(cat, portoes.norm(d.get("name")))].append(d)

    ids = {r["id"] for r in base}
    novos, relatorio = [], []

    curados, tratados = aplicar_curadoria(base, aon, ids, relatorio)
    novos += curados

    for r in list(base):
        if r["id"] in tratados:
            continue                      # ja resolvido a mao, com doc conferido
        if r.get("kind") == "class-feature":
            continue                      # compartilhada por N classes, por design
        candidatos = por_nome.get((r.get("kind"), portoes.norm(r.get("name"))))
        if not candidatos or len(candidatos) < 2:
            continue
        grupos = portoes._grupos_de_identidade(candidatos)
        if len(grupos) < 2:
            continue                      # so par legacy/remaster
        assinaturas = {(g[0].get("level"),
                        tuple(sorted(map(str, g[0].get("trait") or []))))
                       for g in grupos}
        if len(assinaturas) < 2:
            continue                      # mesma entidade em duas edicoes

        casado = str((r.get("xref") or {}).get("aon") or "")
        representantes = [g[0] for g in grupos]
        orfaos = [d for d in representantes if str(d.get("id")) != casado]
        if len(orfaos) == len(representantes):
            # a base casou com um doc que nao representa nenhum grupo: nao da
            # para decidir qual e o "certo" sem arbitrar. Fica para revisao.
            relatorio.append(f"- `{r['id']}` casou com `{casado}`, que nao "
                             f"representa nenhum dos {len(grupos)} grupos -- REVISAR")
            continue

        # Realinhar o ORIGINAL com o doc que ele casou. Sem isto o desmembramento
        # so cria o irmao e deixa a quimera de pe: `death-from-above` casou com o
        # doc mitico (nivel 16) mas seguia com nivel 8 e traits
        # ['archetype','mythic'], porque o nivel vinha do Foundry -- que descreve
        # a OUTRA entidade. Quando o casamento erra, a precedencia por campo
        # propaga o erro em vez de conter.
        doc_casado = aon.get(casado)
        if doc_casado:
            antes_lv, antes_tr = r.get("level"), list(r.get("traits") or [])
            nivel_aon = doc_casado.get("level")
            # passa pela mesma uniao do reconciliador: sem isso o trait vem cru
            # do AoN e reintroduz o que o item 20 corrigiu -- `fatal` no lugar de
            # `fatal-d10`, `gnoll` no lugar de `kholo`
            traits_aon, aliases_tr, _ = traits_uniao.unir(
                {"aon": [str(t) for t in (doc_casado.get("trait") or [])]})
            if aliases_tr:
                r["aliases_traits"] = sorted(
                    set(r.get("aliases_traits") or []) | set(aliases_tr))
            mudou = []
            if nivel_aon is not None and antes_lv != nivel_aon:
                r["level"] = nivel_aon
                r.setdefault("prov", {})["level"] = "aon"
                mudou.append({"campo": "level", "foundry": antes_lv,
                              "aon": nivel_aon, "escolhido": "aon"})
            if traits_aon and sorted(antes_tr) != traits_aon:
                r["traits"] = traits_aon
                r.setdefault("prov", {})["traits"] = ["aon"]
                mudou.append({"campo": "traits", "antes": antes_tr,
                              "aon": traits_aon, "escolhido": "aon"})
            if mudou:
                r.setdefault("conflitos", []).extend(mudou)
                # o xref do Foundry descrevia o irmao, nao este registro
                if "foundry" in (r.get("xref") or {}):
                    r["xref"]["foundry_ambiguo"] = r["xref"].pop("foundry")
                relatorio.append(f"- `{r['id']}` realinhado com `{casado}`: "
                                 f"nivel {antes_lv} -> {r.get('level')}, "
                                 f"traits {antes_tr} -> {r.get('traits')}")

        for doc in orfaos:
            sufixo = aon_kinds.slug(sufixo_de(doc, representantes))
            novo = aon_kinds.converter(doc, r.get("kind"))
            if not novo:
                continue
            novo["id"] = f"{novo['id']}-{sufixo}"
            if novo["id"] in ids:
                novo["id"] = f"{novo['id']}-{aon_kinds.slug(str(doc.get('id')))}"
            novo["text"] = f"wb:text/{r.get('kind')}/{novo['id'].split('/', 1)[-1]}"
            novo["desmembrado_de"] = r["id"]
            # a inferencia de licenca do reconciliador ja passou; sem isto o
            # irmao nasce sem `license` e derruba o portao 5
            src = novo.setdefault("source", {})
            if not src.get("license"):
                livro = normalizar_livro(src.get("book") or "")
                if src.get("remaster") is True or livro in LIVROS_ORC:
                    src["license"] = "ORC"
                elif livro:
                    src["license"] = "OGL"
                if src.get("license"):
                    novo.setdefault("prov", {})["source.license"] = "inferida:livro"
            ids.add(novo["id"])
            novos.append(novo)
            relatorio.append(
                f"- `{r['id']}` (casou `{casado}`) ganhou irmao `{novo['id']}` "
                f"de `{doc.get('id')}` -- nv{doc.get('level')}, "
                f"traits {sorted(map(str, doc.get('trait') or []))}")

    base.extend(novos)
    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    print(f"registros desmembrados: {len(novos)}")
    print(f"base: {len(base) - len(novos)} -> {len(base)}")

    linhas = ["# Colisoes de identidade desmembradas", "",
              "`wb:<kind>/<slug>` assume nome unico por kind, e nao e. Cada",
              "entidade orfa -- presente no censo do AoN, ausente da base porque o",
              "casamento por nome escolheu outra -- vira registro proprio.", "",
              f"- irmaos criados: **{len(novos)}**", "",
              "## Casos", ""] + relatorio
    open(f"{BASE}/relatorio_colisoes.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_colisoes.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
