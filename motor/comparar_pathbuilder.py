#!/usr/bin/env python3
"""
Compara o que o Waybuilder OFERECE num slot com o que o Pathbuilder oferece.

A tese, do review adversarial: o Pathbuilder vale como oraculo de
COMPORTAMENTO. Ele nao e fonte de regra -- a fonte e o livro --, mas e um
segundo implementador do mesmo RAW, e onde os dois discordam ha o que olhar.

Entrada: o JSON colhido por `app/verificacao/sonda-pathbuilder.mjs`, que le a
lista real da tela do Pathbuilder rodando local.

O que o relatorio separa, e por que a separacao importa mais que o placar:

  - **so no Pathbuilder** -- candidato que o Waybuilder nao oferece. Suspeita de
    buraco na base ou de elegibilidade de slot estreita demais.
  - **so no Waybuilder** -- pode ser acerto NOSSO (a houserule muda o que cabe
    no slot) ou ruido de fonte. Nao e defeito automatico.
  - **divergencia de disponibilidade** -- os dois oferecem, mas discordam se o
    personagem atende. Aqui mora o defeito de PREDICADO, que e o mais caro de
    achar por leitura.

Uso: python3 motor/comparar_pathbuilder.py docs/comparacao/pathbuilder-*.json
"""
import collections
import glob
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from motor import Base, Personagem   # noqa: E402

# A sonda parte do default do Pathbuilder (Human / Barkeep) e troca so a classe,
# entao o equivalente aqui e o mesmo trio. Cada classe nova precisa de uma linha
# -- e de proposito: montar por nome adivinhado calaria a divergencia.
ANCESTRIA, BACKGROUND = "wb:ancestry/human", "wb:background/barkeep"
DEFAULT = {
    "Fighter": ("wb:class/fighter", ANCESTRIA, BACKGROUND),
    "Wizard": ("wb:class/wizard", ANCESTRIA, BACKGROUND),
    "Cleric": ("wb:class/cleric", ANCESTRIA, BACKGROUND),
    "Ranger": ("wb:class/ranger", ANCESTRIA, BACKGROUND),
    "Rogue": ("wb:class/rogue", ANCESTRIA, BACKGROUND),
    "Barbarian": ("wb:class/barbarian", ANCESTRIA, BACKGROUND),
    "Bard": ("wb:class/bard", ANCESTRIA, BACKGROUND),
    "Monk": ("wb:class/monk", ANCESTRIA, BACKGROUND),
    "Champion": ("wb:class/champion", ANCESTRIA, BACKGROUND),
    "Druid": ("wb:class/druid", ANCESTRIA, BACKGROUND),
    "Sorcerer": ("wb:class/sorcerer", ANCESTRIA, BACKGROUND),
    "Alchemist": ("wb:class/alchemist", ANCESTRIA, BACKGROUND),
    "Investigator": ("wb:class/investigator", ANCESTRIA, BACKGROUND),
}


