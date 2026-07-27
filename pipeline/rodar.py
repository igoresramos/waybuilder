#!/usr/bin/env python3
"""
Roda o pipeline inteiro na ordem certa, que e a unica em que ele funciona:

  extratores -> reconciliar -> emitir_textos -> fundir_renomeados -> portoes

A ordem importa por motivo, nao por convencao:
  - a deteccao de colisao de identidade vive DENTRO de reconciliar, antes da
    fusao de id (portao 7 da spec);
  - fundir_renomeados precisa da prosa ja emitida para usar similaridade como
    confirmacao;
  - os portoes rodam por ultimo porque medem o artefato final.

Uso:
  python3 pipeline/rodar.py                 tudo
  python3 pipeline/rodar.py --sem-extratores so a partir da reconciliacao
  python3 pipeline/rodar.py --so feats      um extrator especifico e o resto
"""
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

EXTRATORES = ["classes.py", "feats.py", "magias.py", "ancestrias.py",
              "equipamento.py", "companheiros.py", "referencia.py",
              "rituais.py", "relicos_idiomas.py"]
DEPOIS = ["reconciliar.py", "emitir_textos.py", "fundir_renomeados.py", "portoes.py"]


def rodar(caminho, rotulo):
    if not os.path.exists(caminho):
        print(f"[pular] {rotulo}: nao existe")
        return None
    t0 = time.time()
    print(f"\n{'=' * 70}\n== {rotulo}\n{'=' * 70}", flush=True)
    r = subprocess.run([PY, caminho], cwd=AQUI)
    print(f"-- {rotulo}: saida {r.returncode} em {time.time() - t0:.0f}s", flush=True)
    return r.returncode


def main():
    args = sys.argv[1:]
    so = None
    if "--so" in args:
        so = args[args.index("--so") + 1]
    passos = []
    if "--sem-extratores" not in args:
        for e in EXTRATORES:
            if so and so not in e:
                continue
            passos.append((f"{AQUI}/extratores/{e}", f"extrator {e}"))
    for d in DEPOIS:
        passos.append((f"{AQUI}/{d}", d))

    falhas = []
    for caminho, rotulo in passos:
        codigo = rodar(caminho, rotulo)
        if codigo:
            falhas.append((rotulo, codigo))
            # portao que falha nao interrompe: o relatorio inteiro tem valor
            if not rotulo.startswith("portoes"):
                print(f"!! {rotulo} falhou -- seguindo para nao esconder o resto")

    print("\n" + "=" * 70)
    if falhas:
        print("passos com saida diferente de zero:")
        for rotulo, codigo in falhas:
            print(f"  - {rotulo}: {codigo}")
    else:
        print("pipeline completo, todos os passos com saida 0")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
