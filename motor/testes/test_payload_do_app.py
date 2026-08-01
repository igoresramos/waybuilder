#!/usr/bin/env python3
"""O motor monta a MESMA ficha com o payload enxuto do app.

`emitir_app.py` corta 52% do indice (proveniencia por campo, xref para as tres
fontes, conflitos, prosa vazada inline). O corte e por lista negra e foi
medido, mas medida de tamanho nao prova que o dado UTIL sobreviveu -- so
derivar a ficha nos dois indices prova.

E o teste que fecha o ciclo: o app carrega `base/app/`, e se a ficha derivada
dali divergir da ficha derivada de `base/index.json`, o corte comeu algo.

Se o payload ainda nao foi emitido (build.sh passo 9), a classe inteira e
pulada em vez de falhar -- clone limpo nao tem o artefato.

Rodar: python3 -m unittest discover -s motor/testes -t .
"""
import glob
import importlib.util
import json
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
PROJETO = os.path.dirname(MOTOR)
EXEMPLOS = os.path.join(MOTOR, "exemplos")
APP = os.path.join(PROJETO, "pipeline", "base", "app", "index.json")

_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(MOTOR, "motor.py"))
wb_motor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb_motor)

BASE_BUILD = wb_motor.Base()

# campos derivados que definem a ficha. Se algum divergir entre os dois
# indices, o payload perdeu dado que o motor usava.
COMPARAR = ("nivel", "hp", "atributos", "modificadores", "proficiencias",
            "pericias_livres", "slots", "aumentos_de_pericia",
            "boosts_direito", "ac", "focus_pool")


@unittest.skipUnless(os.path.exists(APP),
                     "payload do app ainda nao emitido (build.sh passo 9)")
class TestFichaIdenticaNosDoisIndices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_app = wb_motor.Base(APP)

    def test_o_payload_tem_todos_os_registros(self):
        self.assertEqual(set(self.base_app.por_id), set(BASE_BUILD.por_id))

    def test_toda_ficha_de_exemplo_deriva_igual(self):
        arquivos = sorted(glob.glob(os.path.join(EXEMPLOS, "*.json")))
        self.assertGreater(len(arquivos), 10, "os exemplos sumiram?")
        for caminho in arquivos:
            with open(caminho, encoding="utf-8") as fh:
                doc = json.load(fh)
            # cada Personagem recebe uma copia: o motor nao muta o documento,
            # mas depender disso aqui esconderia regressao
            a = wb_motor.Personagem(json.loads(json.dumps(doc)), BASE_BUILD)
            b = wb_motor.Personagem(json.loads(json.dumps(doc)), self.base_app)
            nome = os.path.basename(caminho)
            with self.subTest(ficha=nome):
                for campo in COMPARAR:
                    self.assertEqual(getattr(a, campo), getattr(b, campo),
                                     f"{nome}: `{campo}` divergiu")
                self.assertEqual([f["id"] for f in a.features],
                                 [f["id"] for f in b.features], nome)
                self.assertEqual([c["id"] for c in a.concedidos],
                                 [c["id"] for c in b.concedidos], nome)
                self.assertEqual(a.fora_do_requisito, b.fora_do_requisito, nome)

    def test_candidatos_sao_os_mesmos(self):
        """A lista que a tela recebe tem de ser identica -- e ela sai do
        payload, nao do indice de build."""
        with open(os.path.join(EXEMPLOS, "guerreiro4-fa-dedicacao-com-grants.json"),
                  encoding="utf-8") as fh:
            doc = json.load(fh)
        a = wb_motor.Personagem(json.loads(json.dumps(doc)), BASE_BUILD)
        b = wb_motor.Personagem(json.loads(json.dumps(doc)), self.base_app)
        for slot in ("free_archetype", "class_feat", "skill_feat", "general_feat"):
            with self.subTest(slot=slot):
                self.assertEqual([x["id"] for x in a.candidatos(slot, em=4)],
                                 [x["id"] for x in b.candidatos(slot, em=4)])