# O Pathbuilder nao nasce com os atributos zerados: ele ja atribui parte dos
# boosts sozinho, e deixa o resto pendente. Comparar o nosso personagem (tudo
# 10) com o dele fabricava divergencia -- 17 pontos de `exige STR >= 14; tem 10`
# que nao eram defeito de motor nenhum, eram bancada torta.
#
# MEDIDO com `app/verificacao/sonda-estado-pathbuilder.mjs`, um arquivo por
# combinacao em `docs/comparacao/estado-pathbuilder-<classe>-nv<N>.json`. Cada
# boost e +2, entao 3 boosts em STR dao 16 (modificador +3).
#
# A habilidade-chave NAO entra na lista quando ela tem opcao unica (INT do Mago,
# WIS do Clerigo, DEX do Ladino): nesse caso o motor ja aplica sozinho, e
# declarar de novo dobrava o valor. A do Guerreiro e escolha entre `str` e `dex`,
# entao ela precisa ser declarada.
BOOSTS_DO_PATHBUILDER = {
    "Fighter": ["str", "str", "str", "dex", "con"],   # STR 16, DEX 12, CON 12
    "Wizard":  ["str", "str", "dex", "con"],          # + INT 12 da chave
    "Cleric":  ["str", "str", "dex", "con"],          # + WIS 12 da chave
    "Rogue":   ["str", "str", "dex", "con"],          # + DEX 14 da chave
    # medidos com `sonda-estado-pathbuilder.mjs` em 2026-07-30, nao chutados:
    # Bard sai STR +2 DEX +1 CON +1 CHA +1, Monk sai STR +3 DEX +1 CON +1.
    "Bard":    ["str", "str", "dex", "con"],          # + CHA 12 da chave
    "Monk":    ["str", "str", "str", "dex", "con"],   # STR 16, sem chave extra
    # medidos em 2026-07-30 com a mesma sonda, um arquivo por classe em
    # `docs/comparacao/estado-pathbuilder-<classe>-nv1.json`. A regra do bloco
    # acima vale: a chave so entra na lista quando ela e ESCOLHA. Campeao tem
    # `key_ability: [dex, str]` e por isso declara os cinco; as outras quatro
    # tem chave unica (WIS, CHA, INT, INT) e o motor a aplica sozinho.
    "Champion":     ["str", "str", "str", "dex", "con"],  # STR +3 DEX +1 CON +1
    "Druid":        ["str", "str", "dex", "con"],         # + WIS da chave
    "Sorcerer":     ["str", "str", "dex", "con"],         # + CHA da chave
    "Alchemist":    ["str", "str", "dex", "con"],         # + INT da chave
    "Investigator": ["str", "str", "dex", "con"],         # + INT da chave
}


def personagem_equivalente(base: Base, classe: str, nivel: int) -> Personagem:
    cid, ancestria, background = DEFAULT[classe]
    escolhas = [
        {"em": "criacao", "slot": "ancestralidade", "pega": ancestria},
        {"em": "criacao", "slot": "background", "pega": background},
    ]
    boosts = BOOSTS_DO_PATHBUILDER.get(classe)
    if boosts:
        escolhas.append({"em": "criacao", "slot": "boosts_livres", "pega": boosts})
    for n in range(1, nivel + 1):
        escolhas.append({"em": n, "slot": "nivel_de_classe", "pega": cid})
    # PERICIA NAO ENTRA, e isso e achado e nao esquecimento: a primeira medicao
    # disse que o Pathbuilder nascia com Acrobatics, Athletics, Stealth e
    # Thievery treinadas, e ERA BUG DA SONDA -- ela chamava de "treinada" toda
    # linha com bonus != 0, e em PF2e pericia sem treino ainda soma o
    # modificador do atributo. O icone de proficiencia e o breakdown da ficha
    # (`Prof 0`) provam que estao untrained. Do lado dele TODA escolha de pericia
    # continua pendente, igual ao nosso. Logo a familia de divergencia por
    # pericia NAO e bancada: e a diferenca de modelo declarada -- ele conta
    # escolha pendente como alcancavel, nos avaliamos o estado atual e MARCAMOS.
    return Personagem({"esquema": "waybuilder/personagem@1", "escolhas": escolhas}, base)


# O Pathbuilder renomeia o que a Paizo nao renomeou -- sai o nome proprio de
# Golarion, entra um generico (`Jalmeri Heavenseeker` -> `Heavenseeker`). Nao e
# remaster: a ponte `remaster_id` do AoN nao registra nenhum desses pares, e os
# nomes deles nao existem em nenhum dos 43.686 docs do dump. Sem esta traducao
# a comparacao acusa 20 falsos positivos e esconde o que importa.
def carregar_equivalencias() -> dict:
    caminho = os.path.join(AQUI, "..", "docs", "comparacao",
                           "equivalencias-pathbuilder.json")
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as fh:
        dados = json.load(fh)
    # o nome DELES passa a valer pelo nosso
    return {norm(deles): norm(nosso) for nosso, deles in dados.get("pares", [])}


