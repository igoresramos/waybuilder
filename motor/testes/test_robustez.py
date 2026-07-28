#!/usr/bin/env python3
"""O motor NUNCA explode -- sinaliza.

Isto nao e paranoia: o construtor e interativo, entao o motor deriva a ficha a
cada clique, inclusive **antes da primeira escolha**. Um personagem de nivel 0,
sem classe nenhuma, e o ESTADO INICIAL do app, nao um caso de borda exotico.

O caso que originou este arquivo foi uma regressao real, achada por review
adversarial em 2026-07-27: `_aumentos_de_pericia` escolhia o teto de rank com
`next(r for n, r in TETO_DE_RANK if self.nivel >= n)`, e a tupla parava em
`(1, "expert")`. Com `nivel == 0` o gerador esgotava e o `next` levantava
`StopIteration` -- o motor inteiro morria antes de derivar qualquer coisa, e
`Personagem({}, Base())` era suficiente para reproduzir.

A regra que estes testes travam: documento malformado vira AVISO, nunca
excecao. Vale para doc vazio, campo faltando, tipo errado e id que nao existe
na base.

Rodar: python3 -m unittest discover -s motor/testes -t .
"""
import copy
import glob
import importlib.util
import json
import os
import random
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
EXEMPLOS = os.path.join(MOTOR, "exemplos")

_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(MOTOR, "motor.py"))
wb_motor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb_motor)

BASE = wb_motor.Base()


class TestNivelZero(unittest.TestCase):
    """O estado inicial do construtor: nada escolhido ainda."""

    def test_documento_vazio_deriva(self):
        p = wb_motor.Personagem({}, BASE)
        self.assertEqual(p.nivel, 0)
        self.assertEqual(p.hp, 0)
        self.assertTrue(p.avisos, "sem classe e sem ancestria tem de gerar aviso")

    def test_nivel_zero_nao_tem_aumento_de_pericia(self):
        p = wb_motor.Personagem({"escolhas": []}, BASE)
        self.assertEqual(p.aumentos_de_pericia, [])

    def test_so_ancestria_ja_da_hp_de_ancestria(self):
        p = wb_motor.Personagem(
            {"escolhas": [{"em": "criacao", "slot": "ancestralidade",
                           "pega": "wb:ancestry/human"}]}, BASE)
        self.assertEqual(p.nivel, 0)
        self.assertEqual(p.hp, 8)


class TestDocumentoMalformado(unittest.TestCase):
    """Campo faltando, tipo errado, id inexistente -- tudo vira aviso."""

    CASOS = [
        ({"escolhas": [{"em": 1, "slot": "nivel_de_classe"}]}, "sem `pega`"),
        ({"escolhas": [{"em": 1, "slot": "nivel_de_classe", "pega": None}]}, "`pega` nulo"),
        ({"escolhas": [{"em": 1, "slot": "nivel_de_classe", "pega": ["x"]}]}, "`pega` lista"),
        ({"escolhas": [{"em": None, "slot": "nivel_de_classe",
                        "pega": "wb:class/fighter"}]}, "`em` nulo"),
        ({"escolhas": [{"em": 1, "slot": "nivel_de_classe",
                        "pega": "wb:class/nao-existe"}]}, "classe fora da base"),
        ({"escolhas": [{"em": "criacao", "slot": "ancestralidade"}]}, "ancestria sem `pega`"),
        ({"escolhas": [{"slot": "skill_increase", "pega": "nao-e-pericia"}]}, "pericia inventada"),
        ({"escolhas": [{"em": 1, "slot": "subclasse",
                        "pega": "wb:class-feature/nao-existe"}]}, "subclasse fora da base"),
    ]

    def test_nenhum_malformado_levanta_excecao(self):
        for doc, nome in self.CASOS:
            with self.subTest(caso=nome):
                try:
                    wb_motor.Personagem(doc, BASE)
                except Exception as ex:      # noqa: BLE001 -- e exatamente o que se testa
                    self.fail(f"{nome} levantou {type(ex).__name__}: {ex}")

    def test_classe_fora_da_base_e_sinalizada(self):
        """Nao basta nao explodir: tem de DIZER o que ignorou."""
        p = wb_motor.Personagem(
            {"escolhas": [{"em": 1, "slot": "nivel_de_classe",
                           "pega": "wb:class/nao-existe"}]}, BASE)
        self.assertTrue([a for a in p.avisos if "ausente da base" in a], p.avisos)
        self.assertEqual(p.nivel, 0)


class TestFuzzSobreOsExemplos(unittest.TestCase):
    """Semente fixa: o mesmo conjunto de mutacoes a cada rodada, para que uma
    falha seja reproduzivel em vez de intermitente."""

    def test_mutacoes_nao_explodem(self):
        random.seed(7)
        casos = falhas = 0
        for caminho in sorted(glob.glob(os.path.join(EXEMPLOS, "*.json"))):
            with open(caminho, encoding="utf-8") as fh:
                base = json.load(fh)
            for _ in range(40):
                doc = copy.deepcopy(base)
                escolhas = doc.get("escolhas", [])
                random.shuffle(escolhas)
                for e in escolhas:
                    if e and random.random() < 0.15:
                        e.pop(random.choice(list(e.keys())), None)
                if random.random() < 0.1:
                    doc.pop("escolhas", None)
                casos += 1
                try:
                    wb_motor.Personagem(doc, BASE)
                except Exception as ex:      # noqa: BLE001
                    falhas += 1
                    print(f"\n  fuzz: {os.path.basename(caminho)} -> "
                          f"{type(ex).__name__}: {ex}")
        self.assertGreater(casos, 200, "os exemplos sumiram?")
        self.assertEqual(falhas, 0, f"{falhas} de {casos} mutacoes explodiram")


class TestOrdemNaoImportaParaOsNumeros(unittest.TestCase):
    """Embaralhar as escolhas nao pode mudar a ficha derivada -- se mudasse, a
    ficha dependeria da ordem de digitacao do jogador."""

    def test_embaralhar_preserva_os_numeros(self):
        random.seed(11)
        for caminho in sorted(glob.glob(os.path.join(EXEMPLOS, "*.json"))):
            with open(caminho, encoding="utf-8") as fh:
                base = json.load(fh)
            ref = wb_motor.Personagem(copy.deepcopy(base), BASE)
            for _ in range(5):
                doc = copy.deepcopy(base)
                random.shuffle(doc.get("escolhas", []))
                p = wb_motor.Personagem(doc, BASE)
                with self.subTest(ficha=os.path.basename(caminho)):
                    self.assertEqual(p.nivel, ref.nivel)
                    self.assertEqual(p.hp, ref.hp)
                    self.assertEqual(p.proficiencias, ref.proficiencias)
                    self.assertEqual(p.pericias_livres, ref.pericias_livres)
                    self.assertEqual(p.slots, ref.slots)


if __name__ == "__main__":
    unittest.main()
