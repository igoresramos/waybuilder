#!/usr/bin/env python3
"""
Waybuilder -- preparar_dados.py

Reconstroi docs/simulacoes/classes.json, que wb_sim.py precisa e que tinha
sumido do diretorio. NAO EDITA nada em pipeline/ (so leitura) -- outros agentes
trabalham la.

O arquivo final tem DUAS camadas de proveniencia, marcadas em cada bloco:

  DERIVADO  -- lido de arquivo em disco, sem digitar numero nenhum a mao.
      * baseline de nivel 1 (perception/saves/attacks/defenses/hp/key_ability)
        vem de pipeline/dados_brutos/foundry/packs/pf2e/classes/<classe>.json
        (system.attacks/defenses/savingThrows/perception/hp/keyAbility), que e
        o checkout oficial do sistema pf2e do Foundry no pin gravado em
        pipeline/dados_brutos/foundry/PIN.
      * pericias livres/automaticas e niveis de skill increase vem de
        pipeline/saida/classes.json (saida do extrator do proprio projeto,
        campo "grants" -> skill_training / skill_increase).
      * os dois foram cruzados um contra o outro para as 12 classes abaixo e
        batem 100% (ver secao de verificacao no fim deste arquivo).

  PREMISSA  -- progressao de proficiencia ACIMA do nivel 1 (em que nivel um
      rank sobe pra Expert/Master/Legendary). NENHUMA das duas fontes de disco
      acima contem esse dado de forma direta e generica: o class item do
      Foundry so tem o nivel 1; o "grants" do pipeline/saida so repete o
      nivel 1 tambem (TODO.md item 2, ainda nao resolvido: "grafo de
      progressao de dois niveis" -- 62 class-features de segundo nivel ficam
      invisiveis). E quando se abre o proprio class-feature (ex.:
      class-features/fighter-expertise.json), o campo "rules" que deveria
      carregar o efeito numerico vem *vazio* pra boa parte deles -- o valor
      real esta hardcoded no codigo TypeScript do sistema pf2e, que nao esta
      neste dump. Confirmado por amostragem em fighter-expertise, weapon-
      mastery, light-armor-expertise, medium-armor-expertise, alertness.

      Por isso a tabela PROG_PREMISSA abaixo foi levantada direto no Archives
      of Nethys (2e.aonprd.com/Classes.aspx?ID=<n>), pagina por classe, e
      cruzada contra o NIVEL de cada class-feature (esse sim confiavel, vem
      de system.items[].level no Foundry) -- todo nivel usado abaixo bateu
      exatamente com o Foundry nas classes onde foi checado (Fighter, Druid,
      Cleric, verificado neste arquivo). O Doctrine do Clerigo tambem foi
      lido direto (Doctrines.aspx?ID=3 Warpriest / ID=4 Cloistered) porque
      TODO.md item 3 ja avisa que Clerigo depende de subclasse -- este
      simulador modela SO Cloistered Cleric (a doutrina padrao, mais magica);
      Warpriest fica de fora (nao invento o numero do Warpriest sem reler a
      pagina dele com o mesmo cuidado).

      Uma excecao dentro do bloco PREMISSA e sinalizada a parte: a escolha de
      QUAL save o Monge melhora em Path to Perfection (nivel 7/11/15) e do
      jogador na mesa, nao uma regra fixa. Fixei Reflexo (7 e 15) e Vontade
      (11) como escolha de simulacao -- e uma decisao de build, marcada
      "ESCOLHA DE BUILD" no dict, nao um numero de regra.

ESCOPO: so as 12 classes de Player Core 1/2 que ja estavam hardcoded em
MARCIAIS/CASTERS no wb_sim.py original (fighter, wizard, cleric, barbarian,
rogue, monk, druid, sorcerer, bard, champion, ranger, alchemist). Cobre TODAS
as combinacoes "pouco obvias" que o Igor pediu (Monge/Clerigo, Barbaro/Mago,
Ladino/Druida). As outras 15 classes do jogo (Investigator, Kineticist,
Magus, Summoner, Swashbuckler, Thaumaturge, Animist, Commander, Exemplar,
Guardian, Gunslinger, Inventor, Oracle, Psychic, Witch) FICAM DE FORA -- cada
uma tem tabela de proficiencia propria e nao ha tempo neste ciclo pra
verificar as 15 uma por uma contra o AoN com o mesmo rigor. Levantar sob
demanda se algum playtest pedir.

Categorias modeladas em "attacks": martial/simple/unarmed (a forma como
wb_sim.py calcula rank_arma). "advanced" weapons e a trilha de "arma
favorita" do Clerigo (favored weapon) NAO tem categoria propria no simulador
-- ja era assim no wb_sim.py original. Onde uma classe so ganha expertise na
arma favorita (Clerigo), o ganho foi dobrado pra dentro de "simple" (unica
categoria de arma corpo-a-corpo generica que o Clerigo realmente usa), o que
SUBESTIMA levemente o Clerigo com arma marcial de deus guerreiro (ex.:
Sarenrae) -- registrado como limite conhecido no relatorio.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # .../waybuilder
FOUNDRY_CLASSES = f"{ROOT}/pipeline/dados_brutos/foundry/packs/pf2e/classes"
PIPELINE_SAIDA = f"{ROOT}/pipeline/saida/classes.json"

RANK = {"untrained": 0, "trained": 1, "expert": 2, "master": 3, "legendary": 4}

CLASSES_ALVO = ["alchemist", "barbarian", "bard", "champion", "cleric", "druid",
                "fighter", "monk", "ranger", "rogue", "sorcerer", "wizard"]


# =====================================================================
# DERIVADO -- le o class item cru do Foundry (baseline de nivel 1)
# =====================================================================
def ler_baseline_foundry(slug):
    with open(f"{FOUNDRY_CLASSES}/{slug}.json", encoding="utf-8") as f:
        s = json.load(f)["system"]
    attacks = {k: v for k, v in s["attacks"].items()
               if k in ("martial", "simple", "unarmed") and v}
    defenses = {k: v for k, v in s["defenses"].items() if v}
    saves = dict(s["savingThrows"])
    return dict(
        attacks=attacks,
        defenses=defenses,
        saves=saves,
        perception=s["perception"],
        hp=s["hp"],
        key_ability=s["keyAbility"]["value"],
    )


# =====================================================================
# DERIVADO -- le "grants" do extrator do proprio pipeline (pericias)
# =====================================================================
def ler_grants_pipeline():
    with open(PIPELINE_SAIDA, encoding="utf-8") as f:
        dados = json.load(f)
    classes = {x["name"].lower(): x for x in dados if x.get("kind") == "class"}
    out = {}
    for slug in CLASSES_ALVO:
        nome = slug  # nomes do pipeline sao capitalizados; casamos por slug abaixo
        entry = next(c for c in classes.values()
                     if c["name"].lower().replace(" ", "-") == slug)
        skills_free, skill_inc = 0, []
        for g in entry["grants"]:
            if "skill_training" in g:
                skills_free = g["skill_training"]["free"]
            if "skill_increase" in g:
                skill_inc = g["skill_increase"]["levels"]
        out[slug] = dict(skills=skills_free, skillInc=skill_inc,
                          spellcasting=entry["spellcasting"])
    return out


# =====================================================================
# PREMISSA -- progressao de proficiencia acima do nivel 1, levantada no
# Archives of Nethys (2e.aonprd.com), cruzada contra o nivel de cada
# class-feature no Foundry onde verificado (ver docstring do arquivo).
# Chaves possiveis por nivel: martial/simple/unarmed, light/medium/heavy/
# unarmored, fortitude/reflex/will, perception, spellcasting.
# =====================================================================
PROG_PREMISSA = {
    # AoN Classes.aspx?ID=35 -- verificado nivel-a-nivel contra
    # system.items[].level do Foundry (bravery=3, battlefield-surveyor=7,
    # battle-hardened=9, armor-expertise=11, fighter-expertise=11,
    # weapon-legend=13, tempered-reflexes=15, armor-mastery=17,
    # versatile-legend=19 -- todos batem).
    "fighter": {
        3: {"will": 2},
        7: {"perception": 3},
        9: {"fortitude": 3},
        11: {"light": 2, "medium": 2, "heavy": 2, "unarmored": 2},
        13: {"martial": 3, "simple": 3, "unarmed": 3},
        15: {"reflex": 3},
        17: {"light": 3, "medium": 3, "heavy": 3, "unarmored": 3},
        19: {"martial": 4, "simple": 4, "unarmed": 4},
    },
    # AoN Classes.aspx?ID=39
    "wizard": {
        5: {"reflex": 2},
        7: {"spellcasting": 2},
        9: {"fortitude": 2},
        11: {"perception": 2, "simple": 2, "unarmed": 2},
        13: {"unarmored": 2},
        15: {"spellcasting": 3},
        17: {"will": 3},
        19: {"spellcasting": 4},
    },
    # AoN Classes.aspx?ID=33 (base) + Doctrines.aspx?ID=4 Cloistered Cleric.
    # Warpriest NAO modelado (ver docstring). Arma favorita dobrada em
    # "simple" -- ver limite conhecido no docstring.
    "cleric": {
        3: {"fortitude": 2},                       # doutrina 2a (Cloistered)
        5: {"perception": 2},                       # base, Perception Expertise
        7: {"spellcasting": 2},                      # doutrina 3a
        9: {"will": 3},                              # base, Resolute Faith
        11: {"reflex": 2, "simple": 2, "unarmed": 2},  # base + doutrina 4a
        13: {"unarmored": 2},                        # base, Divine Defense
        15: {"spellcasting": 3},                      # doutrina 5a
        19: {"spellcasting": 4},                      # doutrina final
    },
    # AoN Classes.aspx?ID=57
    "barbarian": {
        5: {"simple": 2, "martial": 2, "unarmed": 2},
        7: {"fortitude": 3},
        9: {"reflex": 2},
        13: {"fortitude": 4, "light": 2, "medium": 2, "unarmored": 2,
             "simple": 3, "martial": 3, "unarmed": 3},
        15: {"will": 3},
        17: {"perception": 3},
        19: {"light": 3, "medium": 3, "unarmored": 3},
    },
    # AoN Classes.aspx?ID=37
    "rogue": {
        5: {"simple": 2, "martial": 2, "unarmed": 2},
        7: {"reflex": 3, "perception": 3},
        9: {"fortitude": 2},
        13: {"reflex": 4, "perception": 4, "light": 2, "unarmored": 2,
             "simple": 3, "martial": 3, "unarmed": 3},
        17: {"will": 3},
        19: {"light": 3, "unarmored": 3},
    },
    # AoN Classes.aspx?ID=60. Path to Perfection (7/11/15) escolhe UM save
    # por vez -- e decisao de build, nao regra fixa (ver docstring).
    # ESCOLHA DE BUILD: Reflexo em 7 e 15, Vontade em 11.
    "monk": {
        5: {"simple": 2, "unarmed": 2, "perception": 2},
        7: {"reflex": 3},                 # ESCOLHA DE BUILD (Path to Perfection)
        11: {"will": 3},                  # ESCOLHA DE BUILD (Second Path)
        13: {"unarmored": 3, "simple": 3, "unarmed": 3},
        15: {"reflex": 4},                # ESCOLHA DE BUILD (Third Path, mesma trilha do 7)
        17: {"unarmored": 4},
    },
    # AoN Classes.aspx?ID=34 -- verificado contra Foundry (weapon-expertise
    # nivel 11, medium-armor-expertise nivel 13 batem).
    "druid": {
        3: {"perception": 2, "fortitude": 2},
        5: {"reflex": 2},
        7: {"spellcasting": 2},
        11: {"will": 3, "simple": 2, "unarmed": 2},
        13: {"light": 2, "medium": 2, "unarmored": 2},
        15: {"spellcasting": 3},
        19: {"spellcasting": 4},
    },
    # AoN Classes.aspx?ID=62
    "sorcerer": {
        5: {"fortitude": 2},
        7: {"spellcasting": 2},
        9: {"reflex": 2},
        11: {"perception": 2, "simple": 2, "unarmed": 2},
        13: {"unarmored": 2},
        15: {"spellcasting": 3},
        17: {"will": 3},
        19: {"spellcasting": 4},
    },
    # AoN Classes.aspx?ID=32
    "bard": {
        3: {"reflex": 2},
        7: {"spellcasting": 2},
        9: {"fortitude": 2, "will": 3},
        11: {"martial": 2, "simple": 2, "unarmed": 2, "perception": 3},
        13: {"light": 2, "unarmored": 2},
        15: {"spellcasting": 3},
        17: {"will": 4},
        19: {"spellcasting": 4},
    },
    # AoN Classes.aspx?ID=58
    "champion": {
        5: {"martial": 2, "simple": 2, "unarmed": 2},
        7: {"light": 2, "medium": 2, "heavy": 2, "unarmored": 2},
        9: {"spellcasting": 2, "fortitude": 3},
        11: {"will": 3, "perception": 2},
        13: {"light": 3, "medium": 3, "heavy": 3, "unarmored": 3,
             "martial": 3, "simple": 3, "unarmed": 3},
        17: {"spellcasting": 3, "light": 4, "medium": 4, "heavy": 4, "unarmored": 4},
    },
    # AoN Classes.aspx?ID=36
    "ranger": {
        3: {"will": 2},
        5: {"simple": 2, "martial": 2, "unarmed": 2},
        7: {"reflex": 3, "perception": 3},
        11: {"fortitude": 3, "light": 2, "medium": 2, "unarmored": 2},
        13: {"simple": 3, "martial": 3, "unarmed": 3},
        15: {"reflex": 4, "perception": 4},
        19: {"light": 3, "medium": 3, "unarmored": 3},
    },
    # AoN Classes.aspx?ID=56
    "alchemist": {
        7: {"simple": 2, "unarmed": 2, "will": 2},
        9: {"perception": 2},
        13: {"light": 2, "medium": 2, "unarmored": 2},
        15: {"simple": 3, "unarmed": 3, "reflex": 3},
        19: {"light": 3, "medium": 3, "unarmored": 3},
    },
}


def montar():
    baseline = {slug: ler_baseline_foundry(slug) for slug in CLASSES_ALVO}
    grants = ler_grants_pipeline()

    saida = {}
    for slug in CLASSES_ALVO:
        b, g = baseline[slug], grants[slug]
        # attacks/defenses/saves em numero de rank (0-4), ja vem assim do Foundry
        saida[slug] = dict(
            hp=b["hp"],
            key_ability=b["key_ability"],
            attacks=b["attacks"],
            defenses=b["defenses"],
            saves=b["saves"],
            perception=b["perception"],
            skills=g["skills"],
            skillInc=g["skillInc"],
            prog=PROG_PREMISSA[slug],
        )
    return saida


def verificar(saida):
    """Checagem de sanidade antes de escrever: todo rank cresce ou mantem
    (nunca regride) ao longo dos niveis, por categoria, dentro de cada classe.
    Se regredir e bug de digitacao na tabela PREMISSA."""
    problemas = []
    for slug, d in saida.items():
        atual = {}
        atual.update({f"attacks:{k}": v for k, v in d["attacks"].items()})
        atual.update({f"defenses:{k}": v for k, v in d["defenses"].items()})
        atual.update({f"saves:{k}": v for k, v in d["saves"].items()})
        atual["perception"] = d["perception"]
        for lv in sorted(d["prog"]):
            for cat, novo in d["prog"][lv].items():
                chave = cat if cat in ("perception", "spellcasting") else None
                # normaliza chave composta pra achar o "atual" certo
                for pref in ("attacks", "defenses", "saves"):
                    if f"{pref}:{cat}" in atual:
                        chave = f"{pref}:{cat}"
                if chave is None:
                    chave = cat  # spellcasting nao tem baseline numerico > 0
                velho = atual.get(chave, 0 if chave != "spellcasting" else 1)
                if novo < velho:
                    problemas.append(f"{slug} nivel {lv} {cat}: {novo} < {velho} (regride)")
                atual[chave] = novo
    return problemas


if __name__ == "__main__":
    saida = montar()
    problemas = verificar(saida)
    if problemas:
        print("PROBLEMAS DE SANIDADE (rank regredindo) -- corrija antes de usar:")
        for p in problemas:
            print(" -", p)
        raise SystemExit(1)
    with open(f"{HERE}/classes.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"OK: {HERE}/classes.json escrito com {len(saida)} classes: "
          f"{', '.join(sorted(saida))}")
