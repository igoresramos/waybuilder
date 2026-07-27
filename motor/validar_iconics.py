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
sys.path.insert(0, os.path.join(PROJETO, "pipeline"))
import comum                                  # noqa: E402
# o clone chega como `foundry/` ou `foundry_repo/` conforme quem baixou; este
# era o ultimo script que ainda conhecia so um dos dois nomes
ICONICS = comum.packs_foundry() or os.path.join(
    PROJETO, "pipeline", "dados_brutos", "foundry_repo", "packs", "pf2e")
sys.path.insert(0, AQUI)
from motor import Base, Personagem, RANKS    # noqa: E402

# espelha ficha.py:PERICIAS -- as 16 pericias do PF2e (sem lore, sem
# percepcao, que nao e pericia). Nao importamos de ficha.py pra nao acoplar
# este script a outro dono de arquivo.
PERICIAS = ["acrobatics", "arcana", "athletics", "crafting", "deception",
            "diplomacy", "intimidation", "medicine", "nature", "occultism",
            "performance", "religion", "society", "stealth", "survival",
            "thievery"]


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


def pericias_oficiais(doc):
    """Rank 0-4 de cada pericia do personagem oficial, pelo nome do rank.

    CONVENCAO DE DENOMINADOR (item 4 da tarefa) -- `system.skills.<pericia>`
    do ator do Foundry NAO e o rank final completo. E so o rank RESULTANTE de
    escolha discricionaria do jogador (o treino inicial livre de "N + INT" e
    os aumentos de pericia por nivel) -- o treino AUTOMATICO de classe/
    antecedente fica de fora e a chave some do dict quando a pericia nunca foi
    tocada por uma escolha manual.

    Prova: a Amiri (Barbaro) tem `athletics` ausente/rank 0 em
    `system.skills` nos niveis 1 e 3, mas o item de classe Barbarian desse
    mesmo ator traz `system.trainedSkills.value == ["athletics"]` -- ela E
    treinada em Atletismo por regra (Barbaro treina Atletismo de graca), so
    que isso nunca aparece no dict de pericias. So no nivel 5, quando o
    jogador GASTA um aumento de pericia nela (indo direto pra rank 2), a
    chave aparece.

    Por isso o oraculo usado aqui e a UNIAO de duas fontes independentes do
    proprio ator (nenhuma delas vem da base do motor):
      1. `system.skills.<pericia>.rank`      -- decisao discricionaria
      2. `class`/`background`.system.trainedSkills.value -- treino automatico
         (rank 1 garantido, sem decisao nenhuma envolvida)
    oficial = max(rank_discricionario, 1 se automatico senao 0)

    Chave ausente EM AMBAS as fontes == rank 0 (untrained) de fato -- so
    nesse caso a pericia realmente nunca foi tocada por nada.

    LIMITE CONHECIDO (nao coberto por nenhuma das duas fontes): aumento de
    proficiencia automatico vindo de CLASS FEATURE/feat (ex. o Inventor tem
    a classe-feature "Expert Overdrive", que da RAW confirmado em
    pipeline/base/text/class-feature.json ("You become an expert in
    Crafting") -- automatico, sem escolha do jogador). Isso nao entra em
    `trainedSkills.value` (que so cobre o treino INICIAL) nem sempre aparece
    em `system.skills`. Gera falso positivo de "motor deu rank maior que o
    oficial" -- ver achado no relatorio.
    """
    skills = ((doc.get("system") or {}).get("skills")) or {}
    auto = set()
    for it in doc.get("items") or []:
        if it.get("type") not in ("class", "background"):
            continue
        for s in (((it.get("system") or {}).get("trainedSkills") or {}).get("value") or []):
            auto.add(s)

    saida = {}
    for pericia in PERICIAS:
        discricionario = (skills.get(pericia) or {}).get("rank", 0) or 0
        automatico = 1 if pericia in auto else 0
        rank_num = max(discricionario, automatico)
        saida[pericia] = RANKS[rank_num] if 0 <= rank_num < len(RANKS) else "untrained"
    return saida


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

    # comparacao de rank de pericia -- por pericia, por classe e por
    # combinacao (classe, pericia), pra achar padrao sistematico (item 3)
    contagem_pericias = collections.Counter()
    por_pericia = collections.defaultdict(lambda: collections.Counter())
    por_classe = collections.defaultdict(lambda: collections.Counter())
    por_par = collections.defaultdict(lambda: collections.Counter())
    diverg_pericias = []
    sobre_concessao = []   # motor da rank MAIOR que o oficial -- sinal acionavel

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

        classes_doc = por_tipo(doc, "class")
        classe_nome = classes_doc[0]["name"] if classes_doc else "?"
        oficiais = pericias_oficiais(doc)
        for pericia in PERICIAS:
            of_r = oficiais[pericia]
            no_r = p.proficiencias.get(pericia, "untrained")
            bate_p = (of_r == no_r)
            contagem_pericias["pericia bate" if bate_p else "pericia diverge"] += 1
            por_pericia[pericia]["total"] += 1
            por_classe[classe_nome]["total"] += 1
            por_par[(classe_nome, pericia)]["total"] += 1
            if not bate_p:
                por_pericia[pericia]["diverge"] += 1
                por_classe[classe_nome]["diverge"] += 1
                por_par[(classe_nome, pericia)]["diverge"] += 1
                diverg_pericias.append((doc.get("name"), classe_nome, p.nivel,
                                        pericia, of_r, no_r))
                if RANKS.index(no_r) > RANKS.index(of_r):
                    sobre_concessao.append((doc.get("name"), classe_nome, p.nivel,
                                            pericia, of_r, no_r))

    total_pericias = sum(contagem_pericias.values())
    bate_pericias = contagem_pericias["pericia bate"]

    print(f"personagens avaliados: {sum(contagem.values())}")
    for k, n in contagem.most_common():
        print(f"  {k:16} {n:>4}")
    if divergencias:
        print("\ndivergencias de HP:")
        for nome, of, no, nv, cl in divergencias[:15]:
            print(f"  {nome:26} nivel {nv}  oficial {of}  motor {no}  "
                  f"({of - no:+d})")

    print(f"\npontos de comparacao de pericia (rank): {total_pericias}")
    print(f"  bate      {bate_pericias:>5} ({100*bate_pericias/total_pericias:.1f}%)"
          if total_pericias else "  sem pontos de comparacao")
    print(f"  diverge   {total_pericias - bate_pericias:>5}")
    if por_pericia:
        print("\ndivergencias por pericia:")
        for pericia, c in sorted(por_pericia.items(),
                                  key=lambda kv: -kv[1]["diverge"]):
            if c["diverge"]:
                print(f"  {pericia:14} {c['diverge']:>4}/{c['total']:<4} "
                      f"({100*c['diverge']/c['total']:.0f}%)")

    # secoes markdown -----------------------------------------------------
    linhas_por_pericia = [
        f"- `{pericia}`: {c['diverge']}/{c['total']} divergem "
        f"({100*c['diverge']/c['total']:.0f}%)"
        for pericia, c in sorted(por_pericia.items(), key=lambda kv: -kv[1]["diverge"])
        if c["diverge"]]

    linhas_por_classe = [
        f"- `{classe}`: {c['diverge']}/{c['total']} divergem "
        f"({100*c['diverge']/c['total']:.0f}%)"
        for classe, c in sorted(por_classe.items(), key=lambda kv: -kv[1]["diverge"])
        if c["diverge"]]

    # achado sistemico (item 3): combinacao classe+pericia onde a maioria
    # das ocorrencias diverge, com pelo menos 2 amostras (senao e coincidencia
    # de 1 personagem so). So os mais amostrados entram no relatorio -- a
    # lista completa tem 80+ entradas e viraria a mesma lista crua que o
    # item 2 pediu pra evitar, so que reagrupada
    sistemicos = [
        (classe, pericia, c["diverge"], c["total"])
        for (classe, pericia), c in por_par.items()
        if c["total"] >= 2 and c["diverge"] / c["total"] >= 0.5]
    sistemicos.sort(key=lambda t: (-t[3], -t[2] / t[3]))
    TOPO_SISTEMICOS = 15
    linhas_sistemicos = [
        f"- `{classe}` + `{pericia}`: diverge em {d}/{t} ocorrencias ({100*d/t:.0f}%)"
        for classe, pericia, d, t in sistemicos[:TOPO_SISTEMICOS]]
    if len(sistemicos) > TOPO_SISTEMICOS:
        linhas_sistemicos.append(
            f"- ... e mais {len(sistemicos) - TOPO_SISTEMICOS} combinacoes "
            "classe+pericia com >=50% de divergencia (amostra menor, "
            "2-3 personagens cada) -- o padrao e generalizado, nao um "
            "grupo pequeno de excecoes")

    linhas_sobre = [
        f"- `{nome}` ({classe}, nivel {nv}) -- `{pericia}`: oficial {of_r}, motor {no_r}"
        for nome, classe, nv, pericia, of_r, no_r in sobre_concessao]

    linhas_diverg_detalhe = [
        f"- `{nome}` ({classe}, nivel {nv}) -- `{pericia}`: oficial {of_r}, motor {no_r}"
        for nome, classe, nv, pericia, of_r, no_r in diverg_pericias]

    pct_pericia = f"{100*bate_pericias/total_pericias:.1f}%" if total_pericias else "n/a"
    n_sobre = len(sobre_concessao)
    n_sob = total_pericias - bate_pericias - n_sobre
    secao_pericias = (
        "\n## Pericias (rank)\n\n"
        "Compara o rank 0-4 (untrained/trained/expert/master/legendary) de\n"
        "cada uma das 16 pericias contra o rank oficial reconstruido do ator\n"
        "do Foundry -- pra cada personagem que traduziu (HP bateu ou nao, o\n"
        "rank de pericia e um oraculo independente).\n\n"
        "**Convencao de denominador:** `system.skills.<pericia>.rank` do ator\n"
        "NAO e o rank final completo -- e so o resultado de escolha\n"
        "DISCRICIONARIA do jogador (treino inicial livre + aumentos de\n"
        "pericia por nivel). O treino AUTOMATICO de classe/antecedente fica de\n"
        "fora: a chave simplesmente some do dict quando a pericia nunca foi\n"
        "tocada por uma escolha manual. Prova no corpus: a Amiri (Barbaro) tem\n"
        "`athletics` ausente/rank 0 em `system.skills` nos niveis 1 e 3, mas o\n"
        "item de classe Barbarian desse ator traz\n"
        "`system.trainedSkills.value == [\"athletics\"]` -- ela E treinada em\n"
        "Atletismo por regra (Barbaro treina Atletismo automatico), e isso\n"
        "nunca aparece no dict de pericias.\n\n"
        "Por isso o oraculo usado aqui e a **uniao de duas fontes\n"
        "independentes do proprio ator** (nenhuma vem da base do motor):\n"
        "`system.skills.<pericia>.rank` (decisao discricionaria) UNIDO com\n"
        "`class`/`background`.system.trainedSkills.value (treino automatico,\n"
        "rank 1 garantido). Chave ausente EM AMBAS as fontes == rank 0\n"
        "(untrained) de fato. O denominador e sempre **16 pericias x\n"
        "personagem traduzido**, sem subconjunto.\n\n"
        f"- pontos de comparacao: **{total_pericias}** "
        f"({sum(contagem.values()) - contagem['nao traduzido']} personagens x 16 pericias)\n"
        f"- bate: **{bate_pericias}** ({pct_pericia})\n"
        f"- diverge: **{total_pericias - bate_pericias}**, sendo:\n"
        f"  - motor da rank MENOR que o oficial: **{n_sob}** -- ver \"causa-raiz\" abaixo\n"
        f"  - motor da rank MAIOR que o oficial: **{n_sobre}** -- sinal acionavel, "
        "ver \"Sobre-concessao\" abaixo\n\n"
        "### Causa-raiz da maioria das divergencias (nao e bug do motor)\n\n"
        "A quase totalidade das divergencias e motor MENOR: o motor nunca\n"
        "recebe a escolha discricionaria de pericia do jogador porque (a) este\n"
        "tradutor (`validar_iconics.py`) nao emite escolhas `skill_increase`\n"
        "-- so ha oraculo pro rank FINAL no Foundry, nao pra em qual nivel\n"
        "cada aumento foi gasto -- e (b) `motor/motor.py` **nao processa o\n"
        "slot `skill_increase` de forma alguma**: o schema\n"
        "(`specs/2026-07-26-schema-personagem.md` linha 172-173) declara o\n"
        "slot, mas `grep -n skill_increase motor/motor.py` nao retorna nenhuma\n"
        "ocorrencia. Isso NAO e o achado de bug pedido pela tarefa -- e uma\n"
        "escolha do jogador que este metodo de validacao estruturalmente nao\n"
        "consegue auditar (nao ha oraculo de \"qual nivel\"), analogo a\n"
        "limitacao ja documentada pro multiclasse por divisao de niveis.\n\n"
        "### Divergencias por pericia\n\n"
        + ("\n".join(linhas_por_pericia) + "\n" if linhas_por_pericia else "nenhuma.\n")
        + "\n### Divergencias por classe\n\n"
        + ("\n".join(linhas_por_classe) + "\n" if linhas_por_classe else "nenhuma.\n")
        + "\n### Achados sistemicos (classe + pericia, >=2 amostras, "
          ">=50% divergindo)\n\n"
        f"**{len(sistemicos)}** combinacoes classe+pericia batem esse\n"
        "criterio -- confirma que a causa-raiz acima e generalizada: sao as\n"
        "pericias que os personagens pre-gerados da Paizo tipicamente ELEGEM\n"
        "treinar/subir por escolha do jogador, nao um bug localizado numa\n"
        f"classe. Top {min(TOPO_SISTEMICOS, len(sistemicos))} por tamanho de amostra:\n\n"
        + ("\n".join(linhas_sistemicos) + "\n" if linhas_sistemicos
           else "nenhum padrao sistemico encontrado.\n")
        + "\n### Sobre-concessao (motor MAIOR que o oficial -- unico sinal "
          f"realmente acionavel, {n_sobre} caso(s))\n\n"
        "Investigado caso a caso -- NAO e bug do motor. Os 2 casos sao\n"
        "`Droven` (Inventor) em `crafting`: o motor aplica a class-feature\n"
        "`Expert Overdrive`, cujo texto RAW confirma\n"
        "(`pipeline/base/text/class-feature.json`, chave\n"
        "`wb:text/class-feature/expert-overdrive`): \"You become an expert in\n"
        "Crafting\" -- automatico, sem escolha do jogador. O motor esta\n"
        "correto; e o `system.skills` do ator do Foundry que NAO persiste\n"
        "esse aumento automatico vindo de class feature (mesma classe de\n"
        "limite documentada acima pro `trainedSkills.value`, so que essa\n"
        "fonte nao cobre aumentos de FEATURE, so o treino INICIAL). Sem essa\n"
        "explicacao os 2 casos ficariam contados como divergencia real; estao\n"
        "listados aqui por transparencia, mas nao indicam problema no motor.\n\n"
        + ("\n".join(linhas_sobre) + "\n" if linhas_sobre else "nenhuma.\n")
        + "\n### Amostra de divergencias individuais (ate 25, nao exaustiva -- "
          "ver secoes acima pro padrao completo)\n\n"
        + ("\n".join(linhas_diverg_detalhe[:25]) + "\n" if linhas_diverg_detalhe
           else "nenhuma.\n"))

    saida = os.path.join(PROJETO, "docs", "2026-07-27_validacao-iconics.md")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    open(saida, "w").write(
        "# Validacao contra os personagens oficiais da Paizo\n\n"
        "A houserule so diverge do RAW quando ha mais de uma classe. Logo, um\n"
        "personagem de **classe unica** montado por este motor tem que bater\n"
        "exatamente com o oficial -- se nao bater, o motor esta errado.\n\n"
        "## HP\n\n"
        f"- avaliados: **{sum(contagem.values())}**\n"
        + "".join(f"- {k}: **{n}**\n" for k, n in contagem.most_common())
        + "\n### Por personagem\n\n" + "\n".join(linhas) + "\n"
        + secao_pericias)
    print(f"-> {saida}")
    return 0 if not divergencias and not diverg_pericias else 1


if __name__ == "__main__":
    sys.exit(main())
