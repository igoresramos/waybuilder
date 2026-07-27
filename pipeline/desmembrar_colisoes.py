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
        if cat:
            por_nome[(cat, portoes.norm(d.get("name")))].append(d)

    ids = {r["id"] for r in base}
    novos, relatorio = [], []

    for r in list(base):
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
