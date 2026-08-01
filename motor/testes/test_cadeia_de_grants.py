#!/usr/bin/env python3
"""A cadeia de concessao: o que ela aplica, de onde ela parte, e o que ela NAO
pode satisfazer.

Todo caso aqui nasceu de um defeito real achado por review adversarial em
2026-07-27, depois de o motor passar a aplicar `grant_feat` (item 62). Cada
classe abaixo trava um deles.

O mais sutil e o requisito circular: `acrobat-dedication` EXIGE acrobatics
trained e CONCEDE acrobatics. Quando o motor passou a aplicar o que o feat
concede, o feat passou a satisfazer o proprio requisito, e a ficha saia limpa
onde antes sinalizava -- 25 termos ficaram auto-satisfeitos entre os 6.273
feats com `requires`. O conserto e avaliar o `requires` de um feat contra o
estado SEM o efeito dele proprio, o que exige saber a RAIZ de cada concessao.

Rodar: python3 -m unittest discover -s motor/testes -t .
"""
import copy
import importlib.util
import json
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
EXEMPLOS = os.path.join(MOTOR, "exemplos")

_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(MOTOR, "motor.py"))
wb_motor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb_motor)

BASE = wb_motor.Base()
FICHA = os.path.join(EXEMPLOS, "guerreiro4-fa-dedicacao-com-grants.json")

# Base sintetica: quatro registros que EXISTEM so para manter dois defeitos
# reproduziveis depois que o pipeline apagou a evidencia deles da base real.
#
# Medido em 2026-08-01 sobre `pipeline/base/index.json` (20.083 registros):
#   - 1.170 alvos de `grant_feat`, ZERO nao resolvidos (eram 476, todos de
#     background). O aviso "alvo nao resolvido pelo pipeline" virou codigo sem
#     dado que o exercite.
#   - 698 ids alternativos por alias, 578 sem registro proprio, e ZERO `requires`
#     citando um deles -- `aplicar_aliases_em_requires.py` reescreveu todos para
#     o id canonico.
# Os dois consertos sao bons e ficam. Mas o motor continua sendo o ultimo
# anteparo: ficha salva com o nome antigo, e extrator novo que volte a emitir
# nome cru, sao os casos que ele tem de aguentar. Amarrar esses testes ao pin
# significava perde-los em silencio na primeira melhora do pipeline -- o que
# aconteceu. A fixture nao muda quando o pipeline muda.
BASE_SINTETICA = wb_motor.Base(os.path.join(AQUI, "fixtures", "base_sintetica.json"))


def doc_sintetico(escolhas: list[dict]) -> dict:
    """Ficha na base sintetica, com ancestria so para o motor ter de onde
    partir (`hp`, `size`, `speed`)."""
    return {"escolhas": [{"em": "criacao", "slot": "ancestralidade",
                          "pega": "wb:ancestry/povo-de-teste"}] + escolhas}

# slots que descrevem o personagem sem nenhum feat escolhido -- a base neutra
# para medir o que uma dedicacao entrega sem contaminacao. Aprendido na marra:
# a primeira medicao usou a ficha inteira, que ja tinha `additional-lore` e
# `double-slice`, e 30 dedicacoes apareceram falsamente como mudas porque
# `_ja_tenho` bloqueava justo o que se queria medir.
SEM_FEATS = ("ancestralidade", "heranca", "background", "nivel_de_classe",
             "subclasse", "boosts_livres")


def doc_base() -> dict:
    with open(FICHA, encoding="utf-8") as fh:
        return json.load(fh)


def neutro(dedicacao: str | None = None) -> dict:
    d = doc_base()
    d["escolhas"] = [e for e in d["escolhas"] if e.get("slot") in SEM_FEATS]
    if dedicacao:
        d["escolhas"].append({"em": 2, "slot": "free_archetype", "pega": dedicacao})
    return d


def motivos(p) -> list[str]:
    return [f"{f['feat']}: {f['motivo']}" for f in p.fora_do_requisito]