class TestCandidatosEmEscala(unittest.TestCase):
    """`candidatos()` e o metodo que a tela chama a cada clique -- ele tem de
    responder para QUALQUER classe e slot, nao so para as fichas de exemplo."""

    @classmethod
    def setUpClass(cls):
        cls.classes = sorted(r["id"] for r in BASE_BUILD.por_id.values()
                             if r.get("kind") == "class")

    def _personagem(self, classe_id, niveis=4):
        escolhas = [
            {"em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/human"},
            {"em": "criacao", "slot": "heranca", "pega": "wb:heritage/versatile-human"},
            {"em": "criacao", "slot": "background", "pega": "wb:background/warrior"},
        ]
        escolhas += [{"em": n, "slot": "nivel_de_classe", "pega": classe_id}
                     for n in range(1, niveis + 1)]
        return wb_motor.Personagem({"escolhas": escolhas}, BASE_BUILD)

    def test_as_27_classes_respondem_em_todo_slot(self):
        slots = ("class_feat", "skill_feat", "general_feat", "ancestry_feat",
                 "free_archetype", "skill_increase", "boosts_livres")
        self.assertEqual(len(self.classes), 27)
        for classe_id in self.classes:
            p = self._personagem(classe_id)
            for slot in slots:
                with self.subTest(classe=classe_id, slot=slot):
                    lista = p.candidatos(slot, em=4)
                    self.assertIsInstance(lista, list)
                    # nenhum slot pode ficar sem candidato nenhum: seria tela
                    # vazia sem explicacao
                    self.assertTrue(lista, f"{classe_id}/{slot} sem candidatos")

    def test_class_feat_so_traz_a_classe_do_personagem_ou_arquetipo(self):
        """O slot de classe aceita DOIS conjuntos, e nada alem deles.

        Um Barbaro nao ve feat de Mago -- mas VE feat de arquetipo, porque
        gastar o feat de classe na Dedication e a porta RAW para entrar num
        arquetipo (`motor/motor.py:3634-3646`). A versao 1 da spec so previa o
        primeiro conjunto e por isso este teste acusava o motor certo.

        A lista inteira e varrida, nao um prefixo: com a ordenacao por `atende`
        os 30 primeiros de um Guerreiro sao todos de arquetipo, entao um corte
        no topo nao exercitaria o ramo da trait de classe.

        Spec: `specs/2026-07-27-slots-e-candidatos.md`, "Por que o slot de
        classe aceita arquetipo".
        """
        for classe_id in self.classes:
            p = self._personagem(classe_id)
            nome = BASE_BUILD.get(classe_id).get("name", "").lower()
            lista = p.candidatos("class_feat", em=4)
            da_classe = 0
            with self.subTest(classe=classe_id):
                for item in lista:
                    traits = {str(t).lower()
                              for t in (BASE_BUILD.get(item["id"]).get("traits") or [])}
                    if nome in traits:
                        da_classe += 1
                        continue
                    self.assertIn("archetype", traits,
                                  f"{item['id']} nao e de {nome} nem e arquetipo")
                # o ramo da trait de classe tem de continuar existindo: se ele
                # quebrar, o teste acima passaria com uma lista 100% arquetipo.
                # Medido em 2026-08-01: minimo 40 (animist), maximo 136 (monk).
                self.assertGreaterEqual(
                    da_classe, 20, f"{classe_id}: so {da_classe} feats da propria classe")

    def test_toda_dedicacao_e_alcancavel_pelo_slot_de_classe(self):
        """O motivo de o slot aceitar arquetipo, virado em teste.

        Nenhuma das 225 dedicacoes da base carrega trait de classe (medido em
        2026-08-01 sobre `pipeline/base/index.json`). Filtrar o slot por trait
        de classe tornava TODAS inalcancaveis por ele, e a unica porta para
        arquetipo virava o slot de Free Archetype -- que e regra variante. Este
        teste e o que impede essa regressao de voltar.
        """
        dedicacoes = {r["id"] for r in BASE_BUILD.por_id.values()
                      if r.get("kind") == "feat"
                      and "dedication" in {str(t).lower() for t in (r.get("traits") or [])}}
        self.assertGreaterEqual(len(dedicacoes), 200, "as dedicacoes sumiram da base?")
        for classe_id in self.classes:
            p = self._personagem(classe_id)
            ids = {x["id"] for x in p.candidatos("class_feat", em=4)}
            with self.subTest(classe=classe_id):
                faltando = dedicacoes - ids
                self.assertFalse(faltando,
                                 f"{classe_id}: {len(faltando)} dedicacoes fora do slot")

    def test_class_feat_continua_sendo_recorte(self):
        """Aceitar arquetipo nao pode virar 'aceita qualquer coisa'.

        Medido em 2026-08-01 num Guerreiro 4: 2.239 candidatos de 6.239 feats
        (35,9%). Os ~4.000 que ficam de fora sao feats de outras classes -- e
        exatamente o que o slot tem de barrar.
        """
        p = self._personagem("wb:class/fighter")
        todos = len(p.disponiveis("feat"))
        do_slot = len(p.candidatos("class_feat", em=4))
        self.assertLess(do_slot, todos * 0.45,
                        f"{do_slot} de {todos} -- o slot parou de recortar")

    def test_slots_abertos_responde_para_todas(self):
        for classe_id in self.classes:
            p = self._personagem(classe_id)
            with self.subTest(classe=classe_id):
                abertos = p.slots_abertos()
                self.assertTrue(abertos, f"{classe_id}: nada aberto num nivel 4 cru")
                # personagem sem nenhum feat escolhido tem de acusar os feats
                self.assertTrue([s for s in abertos if s["kind"] == "feat"])
                # e o boost, que e o item 74
                self.assertTrue([s for s in abertos if s["slot"] == "boosts_livres"])


if __name__ == "__main__":
    unittest.main()
