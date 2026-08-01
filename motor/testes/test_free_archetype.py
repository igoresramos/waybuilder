#!/usr/bin/env python3
"""Testes do slot de Free Archetype (regra 2, sempre ligada).

Cada caso sai de uma ficha real em `motor/exemplos/`, nao de documento
inventado dentro do teste -- assim a mesma evidencia pode ser lida com
`python3 ficha.py exemplos/<arquivo>.json` sem passar pelo unittest.

O que estes testes travam:

  1  o slot de Free Archetype so aceita feat de ARQUETIPO
  2  a primeira coisa de um arquetipo tem de ser a Dedication
  3  nova dedicacao so depois de 2 feats do arquetipo anterior (RAW)
  4  regra 23: dedicacao de multiclasse da propria classe e vetada
  5  o slot e em nivel PAR e NAO consome o slot de class feat

PRINCIPIO ZERO: `requires` sugere e ORDENA, nunca bloqueia. Entao "sinalizar"
aqui quer dizer aparecer em `fora_do_requisito` (ou em `avisos`) -- nenhum
teste exige que o motor recuse a escolha, e um teste que exigisse estaria
errado.

Os casos que o motor ainda NAO trata estao marcados com
`@unittest.expectedFailure`: eles descrevem o comportamento CERTO, ficam
vermelhos por dentro sem sujar a suite, e viram `unexpected success` no dia em
que o motor implementar a regra -- que e exatamente o sinal desejado.

Rodar: python3 -m unittest discover -s motor/testes -t .
"""
import importlib.util
import json
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
EXEMPLOS = os.path.join(MOTOR, "exemplos")

# O `discover -t .` importa este arquivo como `motor.testes.test_free_archetype`,
# e com isso `motor` ja fica em sys.modules como PACOTE (o diretorio). Um
# `from motor import Base` traria o diretorio, nao o motor.py. Por isso o
# modulo e carregado pelo caminho do arquivo, sem depender do sys.path.
_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(MOTOR, "motor.py"))
wb_motor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb_motor)

BASE = wb_motor.Base()

ARCHER_DEDICATION = "wb:feat/archer-dedication"
FIGHTER_DEDICATION = "wb:feat/fighter-dedication"
QUICK_SHOT = "wb:feat/quick-shot"


def carregar(nome: str, mutacao=None) -> "wb_motor.Personagem":
    """Le uma ficha de `motor/exemplos/`. `mutacao` recebe o doc e pode
    altera-lo antes de derivar -- usado para montar o par 'com e sem' sem
    precisar de um segundo arquivo so pra isso."""
    with open(os.path.join(EXEMPLOS, nome), encoding="utf-8") as fh:
        doc = json.load(fh)
    if mutacao:
        mutacao(doc)
    return wb_motor.Personagem(doc, BASE)


def motivos(p) -> list[str]:
    return [f"{f['feat']}: {f['motivo']}" for f in p.fora_do_requisito]


# Um aviso QUALQUER nao serve de prova: o motor avisa de muita coisa que nao
# tem nada a ver com o trilho de arquetipo (cadeia de grants, subclasse por
# escolher, boost de nivel futuro). Sem este filtro, um aviso novo vindo de
# outra parte do motor faria um teste de lacuna passar por acidente -- foi o
# que aconteceu com `natural-ambition` na primeira versao destes testes.
ASSUNTO = ("arquetipo", "archetype", "dedica", "dedication", "slot")


def sinal_de_arquetipo(p) -> list[str]:
    """Sinais -- `fora_do_requisito` mais `avisos` -- que falam do trilho de
    arquetipo. E este o vocabulario do principio zero: sinalizar."""
    return [m for m in motivos(p) + list(p.avisos)
            if any(k in m.lower() for k in ASSUNTO)]


def picks_de_arquetipo(p) -> list[str]:
    return [e["pega"] for e in p.doc["escolhas"] if e.get("slot") == "free_archetype"]


def feat(wb_id: str) -> dict:
    return BASE.get(wb_id)


def e_de_arquetipo(wb_id: str) -> bool:
    """A pergunta do ponto 1, respondida so com dado que a base ja tem."""
    return "archetype" in (feat(wb_id).get("traits") or [])


def arquetipo_de(wb_id: str) -> str | None:
    return feat(wb_id).get("archetype")


def e_dedicacao(wb_id: str) -> bool:
    return "dedication" in (feat(wb_id).get("traits") or [])