class TestRequisitoCircular(unittest.TestCase):
    """Um feat nao satisfaz o proprio requisito."""

    def test_o_dado_sustenta_o_caso(self):
        """Se a dedicacao deixasse de exigir ou de conceder acrobatics, o teste
        abaixo passaria pelo motivo errado."""
        reg = BASE.get("wb:feat/acrobat-dedication")
        texto = json.dumps(reg, ensure_ascii=False)
        self.assertIn('"acrobatics"', json.dumps(reg.get("requires"), ensure_ascii=False))
        self.assertIn("acrobatics", texto)

    def test_dedicacao_que_concede_o_que_exige_e_sinalizada(self):
        p = wb_motor.Personagem(neutro("wb:feat/acrobat-dedication"), BASE)
        self.assertTrue([m for m in motivos(p) if "acrobatics" in m], motivos(p))

    def test_mas_o_efeito_e_aplicado_assim_mesmo(self):
        """Principio zero: sinaliza e nao desfaz. A pericia entra na ficha."""
        p = wb_motor.Personagem(neutro("wb:feat/acrobat-dedication"), BASE)
        self.assertEqual(p.proficiencias.get("acrobatics"), "trained")

    def test_requisito_legitimo_continua_limpo(self):
        """Controle: uma dedicacao cujo requisito a ficha atende de verdade nao
        pode ser afetada pelo desconto."""
        p = wb_motor.Personagem(neutro("wb:feat/shieldmarshal-dedication"), BASE)
        self.assertEqual(p.fora_do_requisito, [], motivos(p))
        self.assertEqual(p.proficiencias.get("society"), "expert")

    def test_rank_sem_desconta_so_a_origem_pedida(self):
        p = wb_motor.Personagem(neutro("wb:feat/shieldmarshal-dedication"), BASE)
        self.assertEqual(p._rank_sem("society", None), "expert")
        self.assertEqual(p._rank_sem("society", "wb:feat/shieldmarshal-dedication"),
                         "untrained")


class TestRaizDaCadeia(unittest.TestCase):
    """Concessao carrega de QUEM ela veio, ate a ponta da cadeia."""

    def setUp(self):
        self.p = wb_motor.Personagem(doc_base(), BASE)

    def test_concedido_sabe_a_origem_imediata_e_a_raiz(self):
        por_id = {c["id"]: c for c in self.p.concedidos}
        streetwise = por_id["wb:feat/streetwise"]
        self.assertEqual(streetwise["concedido_por"], "wb:feat/shieldmarshal-dedication")
        self.assertEqual(streetwise["raiz"], "wb:feat/shieldmarshal-dedication")

    def test_a_ficha_expoe_os_concedidos(self):
        v = self.p.visao()
        ids = {c["id"] for c in v["concedidos"]}
        self.assertIn("wb:feat/streetwise", ids)
        self.assertIn("wb:feat/courtly-graces", ids)


class TestOrigensDaCadeia(unittest.TestCase):
    """A cadeia parte de feat, feature, ancestria, heranca e background."""

    def test_heranca_concede(self):
        """`ambitious-human` concede Fleet. Sao 69 alvos validos nesses tres
        kinds (44 heranca + 25 background) que ficavam inertes."""
        d = doc_base()
        d["escolhas"] = [e for e in d["escolhas"] if e.get("pega") != "wb:feat/fleet"]
        for e in d["escolhas"]:
            if e.get("slot") == "heranca":
                e["pega"] = "wb:heritage/ambitious-human"
        p = wb_motor.Personagem(d, BASE)
        self.assertIn("wb:feat/fleet", {c["id"] for c in p.concedidos})

    def test_o_que_ja_foi_escolhido_nao_e_concedido_de_novo(self):
        """Mesma heranca, mas com Fleet escolhido a mao: nao duplica."""
        d = doc_base()
        for e in d["escolhas"]:
            if e.get("slot") == "heranca":
                e["pega"] = "wb:heritage/ambitious-human"
        p = wb_motor.Personagem(d, BASE)
        self.assertEqual([c for c in p.concedidos if c["id"] == "wb:feat/fleet"], [])

    def test_alvo_nao_resolvido_pelo_pipeline_e_sinalizado(self):
        """Concessao que aponta para NOME em vez de id vira aviso, e nao perda
        silenciosa.

        O caso nasceu do background `warrior`, que prometia Intimidating Glare
        por nome (item 70): eram 476 alvos orfaos, todos em background. Hoje o
        pipeline resolve todos os 1.170 -- `wb:background/warrior` concede
        `wb:feat/intimidating-glare` de verdade -- entao o caso so existe na
        fixture. O motor continua sendo quem segura extrator novo que volte a
        emitir nome cru.
        """
        p = wb_motor.Personagem(
            doc_sintetico([{"em": "criacao", "slot": "background",
                            "pega": "wb:background/promessa-vaga"}]),
            BASE_SINTETICA)
        avisos = [a for a in p.avisos if "nao resolvido pelo pipeline" in a]
        self.assertTrue(avisos, p.avisos)
        self.assertIn("Olhar Intimidador", avisos[0])
        # o aviso e sobre alvo NAO resolvido: o que a fixture prometeu nao pode
        # ter entrado na ficha por baixo do pano
        self.assertEqual(p.concedidos, [])


