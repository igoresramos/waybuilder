#!/usr/bin/env python3
"""
Diff registro a registro entre a base atual e a de um commit.

O portao 4 so olha CONTAGEM -- ele pega registro que sumiu, nao campo que
mudou de valor. Depois de um build, a pergunta e outra: o que exatamente
mudou, e era o que eu queria mudar? `git diff` num index.json de 15 MB nao
responde isso.

Le o baseline direto do git (`git show <ref>:<caminho>`), entao nao cria
arquivo nem depende de copia manual.

Uso:
    python3 comparar_bases.py              # compara com HEAD
    python3 comparar_bases.py b217be5b8    # com um commit especifico
    python3 comparar_bases.py HEAD --tudo  # lista todos, sem truncar
"""
import json, os, subprocess, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
# Derivado, nunca hardcoded: o projeto saiu do monorepo em 2026-08-01 e os dois
# caminhos fixos ("/home/igor0" e o REL com Tartarus/Projetos/...) deixaram este
# script morto sem ninguem notar -- ele tinha zero chamadas. Ancorar em `AQUI`
# faz funcionar de qualquer cwd; derivar `REL` por relpath sobrevive ao repo
# mudar de lugar de novo.
_r = subprocess.run(["git", "-C", AQUI, "rev-parse", "--show-toplevel"],
                    capture_output=True, text=True)
if _r.returncode != 0:
    sys.exit(f"nao estou dentro de um repo git: {_r.stderr.strip()}")
RAIZ_GIT = _r.stdout.strip()
REL = os.path.relpath(f"{AQUI}/base/index.json", RAIZ_GIT)
ATUAL = f"{AQUI}/base/index.json"


def por_id(base):
    it = list(base.values()) if isinstance(base, dict) else base
    return {r.get("id"): r for r in it if r.get("id")}


def baseline(ref):
    r = subprocess.run(["git", "-C", RAIZ_GIT, "show", f"{ref}:{REL}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"nao consegui ler {ref}:{REL}\n{r.stderr.strip()}")
    return json.loads(r.stdout)


def resumo(v, n=90):
    s = json.dumps(v, ensure_ascii=False, sort_keys=True)
    return s if len(s) <= n else s[:n] + "..."


def main():
    ref = next((a for a in sys.argv[1:] if not a.startswith("--")), "HEAD")
    tudo = "--tudo" in sys.argv

    velho, novo = por_id(baseline(ref)), por_id(json.load(open(ATUAL)))
    print(f"baseline {ref}: {len(velho)} registros")
    print(f"atual        : {len(novo)} registros   "
          f"({len(novo) - len(velho):+d})\n")

    sumiram = sorted(set(velho) - set(novo))
    nasceram = sorted(set(novo) - set(velho))
    mudaram = collections.defaultdict(list)   # campo -> [(id, antes, depois)]
    for i in sorted(set(velho) & set(novo)):
        a, b = velho[i], novo[i]
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                mudaram[k].append((i, a.get(k), b.get(k)))

    total = sum(len(v) for v in mudaram.values())
    ids = {i for v in mudaram.values() for i, _, _ in v}
    print(f"registros que SUMIRAM : {len(sumiram)}")
    print(f"registros que NASCERAM: {len(nasceram)}")
    print(f"registros ALTERADOS   : {len(ids)}  ({total} campo(s) no total)\n")

    for rot, lst in (("SUMIRAM", sumiram), ("NASCERAM", nasceram)):
        if lst:
            print(f"== {rot} ==")
            for i in (lst if tudo else lst[:25]):
                print(f"  {i}")
            if not tudo and len(lst) > 25:
                print(f"  ... e mais {len(lst) - 25}")
            print()

    if mudaram:
        print("== CAMPOS ALTERADOS, por volume ==")
        for k, v in sorted(mudaram.items(), key=lambda x: -len(x[1])):
            print(f"\n  {k}  --  {len(v)} registro(s)")
            for i, a, b in (v if tudo else v[:4]):
                print(f"    {i}")
                print(f"       antes : {resumo(a)}")
                print(f"       depois: {resumo(b)}")
            if not tudo and len(v) > 4:
                print(f"    ... e mais {len(v) - 4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
