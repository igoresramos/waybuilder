#!/usr/bin/env python3
"""
Triagem do conteudo legado (OGL) sem par de remaster.

Ausencia de `remaster_id` NAO prova remocao. Os 3.373 orfaos sao tres coisas
diferentes no mesmo balde, e so a terceira e a pilha de resgate:

  A. RENOMEADO  -- existe equivalente remaster com outro nome. Erro de ponte,
                   nao conteudo perdido. O certo e fundir, nao reviver.
  B. INTOCADO   -- o livro de origem nunca teve sucessor remaster, entao o
                   conteudo segue valido. Nao foi removido, so nao foi revisitado.
  C. REMOVIDO   -- o livro TEM sucessor remaster e o conteudo nao apareceu la.
                   Esta e a pilha de resgate de verdade.

Entrada: pipeline/base/index.json
Saida:   pipeline/base/triagem_legado.md + triagem_legado.json
"""
import json, os, re, collections, difflib, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# livro legado -> sucessor remaster. Se um livro tem sucessor, o que nao migrou
# foi cortado de proposito.
SUCESSOR = {
    "core rulebook": "Player Core",
    "advanced players guide": "Player Core 2",
    "gamemastery guide": "GM Core",
    "bestiary": "Monster Core",
    "bestiary 2": "Monster Core",
    "bestiary 3": "Monster Core",
    "secrets of magic": None,
    "ancestry guide": None,
    "character guide": None,
    "world guide": None,
    "book of the dead": None,
    "guns gears": "Guns & Gears (Remastered)",
    "dark archive": "Dark Archives (Remastered)",
    "treasure vault": "Treasure Vault (Remastered)",
}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    base = json.load(open(f"{BASE}/index.json"))
    lic = lambda r: (r.get("source") or {}).get("license")
    livro = lambda r: norm((r.get("source") or {}).get("book"))

    orc = [r for r in base if lic(r) == "ORC"]
    ogl = [r for r in base if lic(r) == "OGL"]
    tem_par = lambda r: bool((r.get("xref") or {}).get("aon_remaster")
                             or (r.get("xref") or {}).get("aon_legacy"))
    orfaos = [r for r in ogl if not tem_par(r)]
    print(f"ORC {len(orc)} | OGL {len(ogl)} | orfaos {len(orfaos)}")

    # indice dos remaster por kind+nome normalizado, para achar renomeados
    por_nome = collections.defaultdict(list)
    for r in orc:
        por_nome[(r.get("kind"), norm(r.get("name")))].append(r)
    nomes_por_kind = collections.defaultdict(list)
    for (k, n) in por_nome:
        nomes_por_kind[k].append(n)

    A, B, C = [], [], []
    for r in orfaos:
        k, n = r.get("kind"), norm(r.get("name"))
        # A1: nome identico existe em ORC -> ponte perdida
        if (k, n) in por_nome:
            A.append((r, por_nome[(k, n)][0]["name"], "nome identico"))
            continue
        # A2: nome muito parecido em ORC -> provavel rebranding
        perto = difflib.get_close_matches(n, nomes_por_kind.get(k, []), n=1, cutoff=0.88)
        if perto:
            A.append((r, por_nome[(k, perto[0])][0]["name"], "nome proximo"))
            continue
        # B vs C: o livro de origem tem sucessor?
        lv = livro(r)
        chave = next((s for s in SUCESSOR if s in lv or lv in s), None)
        if chave and SUCESSOR[chave]:
            C.append((r, SUCESSOR[chave]))
        else:
            B.append(r)

    print(f"\nA renomeado (fundir):   {len(A)}")
    print(f"B intocado (segue valido): {len(B)}")
    print(f"C REMOVIDO (resgatar):  {len(C)}")

    linhas = ["# Triagem do conteudo legado", "",
              "Ausencia de `remaster_id` nao prova remocao. Os orfaos sao tres coisas:",
              "",
              f"| categoria | registros | o que fazer |",
              f"|---|---|---|",
              f"| **A. renomeado** | {len(A)} | fundir com o par remaster -- nao e perda |",
              f"| **B. intocado** | {len(B)} | nada: o livro nunca teve sucessor, segue valido |",
              f"| **C. REMOVIDO** | {len(C)} | **a pilha de resgate** |", ""]

    linhas += ["## C -- removido de proposito", "",
               "O livro de origem TEM sucessor remaster e este conteudo nao migrou.", ""]
    porkind = collections.Counter(r.get("kind") for r, _ in C)
    linhas += [f"- `{k}`: {n}" for k, n in porkind.most_common()] + [""]
    porlivro = collections.Counter(str((r.get("source") or {}).get("book")) for r, _ in C)
    linhas += ["Por livro de origem:", ""]
    linhas += [f"- {b} -> {SUCESSOR.get(next((s for s in SUCESSOR if s in norm(b)), ''), '?')}: {n}"
               for b, n in porlivro.most_common()] + [""]
    for kind in [k for k, _ in porkind.most_common()]:
        itens = sorted([r for r, _ in C if r.get("kind") == kind],
                       key=lambda r: (r.get("level") or 0, r.get("name") or ""))
        linhas += [f"### {kind} ({len(itens)})", ""]
        for r in itens[:120]:
            lv = r.get("level")
            linhas.append(f"- **{r.get('name')}**"
                          + (f" (nv {lv})" if lv is not None else "")
                          + f" -- {(r.get('source') or {}).get('book')}")
        if len(itens) > 120:
            linhas.append(f"- _... e mais {len(itens)-120}_")
        linhas.append("")

    linhas += ["## A -- renomeado (amostra)", ""]
    for r, novo, motivo in A[:60]:
        linhas.append(f"- `{r['id']}` **{r.get('name')}** -> **{novo}** _({motivo})_")
    if len(A) > 60:
        linhas.append(f"- _... e mais {len(A)-60}_")

    open(f"{BASE}/triagem_legado.md", "w").write("\n".join(linhas) + "\n")
    json.dump({"renomeado": [{"id": r["id"], "nome": r.get("name"), "vira": novo,
                              "motivo": m} for r, novo, m in A],
               "intocado": [r["id"] for r in B],
               "removido": [{"id": r["id"], "nome": r.get("name"), "kind": r.get("kind"),
                             "level": r.get("level"),
                             "livro": (r.get("source") or {}).get("book"),
                             "sucessor": suc} for r, suc in C]},
              open(f"{BASE}/triagem_legado.json", "w"), ensure_ascii=False, indent=1)
    print(f"\n-> base/triagem_legado.md e .json")


if __name__ == "__main__":
    main()
