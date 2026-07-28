#!/usr/bin/env python3
"""
Congela a visao derivada das fichas de exemplo, para o porte TypeScript ter
contra o que se medir.

O porte do motor para o navegador nao pode ser "traduzir e torcer". Aqui o
Python -- que tem 95 testes e foi validado contra os iconics da Paizo --
escreve o gabarito, e o TS roda os MESMOS documentos e compara campo a campo.
Divergencia e falha, sem tolerancia.

E o mesmo metodo que provou o payload do app (as 20 fichas derivam identicas no
indice de build e no enxuto). A diferenca e que agora a comparacao atravessa
duas linguagens.

Depois do porte o Python NAO sai de cena: ele continua sendo o oraculo
(`validar_iconics.py`, teste de carga, portoes). Duas implementacoes com o
mesmo contrato e um gerador de fixtures no meio custam pouco; abandonar o
Python custaria o unico gabarito externo que o projeto tem.

Uso: python3 motor/gerar_fixtures.py
Saida: motor/fixtures/<nome-da-ficha>.json  +  fixtures/_indice.json
"""
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(AQUI, "motor.py"))
wb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb)

EXEMPLOS = os.path.join(AQUI, "exemplos")
SAIDA = os.path.join(AQUI, "fixtures")

# Campos derivados que NAO entram na `visao()` mas que o porte precisa acertar
# igual -- sao o "como", e e neles que uma traducao desatenta erra primeiro.
EXTRAS = ("hp_detalhe", "origem_proficiencia", "pericias_livres_detalhe",
          "aumentos_detalhe", "boosts_direito", "boosts_declarados",
          "boosts_pendentes", "gastos", "class_feat_nivel_1",
          "niveis_por_classe", "ordem_de_classe", "classe_do_nivel",
          "entrada_da_classe", "pericias_automaticas")


def normalizar(o):
    """defaultdict e set nao sobrevivem a serializacao com forma estavel."""
    if isinstance(o, dict):
        return {str(k): normalizar(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)):
        return [normalizar(x) for x in o]
    if isinstance(o, set):
        return sorted(str(x) for x in o)
    return o


def main() -> int:
    base = wb.Base()
    os.makedirs(SAIDA, exist_ok=True)
    indice = []

    for caminho in sorted(glob.glob(os.path.join(EXEMPLOS, "*.json"))):
        nome = os.path.basename(caminho)[:-5]
        with open(caminho, encoding="utf-8") as fh:
            doc = json.load(fh)
        p = wb.Personagem(json.loads(json.dumps(doc)), base)

        fixture = {
            "_doc": ("Gabarito do porte TS. Gerado por motor/gerar_fixtures.py a "
                     "partir do motor Python. NAO editar a mao: regenerar."),
            "ficha": nome,
            "visao": normalizar(p.visao()),
            "extras": {c: normalizar(getattr(p, c)) for c in EXTRAS if hasattr(p, c)},
            # a lista que a tela pede em cada slot -- e o metodo mais novo e o
            # mais facil de portar errado
            "candidatos": {
                f"{slot}@{em}": [x["id"] for x in p.candidatos(slot, em=em)[:40]]
                for slot in ("class_feat", "skill_feat", "general_feat",
                             "ancestry_feat", "free_archetype")
                for em in (1, 2, 4)
            },
        }
        destino = os.path.join(SAIDA, f"{nome}.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump(fixture, fh, ensure_ascii=False, sort_keys=True, indent=1)
        indice.append({"ficha": nome, "nivel": p.nivel, "hp": p.hp,
                       "avisos": len(p.avisos),
                       "fora_do_requisito": len(p.fora_do_requisito),
                       "slots_abertos": len(p.slots_abertos())})
        print(f"  {nome:<44} nivel {p.nivel:>2}  hp {p.hp:>3}  "
              f"pendencias {len(p.slots_abertos()):>2}")

    with open(os.path.join(SAIDA, "_indice.json"), "w", encoding="utf-8") as fh:
        json.dump({"_doc": "resumo das fichas congeladas; o detalhe esta em cada arquivo",
                   "pin_base": base.get("wb:class/fighter").get("id") and "ok",
                   "fichas": indice}, fh, ensure_ascii=False, indent=1)

    print(f"\n{len(indice)} fichas congeladas em motor/fixtures/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