# -- ponto 5: o slot existe, e par, e nao come o slot de classe -------------

class TestSlotDeFreeArchetype(unittest.TestCase):
    """Regra 2 + regra 12: o trilho gratuito e paralelo ao de class feat."""

    def setUp(self):
        self.p = carregar("guerreiro4-fa-archer.json")

    def test_slot_so_em_nivel_par(self):
        self.assertEqual(self.p.slots["free_archetype"], [2, 4])
        self.assertEqual(carregar("guerreiro6-fa-duas-dedicacoes.json")
                         .slots["free_archetype"], [2, 4, 6])

    def test_slot_acompanha_o_nivel_de_personagem_nao_o_de_classe(self):
        # o dobro de classes nao dobra nem divide o trilho: e por personagem
        p = carregar("guerreiro4-fa-archer.json", lambda d: [
            e.update({"pega": "wb:class/wizard"})
            for e in d["escolhas"]
            if e.get("slot") == "nivel_de_classe" and e["em"] in (3, 4)])
        self.assertEqual(p.nivel, 4)
        self.assertEqual(p.slots["free_archetype"], [2, 4])

    def test_free_archetype_nao_consome_o_slot_de_class_feat(self):
        sem_fa = carregar("guerreiro4-fa-archer.json", lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "free_archetype"]))
        self.assertEqual(self.p.slots["class"], sem_fa.slots["class"])
        self.assertEqual(len(self.p.gastos["class_feat"]),
                         len(sem_fa.gastos["class_feat"]))
        # os dois trilhos ficam cheios ao mesmo tempo, cada um no proprio balde
        self.assertEqual(len(self.p.gastos["class_feat"]), 3)      # niveis 1, 2, 4
        self.assertEqual(len(self.p.gastos["free_archetype"]), 2)  # niveis 2, 4

    def test_dedicacao_no_slot_gratuito_nao_vira_class_feat(self):
        pegos = [e["pega"] for e in self.p.gastos["class_feat"]]
        self.assertNotIn(ARCHER_DEDICATION, pegos)
        self.assertIn(ARCHER_DEDICATION, picks_de_arquetipo(self.p))


# -- ponto 2: a Dedication vem primeiro ------------------------------------

class TestDedicacaoPrimeiro(unittest.TestCase):
    """Sem a dedicacao do arquetipo, nenhum feat dele deveria estar em ordem."""

    def test_ordem_certa_nao_gera_sinal(self):
        p = carregar("guerreiro4-fa-archer.json")
        self.assertEqual(p.fora_do_requisito, [], motivos(p))

    def test_feat_do_arquetipo_sem_dedicacao_e_sinalizado(self):
        # o `requires` de Quick Shot cita `has: archer-dedication`, entao o
        # predicado sozinho ja resolve o caso
        p = carregar("guerreiro4-fa-avancado-sem-dedicacao.json")
        self.assertTrue(any("Archer Dedication" in m for m in motivos(p)), motivos(p))

    def test_sinaliza_mas_nao_bloqueia(self):
        """Principio zero: a escolha continua no documento e a ficha deriva."""
        p = carregar("guerreiro4-fa-avancado-sem-dedicacao.json")
        self.assertIn(QUICK_SHOT, picks_de_arquetipo(p))
        self.assertEqual(len(p.gastos["free_archetype"]), 1)
        self.assertGreater(p.hp, 0)

    def test_feat_de_arquetipo_sem_has_no_requires(self):
        """Barbarian Resiliency exige Barbarian Dedication no RAW, mas o
        `requires` da base so traz `character_level >= 4` -- sao 181 feats de
        arquetipo nessa situacao. `_exige_a_dedicacao_do_arquetipo` deduz do
        dado que ja existe: `feat["archetype"]` aponta o arquetipo e a
        dedicacao dele e achavel por trait."""
        p = carregar("guerreiro4-fa-lacuna-dedicacao.json")
        self.assertTrue(any("edication" in m for m in motivos(p)), motivos(p))

    def test_o_dado_sustenta_a_checagem_que_falta(self):
        """Prova de que o conserto e barato: o vinculo feat -> arquetipo ja
        esta na base, nao precisa de lista escrita a mao."""
        self.assertEqual(arquetipo_de("wb:feat/barbarian-resiliency"),
                         "wb:archetype/barbarian")
        self.assertEqual(arquetipo_de(ARCHER_DEDICATION), "wb:archetype/archer")
        self.assertTrue(e_dedicacao(ARCHER_DEDICATION))
        self.assertFalse(e_dedicacao("wb:feat/barbarian-resiliency"))

    def test_ordem_no_tempo_e_conferida(self):
        """Era LACUNA ate 29/07: `has` olhava o documento INTEIRO, nunca o que
        existia naquele nivel, e pegar Quick Shot no nivel 2 com a dedicacao no
        4 -- ordem ilegal -- passava limpo.

        O recorte temporal do `has` fechou o buraco
        (`specs/2026-07-29-recorte-temporal-do-has.md`), e o
        `@unittest.expectedFailure` ficou para tras: virou `unexpected
        success`, que e o sinal combinado no cabecalho deste arquivo para
        "a lacuna fechou, tire o marcador". Este e o ato de tirar."""
        def inverter(d):
            for e in d["escolhas"]:
                if e.get("slot") == "free_archetype":
                    e["em"] = 2 if e["pega"] == QUICK_SHOT else 4
        p = carregar("guerreiro4-fa-archer.json", inverter)
        self.assertTrue(sinal_de_arquetipo(p), "nada sinalizado")


