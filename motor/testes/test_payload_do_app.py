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

    def test_class_feat_traz_feat_da_classe_certa(self):
        """O recorte e por classe DO PERSONAGEM -- um Barbaro nao ve feat de
        Mago no slot de classe."""
        for classe_id in self.classes:
            p = self._personagem(classe_id)
            nome = BASE_BUILD.get(classe_id).get("name", "").lower()
            lista = p.candidatos("class_feat", em=4)
            with self.subTest(classe=classe_id):
                for item in lista[:30]:
                    traits = {str(t).lower()
                              for t in (BASE_BUILD.get(item["id"]).get("traits") or [])}
                    self.assertIn(nome, traits, f"{item['id']} nao e de {nome}")

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
