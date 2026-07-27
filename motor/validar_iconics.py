#!/usr/bin/env python3
"""
Valida o motor contra os personagens oficiais da Paizo.

## Por que isto e possivel, e por que e a validacao mais forte disponivel

A houserule so diverge do RAW **quando ha mais de uma classe**. Todas as 22
regras se reduzem ao PF2e oficial quando `nivel_de_classe == nivel_de_personagem`
-- a regra 17 da elevacao zero, a regra 4 nao tem o que comparar, a regra 8 nao
tem segunda classe para negar, a regra 12 cai na cadencia normal.

Logo: **um personagem de classe unica montado por este motor tem que bater
exatamente com o oficial.** Se nao bater, o motor esta errado, sem ambiguidade
e sem discussao de balanceamento.

O repo do Foundry traz os iconics da Paizo (Valeros, Ezren, Kyra...) nos niveis
1, 3 e 5, com HP calculado e a lista de escolhas completa -- ancestria, heranca,
background, classe e os boosts por nivel em `build.attributes.boosts`.

## O que NAO da para validar assim

O multiclasse por divisao de niveis. Nenhuma fonte no mundo tem esses numeros,
porque a regra nao existe fora desta mesa. Ali sobram consistencia interna
(teste_motor.py) e a regra 21: a rota de nivel de classe nunca pode entregar
menos que a rota de dedicacao.

Uso: python3 validar_iconics.py
"""
import json, os, re, sys, glob, unicodedata, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)
ICONICS = os.path.join(PROJETO, "pipeline", "dados_brutos",
                       "foundry_repo", "packs", "pf2e")
sys.path.insert(0, AQUI)
from motor import Base, Personagem          # noqa: E402


