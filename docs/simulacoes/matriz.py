#!/usr/bin/env python3
"""
Waybuilder -- matriz.py

Roda a matriz completa de balanceamento (niveis 1-15, HOUSE vs RAW vs
RAW_FA, combate SOLO/GRUPO, pilares nao-combate) e escreve
matriz_resultados.json em docs/simulacoes/. O relatorio
2026-07-27_balanceamento.md e escrito a mao lendo esse JSON -- nao gerado
automaticamente, pra garantir que todo numero citado no texto foi de fato
conferido, nao so despejado de template.

Uso: python3 matriz.py [--rapido]   (--rapido reduz N pra iterar o script)
"""
import json, sys, time, os
import wb_sim as w

HERE = os.path.dirname(os.path.abspath(__file__))
RAPIDO = "--rapido" in sys.argv

# Niveis 1-15 (pedido do Igor). Checkpoints de combo em niveis IMPARES:
# e exatamente onde as 12 classes verificadas sobem de rank (ver
# preparar_dados.py, PROG_PREMISSA) -- nivel par nunca muda proficiencia
# pra nenhuma das 12, entao amostrar so nos impares nao perde resolucao
# nenhuma dentro do intervalo pedido.
NIVEIS_TODOS = list(range(1, 16))
NIVEIS_CHECKPOINT = [1, 3, 5, 7, 9, 11, 13, 15]

N_COMBATE = 150 if RAPIDO else 500
N_PILARES = 60 if RAPIDO else 200

# combos pedidos pelo Igor (marcados) + combos adicionais pra ampliar
# cobertura de "pouco obvio" alem dos tres exemplos citados
COMBOS = [
    ("fighter", "wizard", "classico (dip tardio, ja calibrou a regra 17b)"),
    ("fighter", "cleric", "classico (cura, ja calibrou a regra 17b)"),
    ("monk", "cleric", "PEDIDO PELO IGOR -- pouco obvio"),
    ("barbarian", "wizard", "PEDIDO PELO IGOR -- pouco obvio"),
    ("rogue", "druid", "PEDIDO PELO IGOR -- pouco obvio"),
    ("alchemist", "bard", "pouco obvio -- suporte duplo, sem front-line"),
    ("champion", "sorcerer", "pouco obvio -- carisma dupla"),
    ("ranger", "monk", "pouco obvio -- marcial+marcial sem magia"),
    ("cleric", "rogue", "suporte + furtivo"),
    ("druid", "barbarian", "primal + furia, inverso do barbaro/mago"),
]

CASTERS = w.CASTERS


def resumir_personagem(p):
    return dict(nome=p.nome, hp=p.hp, ac=p.ac, ataque=p.ataque,
                dc_magia=p.dc_magia, saves=dict(p.saves),
                n_pericias=p.n_pericias, slots=dict(p.slots))


def rodar_personagem(p, nivel, seed):
    return dict(
        ficha=resumir_personagem(p),
        solo=w.simular_encontro([p], nivel, "solo", n=N_COMBATE, seed=seed),
        grupo=w.simular_encontro([p], nivel, "grupo", n=N_COMBATE, seed=seed+1),
        pilares=w.simular_pilares([p], nivel, n=N_PILARES, seed=seed+2),
    )


def main():
    t0 = time.time()
    resultado = dict(niveis_puros=NIVEIS_TODOS, niveis_checkpoint=NIVEIS_CHECKPOINT,
                      n_combate=N_COMBATE, n_pilares=N_PILARES,
                      classes=sorted(w.CLASSES), casters=sorted(CASTERS),
                      puros={}, combos={})

    # ---- baselines RAW puros, todas as 12 classes, todos os 15 niveis ----
    print("== baselines RAW puros (12 classes x 15 niveis) ==")
    for cls in sorted(w.CLASSES):
        resultado["puros"][cls] = {}
        for lvl in NIVEIS_TODOS:
            p = w.montar_personagem("RAW", lvl, cls)
            seed = hash((cls, lvl)) & 0xffff
            resultado["puros"][cls][lvl] = rodar_personagem(p, lvl, seed)
        print(f"  {cls:12} ok  ({time.time()-t0:6.1f}s acumulado)")

    # ---- combos: HOUSE (2 razoes) / RAW_FA (quando aplicavel) ----
    print("== combos (HOUSE 50/50 + dip tardio, RAW_FA quando aplicavel) ==")
    for a, b, tag in COMBOS:
        chave = f"{a}+{b}"
        resultado["combos"][chave] = dict(tag=tag, niveis={})
        for lvl in NIVEIS_CHECKPOINT:
            entrada = {}
            seed_base = hash((a, b, lvl)) & 0xffff

            # HOUSE 50/50
            p = w.montar_personagem("HOUSE", lvl, a, b, ratio=0.5)
            entrada["house_5050"] = rodar_personagem(p, lvl, seed_base)

            # HOUSE dip tardio: 1 nivel na secundaria, resto na principal
            if lvl >= 2:
                ratio_dip = 1 - 1/lvl
                p = w.montar_personagem("HOUSE", lvl, a, b, ratio=ratio_dip)
                entrada["house_dip"] = rodar_personagem(p, lvl, seed_base+10)

            # RAW_FA: dedicacao so e modelada numericamente quando a classe
            # secundaria e conjuradora (ver ASSUNCOES em wb_sim.py) -- pra
            # combos onde nenhum lado e caster, nao ha ponto RAW_FA (fica
            # documentado como lacuna no relatorio, nao inventado como 0).
            if b in CASTERS:
                p = w.montar_personagem("RAW_FA", lvl, a, b)
                entrada["raw_fa_a_ded_b"] = rodar_personagem(p, lvl, seed_base+20)
            if a in CASTERS:
                p = w.montar_personagem("RAW_FA", lvl, b, a)
                entrada["raw_fa_b_ded_a"] = rodar_personagem(p, lvl, seed_base+30)

            resultado["combos"][chave]["niveis"][lvl] = entrada
        print(f"  {chave:24} ok  ({time.time()-t0:6.1f}s acumulado)")

    resultado["tempo_total_s"] = time.time() - t0
    caminho = f"{HERE}/matriz_resultados.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    print(f"\nOK: {caminho} escrito em {resultado['tempo_total_s']:.1f}s")


if __name__ == "__main__":
    main()