def norm(nome: str) -> str:
    """Nome comparavel entre os dois apps.

    Tres fontes de ruido, todas medidas no primeiro relatorio e nenhuma delas
    divergencia de regra:

      - o sufixo de desambiguacao que NOS colocamos ao desmembrar colisao de
        identidade: `Guardian's Deflection (Fighter)` e o mesmo feat que o
        `Guardian's Deflection` deles;
      - apostrofo tipografico e caixa: `Needle In The God's Eyes` x
        `Needle in the Gods' Eyes`;
      - pontuacao solta.

    Sem isto o relatorio enche de falso positivo e esconde o achado real.
    """
    texto = re.sub(r"\s*\([^)]*\)\s*$", "", str(nome or ""))
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace("\u2019", "").replace("'", "")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", texto.casefold()).split())


# O modal do Pathbuilder tem abas, e cada uma recorta um pedaco do MESMO slot.
# Comparar a lista inteira contra a nossa mente nos dois sentidos, entao cada
# aba e comparada com o subconjunto equivalente dos nossos candidatos.
#
# `Archetype Class Feats` fica VAZIA enquanto o personagem nao tem dedicacao --
# e ai esta a diferenca de design, nao um defeito: pelo principio zero nos
# mostramos esses feats marcados, e o Pathbuilder os esconde ate a dedicacao
# existir. Por isso ela nao entra na comparacao com placar.
def _traits(r):
    return {str(t).lower() for t in (r.get("traits") or [])}


ABAS = {
    # trait da classe E sem `archetype`: os 11 feats de mascara do Wizard
    # (Pathfinder #174) carregam `wizard` junto com `archetype`, e o Pathbuilder
    # os poe na aba de arquetipo. Sem o `and not`, eles apareciam como sobra
    # nossa na aba de classe -- recorte diferente, nao defeito.
    "Class Feats": lambda base, p, r: bool(
        _traits(r) & {str(base.get(c).get("name") or "").lower()
                      for c in p.ordem_de_classe}) and "archetype" not in _traits(r),
    "Dedication Feats": lambda base, p, r: "dedication" in _traits(r),
    # `and not archetype` pela MESMA razao da aba de classe, e o esquecimento
    # aqui custou 118 falsos positivos numa rodada de Rogue 8: 24 feats de
    # Player Core 2 carregam `archetype` E `skill` juntos (Linguist, Dandy,
    # Acrobat...), e o Pathbuilder os poe na aba de Arquetipo. Nos os
    # oferecemos no slot de pericia -- e isso esta CERTO pelo RAW, desde que
    # haja a dedicacao --, mas nao e o recorte da aba dele.
    "Skill Feats": lambda base, p, r: (
        "skill" in _traits(r) and "archetype" not in _traits(r)),
    "General Feats": lambda base, p, r: (
        "general" in _traits(r) and "skill" not in _traits(r)
        and "archetype" not in _traits(r)),
    # `All Feats` fica de FORA do placar: ela nao recorta nada do lado deles, e
    # do nosso o slot de class feat aceita todo feat de arquetipo (RAW), entao a
    # comparacao virava 2.253 contra 341 -- ruido pelo desenho, nao achado.
}