# -- ponto 4: regra 23 ------------------------------------------------------

class TestRegra23DedicacaoDaPropriaClasse(unittest.TestCase):
    """Um Guerreiro nao pega Fighter Dedication. A exclusao e MUTUA."""

    def setUp(self):
        self.p = carregar("guerreiro4-fa-dedicacao-propria-classe.json")

    def test_sinaliza_nos_dois_sentidos(self):
        regra23 = [m for m in motivos(self.p) if "regra 23" in m]
        self.assertEqual(len(regra23), 2, motivos(self.p))
        self.assertTrue(any(m.startswith("Fighter Dedication") for m in regra23))
        self.assertTrue(any("nivel de classe" in m for m in regra23))

    def test_o_motivo_e_a_regra_23_e_nao_o_atributo(self):
        """A ficha foi montada com STR/DEX 14 de proposito: se o requisito de
        atributo tambem falhasse, o teste passaria pelo motivo errado."""
        self.assertGreaterEqual(self.p.atributos["str"], 14)
        self.assertGreaterEqual(self.p.atributos["dex"], 14)
        self.assertFalse([m for m in motivos(self.p) if "STR" in m or "DEX" in m])

    def test_sinaliza_mas_nao_bloqueia(self):
        self.assertIn(FIGHTER_DEDICATION, picks_de_arquetipo(self.p))
        self.assertEqual(self.p.nivel, 4)

    def test_dedicacao_de_outra_classe_nao_dispara_a_regra_23(self):
        """O veto e cirurgico: so a dedicacao DAQUELA classe."""
        p = carregar("guerreiro4-fa-dedicacao-propria-classe.json", lambda d: [
            e.update({"pega": "wb:feat/cleric-dedication"})
            for e in d["escolhas"]
            if e.get("slot") == "free_archetype"])
        self.assertFalse([m for m in motivos(p) if "regra 23" in m], motivos(p))

    def test_dedicacao_nao_multiclasse_nao_dispara_a_regra_23(self):
        p = carregar("guerreiro4-fa-archer.json")
        self.assertFalse([m for m in motivos(p) if "regra 23" in m], motivos(p))
        self.assertNotIn("multiclass", feat(ARCHER_DEDICATION).get("traits") or [])


# -- ponto 1: o slot so aceita feat de arquetipo ---------------------------

class TestSlotSoAceitaFeatDeArquetipo(unittest.TestCase):

    def test_o_dado_sustenta_a_checagem(self):
        self.assertTrue(e_de_arquetipo(ARCHER_DEDICATION))
        self.assertTrue(e_de_arquetipo(QUICK_SHOT))
        self.assertFalse(e_de_arquetipo("wb:feat/reactive-shield"))

    def test_class_feat_puro_passa_no_proprio_requisito(self):
        """Garante que o silencio do teste seguinte vem da checagem ausente, e
        nao de um requisito que por acaso reprovaria de qualquer jeito."""
        p = carregar("guerreiro4-fa-class-feat-no-slot.json")
        self.assertEqual(p.fora_do_requisito, [], motivos(p))

    def test_class_feat_no_slot_de_arquetipo_e_sinalizado(self):
        """Reactive Shield nao tem trait `archetype`. Ocupar um slot de Free
        Archetype com ele gera sinal -- `_higiene_de_slot` compara o tipo do
        feat com o slot que o recebeu."""
        p = carregar("guerreiro4-fa-class-feat-no-slot.json")
        self.assertTrue(sinal_de_arquetipo(p), "nada sinalizado")


