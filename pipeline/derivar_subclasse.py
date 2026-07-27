#!/usr/bin/env python3
"""
Ensina o predicado a falar de SUBCLASSE.

A linguagem de predicado sabia falar de classe (`class_level`) e de personagem
(`character_level`), mas nao da camada do meio. Isso fura a premissa da regra 3
em pelo menos um caso publicado: a proficiencia de conjuracao do Clerigo depende
da **Doutrina** -- Cloistered segue o padrao de conjurador pleno (expert 7,
master 15, legendary 19) e Warpriest e mais lento e nunca chega a legendary
(expert 11, master 19). Duas progressoes, mesma classe, mesmo nivel.

O dado ja existia: `spellcasting.proficiency` do Clerigo vem com as duas
progressoes separadas por doutrina desde a primeira extracao. Faltava alguem
consumir.

Faltava tambem o termo. 199 `requires` ja apontavam para sub-escolhas usando
`has`, que e generico demais: `has` significa "tem este registro", e nao
distingue "escolheu esta doutrina" de "pegou este feat". Um predicado que nao
distingue nao consegue expressar "so para Warpriest".

Converte:
    {"has": "wb:class-feature/warpriest"}
    -> {"subclass": {"cleric": "wb:class-feature/warpriest"}}

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_subclasse_predicado.md
"""
import json, os, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def caminhar(obj):
    """Devolve (container, chave) de cada `has` do predicado."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k == "has" and isinstance(v, str):
                yield obj, k
            else:
                yield from caminhar(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from caminhar(x)


def main():
    base = json.load(open(f"{BASE}/index.json"))

    # id de sub-escolha -> (slug da classe dona, eixo)
    dono = {}
    for classe in [r for r in base if r.get("kind") == "class"]:
        slug = classe["id"].split("/")[-1]
        for bloco in classe.get("subclasses") or []:
            for opcao in bloco.get("opcoes") or []:
                dono[opcao] = (slug, bloco.get("eixo"))

    convertidos = collections.Counter()
    exemplos = []
    for r in base:
        for container, chave in caminhar(r.get("requires")):
            alvo = container[chave]
            if alvo not in dono:
                continue
            slug, eixo = dono[alvo]
            del container[chave]
            container["subclass"] = {slug: alvo}
            convertidos[eixo] += 1
            if len(exemplos) < 8:
                exemplos.append((r["id"], r.get("name"), slug, eixo, alvo))
            r.setdefault("prov", {})["requires"] = (
                (r.get("prov") or {}).get("requires", "") + "+subclasse").lstrip("+")

    # a progressao de proficiencia por subclasse ja existe no dado; marcar
    # explicitamente quais classes a tem, para o motor nao ter que adivinhar
    por_subclasse = []
    for classe in [r for r in base if r.get("kind") == "class"]:
        sc = classe.get("spellcasting")
        if not isinstance(sc, dict):
            continue
        prof = sc.get("proficiency") or {}
        # progressao normal e {trained: 1, expert: 7, ...}; por subclasse e
        # {cloistered_cleric: {...}, warpriest: {...}}
        aninhada = {k: v for k, v in prof.items() if isinstance(v, dict)}
        if aninhada:
            sc["proficiency_por_subclasse"] = True
            por_subclasse.append((classe.get("name"), sorted(aninhada)))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    total = sum(convertidos.values())
    print(f"`has` convertidos para `subclass`: {total}")
    for eixo, n in convertidos.most_common():
        print(f"  {eixo:20} {n:>4}")
    print(f"\nclasses com progressao de proficiencia por subclasse: {len(por_subclasse)}")
    for nome, chaves in por_subclasse:
        print(f"  {nome}: {chaves}")

    linhas = ["# `subclass` no predicado", "",
              "A linguagem sabia falar de classe e de personagem, nao da camada do",
              "meio. `has` e generico demais: nao distingue \"escolheu esta doutrina\"",
              "de \"pegou este feat\".", "",
              f"- `has` convertidos: **{total}**", "",
              "## Por eixo", ""]
    linhas += [f"- `{e}`: {n}" for e, n in convertidos.most_common()]
    linhas += ["", "## Exemplos", ""]
    for wid, nome, slug, eixo, alvo in exemplos:
        linhas.append(f"- `{wid}` ({nome}) -> "
                      f"`{{\"subclass\": {{\"{slug}\": \"{alvo}\"}}}}`  _({eixo})_")
    linhas += ["", "## Progressao de proficiencia por subclasse", "",
               "O caso que a spec cita, e que o dado ja carregava sem ninguem ler:", ""]
    for nome, chaves in por_subclasse:
        linhas.append(f"- **{nome}**: {', '.join(chaves)}")
    open(f"{BASE}/relatorio_subclasse_predicado.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_subclasse_predicado.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