def comparar(base: Base, sonda: dict, aba: str | None = None) -> dict:
    p = personagem_equivalente(base, sonda["classe"], sonda["nivel"])
    todos = p.candidatos(sonda["slot"], sonda["nivel"])
    if aba:
        cabe = ABAS[aba]
        todos = [c for c in todos if cabe(base, p, base.opcional(c["id"]) or {})]
    equiv = carregar_equivalencias()
    # ALIAS tambem casa. A fusao legacy/remaster guarda o nome antigo em
    # `aliases` (`Drow Shootist Dedication` -> `Crossbow Infiltrator
    # Dedication`, renomeado pela Paizo), e sem isso o comparador acusa como
    # buraco nosso um registro que temos com o nome NOVO -- que e o certo.
    nossos, chaves_de = {}, {}
    # `nossos` guarda UM registro por chave, e `todos_da_chave` guarda todos.
    # A diferenca importa: 75 chaves da base normalizam igual, envolvendo 205
    # feats -- `Incredible Familiar`, `(Animist)` e `(Familiar Master)` viram a
    # mesma chave --, e ate 2026-07-31 o laco de divergencia so olhava o
    # primeiro. Os outros contavam como casados sem nunca ser comparados.
    # Spec: `specs/2026-07-31-colisao-no-comparador.md`
    todos_da_chave = collections.defaultdict(list)
    for c in todos:
        reg = base.opcional(c["id"]) or {}
        chaves = {norm(c["nome"])} | {norm(a) for a in (reg.get("aliases") or [])}
        chaves_de[c["id"]] = chaves
        for chave in chaves:
            nossos.setdefault(chave, c)
            todos_da_chave[chave].append(c)
    deles = {}
    for o in (sonda.get("abas", {}).get(aba) if aba else sonda["opcoes"]):
        chave = norm(o["nome"])
        deles[equiv.get(chave, chave)] = o

    # Um candidato casa se QUALQUER chave sua (nome canonico ou alias) aparece
    # do outro lado. Duas armadilhas ja cometidas aqui:
    #   - contar chaves em vez de registros faz quem casou pelo alias aparecer
    #     como sobra pelo nome canonico;
    #   - guardar so o primeiro registro de cada chave faz o DESMEMBRADO
    #     (`Dueling Dance (Fighter)`, criado por colisao de identidade) virar
    #     sobra, quando o irmao dele ja casou pelo mesmo nome.
    casadas = nossos.keys() & deles.keys()
    vistos, so_nossos = set(), []
    for c in todos:
        if chaves_de[c["id"]] & casadas or c["nome"] in vistos:
            continue
        vistos.add(c["nome"])
        so_nossos.append(c["nome"])
    so_nossos.sort()
    so_deles = sorted(deles[k]["nome"] for k in deles.keys() - nossos.keys())

    divergem, colisoes = [], []
    for k in nossos.keys() & deles.keys():
        # todos os NOSSOS registros que caem nesta chave, sem repetir quem
        # entrou por nome e por alias (`Crossbow Infiltrator Dedication` tem o
        # nome antigo `Drow Shootist Dedication` em `aliases`, e saia duplicado).
        grupo, vistos_id = [], set()
        for c in todos_da_chave[k]:
            if c["id"] not in vistos_id:
                vistos_id.add(c["id"])
                grupo.append(c)
        if len({c["nome"] for c in grupo}) > 1:
            # a colisao vai DECLARADA no relatorio. Truncar cobertura em
            # silencio faz o placar dizer "cobri tudo" quando nao cobriu.
            colisoes.append({"chave": k,
                             "nossos": sorted({c["nome"] for c in grupo}),
                             "pathbuilder": deles[k]["nome"]})
        # `ja_pego` do nosso lado explica o "nao atende" do lado deles sem ser
        # divergencia de regra: `Hobnobber` vem do background Barkeep, e o
        # Pathbuilder marca em vermelho o que o personagem ja tem
        elegiveis = [c for c in grupo
                     if not (c["ja_pego"] and not deles[k]["atende"])]
        if not elegiveis:
            continue
        # O veredito e do GRUPO, nao do primeiro registro. Quando a colisao e
        # desmembramento nosso (`Animal Companion` do Druida e
        # `Animal Companion (Ranger)`), UM dos irmaos e o par legitimo da
        # entrada deles -- se ele concorda, nao ha divergencia, e cobrar do
        # outro irmao fabricaria falso positivo. So ha divergencia quando
        # NENHUM dos nossos concorda, e ai ela sai nomeando todos.
        if any(c["atende"] == deles[k]["atende"] for c in elegiveis):
            continue
        divergem.append({
            "nome": " / ".join(sorted({c["nome"] for c in elegiveis})),
            "waybuilder": elegiveis[0]["atende"],
            "pathbuilder": deles[k]["atende"],
            "motivos": elegiveis[0]["motivos"],
        })
    divergem.sort(key=lambda d: d["nome"])
    colisoes.sort(key=lambda c: c["chave"])

    return {
        "slot": f"{sonda['classe']} {sonda['nivel']} / {sonda['slot']}"
                + (f" [{aba}]" if aba else ""),
        "waybuilder": len(todos), "pathbuilder": len(deles),
        "em_comum": len(casadas),
        "so_no_pathbuilder": so_deles,
        "so_no_waybuilder": so_nossos,
        "divergencia_de_disponibilidade": divergem,
        "colisoes_de_normalizacao": colisoes,
    }