class TestRegrasDeDedicacaoEnxergamConcedidos(unittest.TestCase):
    """As checagens de arquetipo leem escolhido MAIS concedido."""

    def test_ids_de_feat_inclui_os_concedidos(self):
        p = wb_motor.Personagem(doc_base(), BASE)
        ids = p._ids_de_feat_escolhidos()
        self.assertIn("wb:feat/shieldmarshal-dedication", ids)   # escolhido
        self.assertIn("wb:feat/streetwise", ids)                 # concedido

    def test_dedicacao_concedida_nao_gera_falso_positivo(self):
        """`gray-corsair-training` concede `pirate-dedication`. Um feat Pirate
        na mesma ficha nao pode ser acusado de faltar a dedicacao."""
        concede = BASE.opcional("wb:feat/gray-corsair-training")
        if concede is None:
            self.skipTest("gray-corsair-training ausente da base neste pin")
        alvos = [a for g in (concede.get("grants") or []) if isinstance(g, dict)
                 for a in (g.get("grant_feat") or [])]
        self.assertIn("wb:feat/pirate-dedication", alvos)
        d = neutro()
        d["escolhas"].append({"em": 2, "slot": "free_archetype",
                              "pega": "wb:feat/gray-corsair-training"})
        p = wb_motor.Personagem(d, BASE)
        self.assertIn("wb:feat/pirate-dedication", p._ids_de_feat_escolhidos())


class TestSemDuplaContagem(unittest.TestCase):
    """O mesmo efeito nunca entra duas vezes."""

    def test_toughness_escolhido_e_concedido_dao_o_mesmo_hp(self):
        so_dedicacao = wb_motor.Personagem(
            neutro("wb:feat/battle-harbinger-dedication"), BASE)
        d = neutro("wb:feat/battle-harbinger-dedication")
        d["escolhas"].append({"em": 2, "slot": "class_feat", "pega": "wb:feat/toughness"})
        com_os_dois = wb_motor.Personagem(d, BASE)
        self.assertEqual(so_dedicacao.hp, com_os_dois.hp)

    def test_toughness_aparece_uma_vez_so_no_detalhe_de_hp(self):
        p = wb_motor.Personagem(neutro("wb:feat/battle-harbinger-dedication"), BASE)
        vezes = [d for d in p.hp_detalhe if "Toughness" in str(d.get("origem"))]
        self.assertEqual(len(vezes), 1, p.hp_detalhe)


if __name__ == "__main__":
    unittest.main()