# -- ponto 3: nova dedicacao exige 2 feats do arquetipo anterior -----------

class TestNovaDedicacaoExigeDoisFeats(unittest.TestCase):
    """RAW (Dedication trait): 'You can't select another dedication feat until
    you have gained two other feats from the archetype.'"""

    def test_o_dado_sustenta_a_contagem(self):
        p = carregar("guerreiro6-fa-duas-dedicacoes.json")
        por_arquetipo: dict[str, int] = {}
        for wb_id in picks_de_arquetipo(p):
            arq = arquetipo_de(wb_id)
            if arq and not e_dedicacao(wb_id):
                por_arquetipo[arq] = por_arquetipo.get(arq, 0) + 1
        # quando Marshal Dedication entra (nivel 4) o Archer tem ZERO feats
        # alem da propria dedicacao; no fim da ficha ainda so tem um
        self.assertEqual(por_arquetipo.get("wb:archetype/archer", 0), 1)
        self.assertLess(por_arquetipo.get("wb:archetype/archer", 0), 2)

    def test_segunda_dedicacao_sem_dois_feats(self):
        """Marshal Dedication entra no nivel 4 com zero feats de Archer
        acumulados. A regra nao esta no `requires` da base: veio do texto RAW
        do trait, conferido nas 76 dedicacoes que repetem a clausula."""
        p = carregar("guerreiro6-fa-duas-dedicacoes.json")
        self.assertTrue(any("dedica" in m.lower() for m in motivos(p)), motivos(p))


# -- higiene do slot: nivel e quantidade ------------------------------------

class TestHigieneDoSlot(unittest.TestCase):
    """O slot existe em [2, 4]; o motor confere se a escolha caiu neles?"""

    def test_escolha_em_nivel_impar_e_sinalizada(self):
        """Um pick de free_archetype no nivel 3 gera aviso: `_higiene_de_slot`
        confronta `gastos` com `slots`."""
        def para_impar(d):
            for e in d["escolhas"]:
                if e.get("slot") == "free_archetype" and e["em"] == 4:
                    e["em"] = 3
        p = carregar("guerreiro4-fa-archer.json", para_impar)
        self.assertTrue(sinal_de_arquetipo(p), "nada sinalizado")

    def test_mais_escolhas_que_slots_e_sinalizado(self):
        """Tres feats de arquetipo num personagem com dois slots geram
        aviso."""
        p = carregar("guerreiro4-fa-archer.json", lambda d: d["escolhas"].append(
            {"em": 4, "slot": "free_archetype", "pega": "wb:feat/marshal-dedication"}))
        self.assertEqual(len(p.gastos["free_archetype"]), 3)
        self.assertGreater(len(p.gastos["free_archetype"]),
                           len(p.slots["free_archetype"]))
        self.assertTrue(sinal_de_arquetipo(p), "nada sinalizado")


# -- o que a dedicacao CONCEDE ---------------------------------------------

