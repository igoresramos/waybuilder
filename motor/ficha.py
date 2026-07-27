#!/usr/bin/env python3
"""
Imprime a ficha derivada de um documento de personagem.

Uso: python3 ficha.py exemplos/guerreiro3-mago2.json
"""
import sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from motor import carregar, RANK_BONUS       # noqa: E402

PERICIAS = ["acrobatics", "arcana", "athletics", "crafting", "deception",
            "diplomacy", "intimidation", "medicine", "nature", "occultism",
            "performance", "religion", "society", "stealth", "survival", "thievery"]
SAVES = ["fortitude", "reflex", "will"]
ARMAS = ["unarmed", "simple", "martial", "advanced"]
ARMADURAS = ["unarmored", "light", "medium", "heavy"]


def linha(rotulo, valor, largura=30):
    print(f"  {rotulo:<{largura}} {valor}")


def bloco(titulo):
    print(f"\n{titulo}")
    print("  " + "-" * 58)


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else f"{AQUI}/exemplos/guerreiro3-mago2.json"
    p = carregar(caminho)
    v = p.visao()
    ident = p.doc.get("identidade", {})

    print("=" * 62)
    print(f"  {ident.get('nome','(sem nome)')}")
    classes = " / ".join(f"{c} {n}" for c, n in v["classes"].items())
    print(f"  {classes}   ->   nivel de personagem {v['nivel']}")
    print(f"  {v['ancestralidade']} ({v['heranca']}) | {v['background']}")
    print("=" * 62)

    bloco("ATRIBUTOS")
    print("  " + "   ".join(
        f"{a.upper()} {v['atributos'][a]:>2} ({v['modificadores'][a]:+d})"
        for a in ("str", "dex", "con", "int", "wis", "cha")))

    bloco("DEFESA")
    linha("Pontos de vida", v["hp"])
    for d in p.hp_detalhe:
        print(f"      {d['origem']:<28} +{d['hp']:<4} {d['nota']}")
    for s in SAVES:
        rank = v["proficiencias"].get(s, "untrained")
        mod = p.modificadores.get({"fortitude": "con", "reflex": "dex", "will": "wis"}[s], 0)
        total = p.bonus(s) + mod if rank != "untrained" else mod
        linha(s.capitalize(), f"{total:+d}   ({rank}, nivel {v['nivel']} + "
                              f"{RANK_BONUS[rank]} + mod {mod:+d})")

    ac = v.get("ac") or {}
    if ac:
        linha("Classe de Armadura", f"{ac['total']}   ({ac['detalhe']})")
        print(f"      armadura: {ac['armadura']} [{ac['categoria']}, {ac['rank']}]"
              + (f" | escudo: {ac['escudo']['nome']} +{ac['escudo']['ac']}" if ac.get("escudo") else "")
              + (f" | DEX perdida: {ac['dex_perdida']}" if ac.get("dex_perdida") else ""))

    if v.get("ataques"):
        bloco("ATAQUES")
        for a in v["ataques"]:
            linha(a["arma"], f"{a['ataque']:+d}   dano {a['dano']}   "
                             f"({a['rank']}, {a['atributo_do_ataque'].upper()})")
            print(f"      {a['detalhe']}")

    bloco("PROFICIENCIA (regra 3: bonus = nivel de personagem + rank)")
    perc = v["proficiencias"].get("perception", "untrained")
    linha("Percepcao", f"{p.bonus('perception') + p.modificadores.get('wis',0):+d}   ({perc})")
    for grupo, chaves in (("Armas", ARMAS), ("Armadura", ARMADURAS)):
        itens = [f"{k}={v['proficiencias'].get(k,'untrained')}" for k in chaves
                 if v["proficiencias"].get(k, "untrained") != "untrained"]
        linha(grupo, ", ".join(itens) or "nenhuma")

    bloco("PERICIAS")
    treinadas = {k: r for k, r in v["proficiencias"].items()
                 if k in PERICIAS or k.startswith("lore:")}
    for k in sorted(treinadas):
        origem = ", ".join(dict.fromkeys(p.origem_proficiencia.get(k, [])))
        mostrar = k.replace("lore:", "Lore: ")
        linha(mostrar, f"{p.bonus(k):+d}  ({treinadas[k]})  <- {origem}")
    linha("Escolhas livres (regra 10)", v["pericias_livres"])
    for d in p.pericias_livres_detalhe:
        print(f"      {d['classe']:<20} orcamento {d['orcamento']}  ->  delta {d['delta']}")

    bloco("SLOTS DE ESCOLHA (regra 12: class feat em nivel PAR de personagem)")
    for nome, niveis in v["slots"].items():
        gasto = len(p.gastos.get(f"{nome}_feat", p.gastos.get(nome, [])))
        linha(nome, f"niveis {niveis}   ({gasto} usado(s))")

    bloco("IDENTIDADE DE CLASSE (regra 7: o nivel de classe compra identidade)")
    for c in v["classes"]:
        do_c = [f for f in v["features"] if f["classe"] == c]
        print(f"  {c}:")
        for f in do_c:
            marca = "" if f["na_base"] else "  [AUSENTE DA BASE]"
            eixo = f"  <- {f['eixo']}" if f.get("eixo") else ""
            print(f"      nv{f['nivel_de_classe']:<2} {f['nome']}{eixo}{marca}")
    if v["subclasses"]:
        print()
        for s in v["subclasses"]:
            estado = s["nome"] or f"NAO ESCOLHIDO ({s['opcoes']} opcoes)"
            linha(f"  {s['classe']} / {s['eixo']}", estado)

    if v["conjuracao"]:
        bloco("CONJURACAO (regra 16: slots pelo nivel de CLASSE; "
              "regra 17: rank pelo de personagem)")
        for c in v["conjuracao"]:
            print(f"  {c['classe']} {c['nivel_de_classe']}  --  {c['tradicao']}, {c['tipo']}")
            linha("  Truques por dia", c["truques"])
            linha("  Slots", ", ".join(f"rank {r}: {n}" for r, n in sorted(c["slots"].items())) or "nenhum")
            linha("  Rank maximo do slot", f"{c['max_rank_do_slot']}   (nivel de classe {c['nivel_de_classe']})")
            linha("  Rank efetivo", f"{c['rank_efetivo']}   (ceil({v['nivel']}/2) -- regra 17)")
            linha("  Elevacao ganha", f"+{c['elevacao']} rank(s)")
            linha("  DC de conjuracao", f"{c['dc']['dc']}   (ataque {c['dc']['ataque']:+d})")
            print(f"      {c['dc']['nota']}")
    linha("Focus pool (regra 22)", v["focus_pool"])

    bloco("O QUE VOCE PODE PEGAR (o predicado ORDENA, nunca filtra)")
    lista = p.disponiveis("feat")
    atendem = [f for f in lista if f["atende"]]
    linha("Feats que combinam", f"{len(atendem)} de {len(lista)}")
    for f in atendem[:8]:
        print(f"      nv{(f['level'] or 0):<2} {f['nome']}")
    if len(atendem) > 8:
        print(f"      ... e mais {len(atendem) - 8}")
    print()
    fora = [f for f in lista if not f["atende"]][:3]
    print("  fora do requisito (aparecem marcados, nunca escondidos):")
    for f in fora:
        print(f"      nv{(f['level'] or 0):<2} {f['nome']}  --  {'; '.join(f['motivos'])[:60]}")

    if v["fora_do_requisito"]:
        bloco("FORA DO REQUISITO (principio zero: sinaliza, NUNCA bloqueia)")
        for f in v["fora_do_requisito"]:
            print(f"  ! {f['feat']}: {f['motivo']}")
    if v["avisos"]:
        bloco("AVISOS")
        for a in v["avisos"]:
            print(f"  ! {a}")
    print()


if __name__ == "__main__":
    main()