class TestAliasPreRemaster(unittest.TestCase):
    """O motor e o portao 3 tem de concordar sobre o que e "a mesma coisa".

    A base guarda o nome PRE-REMASTER como alias: `stunning-fist` e o mesmo
    feat que `stunning-blows`, `wild-shape` virou `untamed-form`,
    `divine-ally` virou `devout-blessing`. Sao 698 ids alternativos, 578 deles
    sem registro proprio (eram 348 na primeira medicao; recontado 2026-08-01,
    depois da fusao de duplicata de nome).

    O portao 3 sempre resolveu alias antes de reclamar, e por isso passava
    verde. O motor comparava id cru -- entao 24 `requires` de feats de classes
    centrais nunca eram satisfeitos, por mais que o personagem tivesse o feat.
    Portao verde escondendo defeito e pior que portao ausente: da a impressao
    de que o ponto foi verificado.
    """

    def test_o_dado_sustenta_o_caso(self):
        """O alias e um id SEM registro proprio que chega no registro novo.

        A versao anterior media isso em `stunning-fist` e exigia
        `opcional() is None` para o id legado. As duas metades morreram: desde
        a spec `2026-07-30-grau-legado-nao-fundido` o `opcional` segue alias de
        proposito (ficha salva com id aposentado nao pode perder o item em
        silencio), e a base tem 578 ids de alias sem registro proprio -- nenhum
        deles devolve None. O que precisa continuar verdadeiro e o de baixo.
        """
        self.assertNotIn("wb:feat/tecnica-antiga", BASE_SINTETICA.por_id)
        self.assertIn("Tecnica Antiga",
                      BASE_SINTETICA.get("wb:feat/tecnica-nova").get("aliases") or [])
        self.assertEqual(BASE_SINTETICA.opcional("wb:feat/tecnica-antiga")["id"],
                         "wb:feat/tecnica-nova")

    def test_resolver_segue_o_alias(self):
        self.assertEqual(BASE.resolver("wb:feat/stunning-fist"),
                         "wb:feat/stunning-blows")
        self.assertEqual(BASE.resolver("wb:feat/wild-shape"),
                         "wb:feat/untamed-form")

    def test_id_que_existe_nao_e_desviado(self):
        """A resolucao so age sobre o que NAO existe -- senao um id valido
        poderia ser sequestrado por um alias homonimo de outro registro."""
        for wb_id in ("wb:feat/toughness", "wb:class/fighter",
                      "wb:feat/stunning-blows"):
            self.assertEqual(BASE.resolver(wb_id), wb_id)

    def test_id_desconhecido_volta_igual(self):
        self.assertEqual(BASE.resolver("wb:feat/nao-existe-nem-como-alias"),
                         "wb:feat/nao-existe-nem-como-alias")

    ESCOLHAS_COM_AS_DUAS_TECNICAS = [
        {"em": 1, "slot": "class_feat", "pega": "wb:feat/tecnica-nova"},
        {"em": 2, "slot": "class_feat", "pega": "wb:feat/tecnica-derivada"},
    ]

    def test_requisito_citando_o_nome_antigo_e_satisfeito(self):
        """O caso que motivou tudo: `requires` cita o nome pre-remaster e o
        personagem tem o feat com o nome novo.

        Media em `vitality-manipulating-stance`, cujo `requires` citava
        `stunning-fist`. Nao cita mais: `aplicar_aliases_em_requires.py`
        reescreveu para `stunning-blows`, e hoje ZERO dos `requires` da base
        aponta para um id que so existe como alias (medido 2026-08-01). O
        conserto no pipeline nao dispensa o motor de resolver -- ficha salva
        antes dele guarda o id antigo, e o `has` e o unico que a le.
        """
        p = wb_motor.Personagem(
            doc_sintetico(self.ESCOLHAS_COM_AS_DUAS_TECNICAS), BASE_SINTETICA)
        self.assertEqual(p.fora_do_requisito, [], motivos(p))

    def test_e_falha_quando_o_alias_some(self):
        """Controle negativo: sem o alias, o mesmo `requires` reprova. Sem isto
        o teste acima passaria igual se `requires` nunca fosse avaliado."""
        base = wb_motor.Base(os.path.join(AQUI, "fixtures", "base_sintetica.json"))
        base.por_id["wb:feat/tecnica-nova"] = dict(
            base.por_id["wb:feat/tecnica-nova"], aliases=[])
        p = wb_motor.Personagem(
            doc_sintetico(self.ESCOLHAS_COM_AS_DUAS_TECNICAS), base)
        self.assertTrue([m for m in motivos(p) if "tecnica-antiga" in m], motivos(p))