def main() -> int:
    alvos = sys.argv[1:] or sorted(glob.glob(
        os.path.join(AQUI, "..", "docs", "comparacao", "pathbuilder-*.json")))
    if not alvos:
        print("nenhum JSON de sonda -- rode app/verificacao/sonda-pathbuilder.mjs")
        return 1

    base = Base()
    problemas = 0
    for caminho in alvos:
        with open(caminho, encoding="utf-8") as fh:
            sonda = json.load(fh)
        # o glob `pathbuilder-*.json` e um contrato frouxo: qualquer outro
        # artefato colhido do mesmo app cai nele e estoura aqui com KeyError.
        # Aconteceu com a sonda de ESTADO (atributos e pericias da ficha), que
        # tem outro schema. Arquivo sem `classe` nao e sonda de slot -- pula.
        if "classe" not in sonda:
            continue
        if sonda["classe"] not in DEFAULT:
            print(f"pulado (classe sem equivalente montado): {sonda['classe']}")
            continue

        relatorios = ([comparar(base, sonda, aba) for aba in ABAS
                       if aba in (sonda.get("abas") or {})]
                      or [comparar(base, sonda)])
        for r in relatorios:
            problemas += imprimir(r)

        saida = caminho.replace("pathbuilder-", "comparacao-")
        with open(saida, "w", encoding="utf-8") as fh:
            json.dump(relatorios, fh, ensure_ascii=False, indent=2)
        print(f"   -> {os.path.relpath(saida)}")
    print(f"\ntotal de pontos a olhar: {problemas}")
    return 0


def imprimir(r: dict) -> int:
    """Imprime um relatorio e devolve quantos pontos ele levanta."""
    problemas = 0
    print(f"\n== {r['slot']}")
    print(f"   waybuilder {r['waybuilder']} | pathbuilder {r['pathbuilder']} "
          f"| em comum {r['em_comum']}")
    for chave, rotulo in (("so_no_pathbuilder", "so no Pathbuilder"),
                          ("so_no_waybuilder", "so no Waybuilder")):
        itens = r[chave]
        if itens:
            problemas += len(itens)
            print(f"   {rotulo} ({len(itens)}): {', '.join(itens[:12])}"
                  + (" ..." if len(itens) > 12 else ""))
    if r["divergencia_de_disponibilidade"]:
        problemas += len(r["divergencia_de_disponibilidade"])
        print(f"   discordam se atende ({len(r['divergencia_de_disponibilidade'])}):")
        for d in r["divergencia_de_disponibilidade"][:10]:
            print(f"     {d['nome']}: wb={d['waybuilder']} pb={d['pathbuilder']}"
                  + (f"  -- {d['motivos'][0]}" if d["motivos"] else ""))
    return problemas


if __name__ == "__main__":
    sys.exit(main())