class TestGrantsDaDedicacao(unittest.TestCase):
    """A dedicacao entra na ficha como linha e nao entrega o que concede.

    O motor le o array `grants` das CLASSES e das FEATURES de classe
    (`_proficiencias`); de FEAT ele so aproveita `flat_modifier` com selector
    `hp` (`_hp`). Entao tudo que uma dedicacao concede -- `proficiency`,
    `skill_training`, `grant_feat`, `grant_item` -- fica inerte.

    Tamanho medido no pin atual, so entre as 226 dedicacoes:
      grant_item      114        grant_feat       67 (67 com alvo estatico)
      proficiency      49        skill_training   20
      flat_modifier    34

    E o defeito mais caro do trilho de Free Archetype: sob a regra 2 o
    personagem SEMPRE tem esses slots, entao o que se perde aqui se perde em
    toda ficha do sistema.
    """

    def setUp(self):
        self.p = carregar("guerreiro4-fa-dedicacao-com-grants.json")

    def test_a_dedicacao_entra_no_slot_sem_erro(self):
        """A linha aparece: o problema nao e a escolha, e o efeito dela."""
        self.assertEqual(picks_de_arquetipo(self.p), ["wb:feat/shieldmarshal-dedication"])
        self.assertEqual(self.p.fora_do_requisito, [], motivos(self.p))
        # nao se exige silencio TOTAL: esta ficha tem o background `warrior`,
        # que promete um feat cujo alvo o pipeline nao resolveu (item 70) e por
        # isso avisa com razao. O que este teste trava e que o trilho de
        # arquetipo esta limpo -- exigir `avisos == []` faria o teste quebrar
        # por um defeito que nao e o dele.
        self.assertEqual(sinal_de_arquetipo(self.p), [])

    def test_o_dado_esta_na_base(self):
        g = json.dumps(feat("wb:feat/shieldmarshal-dedication").get("grants"))
        self.assertIn('"society": "expert"', g)
        self.assertIn("wb:feat/streetwise", g)
        self.assertIn("wb:feat/courtly-graces", g)

    def test_proficiencia_concedida_pela_dedicacao(self):
        """Shieldmarshal Dedication concede `society: expert` na chave plana
        `proficiency` -- a MESMA chave que o motor ja lia de classe e de
        feature. `_proficiencias` agora percorre tambem os feats efetivos."""
        self.assertEqual(self.p.proficiencias.get("society"), "expert")
        self.assertTrue(any("Shieldmarshal" in o for o in
                            self.p.origem_proficiencia["society"]),
                        self.p.origem_proficiencia["society"])

    def test_grant_feat_estatico_e_aplicado(self):
        """Streetwise e Courtly Graces sao concedidos por `grant_feat` com
        alvo estatico. Aparecem em `concedidos` -- lista propria, com a origem
        junto: o documento continua tendo so o que o jogador escolheu."""
        tudo = {f.get("id") for f in self.p.features}
        # `pega` nem sempre e string (escolha de pericia vem como lista)
        tudo |= {e.get("pega") for e in self.p.doc["escolhas"]
                 if isinstance(e.get("pega"), str)}
        tudo |= {c["id"] for c in self.p.concedidos}
        self.assertIn("wb:feat/streetwise", tudo)
        self.assertIn("wb:feat/courtly-graces", tudo)
        por = {c["id"]: c["concedido_por"] for c in self.p.concedidos}
        self.assertEqual(por["wb:feat/streetwise"],
                         "wb:feat/shieldmarshal-dedication")

    def test_feature_de_classe_concedida_pela_dedicacao(self):
        """Barbarian Dedication concede `wb:class-feature/rage`. Um Guerreiro 4
        com essa dedicacao sob Free Archetype fica com Rage na visao."""
        def barbaro(d):
            d["escolhas"] = [e for e in d["escolhas"] if e.get("slot") != "free_archetype"]
            d["escolhas"].append({"em": 2, "slot": "free_archetype",
                                  "pega": "wb:feat/barbarian-dedication"})
        p = carregar("guerreiro4-fa-dedicacao-com-grants.json", barbaro)
        nomes = [f["nome"] for f in p.features]
        self.assertIn("Rage", nomes)

    def test_grant_que_mexe_no_hp(self):
        """Battle Harbinger Dedication concede Toughness, que vale
        `@actor.level` de HP. Antes: 52 de HP com a dedicacao contra 56 pegando
        Toughness a mao, num nivel 4. Agora os dois caminhos dao o mesmo -- e
        pegar Toughness a mao COM a dedicacao nao soma duas vezes."""
        def dedicacao(d, extra=None):
            d["escolhas"] = [e for e in d["escolhas"] if e.get("slot") != "free_archetype"]
            d["escolhas"].append({"em": 2, "slot": "free_archetype",
                                  "pega": "wb:feat/battle-harbinger-dedication"})
            if extra:
                d["escolhas"].append(extra)
        so_dedicacao = carregar("guerreiro4-fa-dedicacao-com-grants.json", dedicacao)
        a_mao = carregar("guerreiro4-fa-dedicacao-com-grants.json",
                         lambda d: dedicacao(d, {"em": 2, "slot": "class_feat",
                                                 "pega": "wb:feat/toughness"}))
        self.assertEqual(a_mao.hp - so_dedicacao.hp, 0,
                         f"a dedicacao devia render os mesmos {so_dedicacao.nivel} "
                         f"HP de Toughness")


if __name__ == "__main__":
    unittest.main()