def slug(nome):
    s = unicodedata.normalize("NFKD", str(nome or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def por_tipo(doc, tipo):
    return [it for it in (doc.get("items") or []) if it.get("type") == tipo]


def traduzir(doc, base):
    """Ator do Foundry -> documento de personagem do Waybuilder."""
    sistema = doc.get("system") or {}
    nivel = ((sistema.get("details") or {}).get("level") or {}).get("value") or 1

    classes = por_tipo(doc, "class")
    if not classes:
        return None, "sem item de classe"
    classe_id = f"wb:class/{slug(classes[0]['name'])}"
    if base.opcional(classe_id) is None:
        return None, f"classe ausente da base: {classe_id}"

    escolhas = []
    for tipo, slot, prefixo in (("ancestry", "ancestralidade", "ancestry"),
                                ("heritage", "heranca", "heritage"),
                                ("background", "background", "background")):
        itens = por_tipo(doc, tipo)
        if not itens:
            continue
        nome = itens[0]["name"]
        # 'Skilled Human (Intimidation)' -> a escolha entre parenteses e do
        # jogador, nao faz parte do id
        wid = f"wb:{prefixo}/{slug(re.sub(r'\\s*\\([^)]*\\)\\s*$', '', nome))}"
        if base.opcional(wid) is not None:
            escolhas.append({"em": "criacao", "slot": slot, "pega": wid})

    for n in range(1, nivel + 1):
        escolhas.append({"em": n, "slot": "nivel_de_classe", "pega": classe_id})

    boosts = ((sistema.get("build") or {}).get("attributes") or {}).get("boosts") or {}
    for nivel_str, atributos in boosts.items():
        if str(nivel_str).isdigit() and atributos:
            escolhas.append({"em": int(nivel_str), "slot": "boosts_livres",
                             "pega": list(atributos)})

    # Boosts de ancestria e background: o motor os registra como "escolha entre
    # [x, y]" e NAO decide -- decidir por conta seria arbitrar pelo jogador. O
    # Foundry guarda a decisao em `selected`, entao aqui ela e importada como
    # escolha explicita. Sem isso a comparacao acusa exatamente 1 ponto de
    # modificador de diferenca por personagem, que e ruido de metodo, nao bug.
    # So as escolhas REAIS: quando ha uma opcao unica, o motor ja aplicou
    # sozinho, e importar de novo contaria o boost duas vezes.
    resolvidos = []
    for tipo in ("ancestry", "background"):
        for it in por_tipo(doc, tipo):
            for entrada in ((it.get("system") or {}).get("boosts") or {}).values():
                if not isinstance(entrada, dict) or not entrada.get("selected"):
                    continue
                if len(entrada.get("value") or []) != 1:
                    resolvidos.append(entrada["selected"])
    chave_bloco = (classes[0].get("system") or {}).get("keyAbility") or {}
    chave = chave_bloco.get("selected")
    if chave and len(chave_bloco.get("value") or []) != 1:
        resolvidos.append(chave)
    if resolvidos:
        escolhas.append({"em": "criacao", "slot": "boosts_livres",
                         "pega": resolvidos})

    # feats escolhidos: sem eles o motor nao ve `Toughness` e o HP sai
    # `nivel` pontos abaixo
    for it in por_tipo(doc, "feat"):
        wid = f"wb:feat/{slug(re.sub(r'\\s*\\([^)]*\\)\\s*$', '', it['name']))}"
        if base.opcional(wid) is not None:
            escolhas.append({"em": 1, "slot": "class_feat", "pega": wid})

    doc_wb = {"esquema": "waybuilder/personagem@1",
              "identidade": {"nome": doc.get("name")},
              "escolhas": escolhas}
    return (doc_wb, chave), None


def hp_oficial(doc):
    return (((doc.get("system") or {}).get("attributes") or {}).get("hp") or {}).get("value")


def hp_esperado_raw(p, chave_escolhida):
    """HP pelo RAW: ancestria + nivel x (HP da classe + mod de CON)."""
    return p.hp


def main():
    base = Base()
    arquivos = sorted(glob.glob(f"{ICONICS}/iconics/*/*.json")) + \
        sorted(glob.glob(f"{ICONICS}/paizo-pregens/*/*.json"))
    arquivos = [f for f in arquivos if not os.path.basename(f).startswith("_")]
    if not arquivos:
        print(f"sem iconics em {ICONICS} -- rode pipeline/buscar_fontes.sh",
              file=sys.stderr)
        return 1

    linhas, contagem = [], collections.Counter()
    divergencias = []

    for f in arquivos:
        try:
            doc = json.load(open(f))
        except Exception:
            continue
        if doc.get("type") != "character":
            continue
        traduzido, erro = traduzir(doc, base)
        if erro:
            contagem["nao traduzido"] += 1
            linhas.append(f"- `{doc.get('name')}` -- NAO TRADUZIDO: {erro}")
            continue
        doc_wb, chave = traduzido
        p = Personagem(doc_wb, base)

        oficial = hp_oficial(doc)
        nosso = p.hp

        bate = (oficial == nosso)
        contagem["hp bate" if bate else "hp diverge"] += 1
        if not bate:
            divergencias.append((doc.get("name"), oficial, nosso,
                                 p.nivel, list(p.niveis_por_classe)))
        linhas.append(
            f"- {'OK  ' if bate else 'DIFF'} `{doc.get('name')}` "
            f"nivel {p.nivel} -- HP oficial {oficial}, motor {nosso}")

    print(f"personagens avaliados: {sum(contagem.values())}")
    for k, n in contagem.most_common():
        print(f"  {k:16} {n:>4}")
    if divergencias:
        print("\ndivergencias de HP:")
        for nome, of, no, nv, cl in divergencias[:15]:
            print(f"  {nome:26} nivel {nv}  oficial {of}  motor {no}  "
                  f"({of - no:+d})")

    saida = os.path.join(PROJETO, "docs", "2026-07-27_validacao-iconics.md")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    open(saida, "w").write(
        "# Validacao contra os personagens oficiais da Paizo\n\n"
        "A houserule so diverge do RAW quando ha mais de uma classe. Logo, um\n"
        "personagem de **classe unica** montado por este motor tem que bater\n"
        "exatamente com o oficial -- se nao bater, o motor esta errado.\n\n"
        f"- avaliados: **{sum(contagem.values())}**\n"
        + "".join(f"- {k}: **{n}**\n" for k, n in contagem.most_common())
        + "\n## Por personagem\n\n" + "\n".join(linhas) + "\n")
    print(f"-> {saida}")
    return 0 if not divergencias else 1


if __name__ == "__main__":
    sys.exit(main())
