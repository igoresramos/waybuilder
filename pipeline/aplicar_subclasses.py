#!/usr/bin/env python3
"""
Separa, na progressao de cada classe, o que e CONCEDIDO do que e ESCOLHIDO.

O grafo de progressao tem dois niveis: `classe -> feature -> sub-escolha`.
Modelado como um so, a segunda camada some -- e pior, entra na progressao como
se fosse concessao. Medido: `wb:class/wizard` listava **37 features no nivel 1**,
sendo que Escola e Tese sao escolha unica entre 23 e 10 opcoes.

Um motor que aplicasse essa progressao literal daria ao Mago 1 todas as escolas
de magia ao mesmo tempo.

Como distinguir sem inferir: o AoN categoriza cada eixo separadamente
(`arcane-school`, `arcane-thesis`, `muse`, `racket`, `instinct`, `doctrine`...),
extraidos por `extratores/aon_kinds.py`. Feature da progressao cujo nome casa
com um registro desses e **opcao**, nao concessao.

Emite, em cada classe:
    "progressao"  -- so o que e concedido de fato
    "subclasses"  -- [{eixo, nivel, slot, opcoes: [ids]}]

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_subclasses.md
"""
import json, os, sys, glob, collections, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"
sys.path.insert(0, os.path.join(AQUI, "extratores"))
from aon_kinds import SUBESCOLHAS                    # noqa: E402


def concedidas_pelo_foundry():
    """nome da classe -> {nome normalizado da feature: nivel}, de `system.items`.

    Esta e a fonte autoritativa sobre o que a classe **concede**: e o que o VTT
    usa para montar o personagem. `wb:class/wizard` declarava 49 entradas de
    progressao porque o extrator varreu toda class-feature com o trait `wizard`
    -- o que inclui as 23 escolas e as 5 teses, que sao opcao mutuamente
    exclusiva. O Foundry lista **15**, e entre elas "Arcane School" aparece uma
    vez so, como a escolha que e.
    """
    import comum
    raiz = comum.packs_foundry(BRUTOS) or ""
    mapa = {}
    for f in glob.glob(f"{raiz}/classes/*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("name"):
            continue
        itens = ((d.get("system") or {}).get("items") or {})
        valores = itens.values() if isinstance(itens, dict) else itens
        mapa[norm(d["name"])] = {
            norm(x.get("name")): x.get("level")
            for x in valores if isinstance(x, dict) and x.get("name")}
    return mapa


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def main():
    base = json.load(open(f"{BASE}/index.json"))
    por_id = {r["id"]: r for r in base}

    # nome normalizado -> (eixo, id) das opcoes de sub-escolha
    opcao_por_nome = {}
    for r in base:
        if r.get("kind") in SUBESCOLHAS:
            opcao_por_nome.setdefault(norm(r.get("name")), []).append(
                (r["kind"], r["id"]))

    do_foundry = concedidas_pelo_foundry()
    relatorio, total_mov = [], 0
    for classe in [r for r in base if r.get("kind") == "class"]:
        prog = classe.get("progressao") or []
        if not prog:
            continue
        concedidas, escolhas = [], collections.defaultdict(
            lambda: {"nivel": None, "opcoes": []})

        concede_foundry = do_foundry.get(norm(classe.get("name")), {})

        for passo in prog:
            fid = passo.get("concede")
            feature = por_id.get(fid)
            nome = norm((feature or {}).get("name") or
                        str(fid).split("/")[-1].replace("-", " "))

            # 1o criterio, autoritativo: a classe declara o que concede
            if concede_foundry and nome in concede_foundry:
                concedidas.append(passo)
                continue
            candidatos = opcao_por_nome.get(nome)
            if not candidatos:
                if not concede_foundry:
                    concedidas.append(passo)     # sem lista autoritativa, mantem
                    continue
                # A classe tem lista e este nome nao esta nela: e opcao, ainda
                # que o AoN nao categorize o eixo. Cai aqui o que so o Foundry
                # modela -- escolas de Runelord (os sete pecados) e escolas de
                # organizacao do Lost Omens (Cascade Bearers, Uzunjati...).
                eixo = "outras-opcoes"
            else:
                eixo = candidatos[0][0]
            bloco = escolhas[eixo]
            nivel = passo.get("nivel")
            bloco["nivel"] = nivel if bloco["nivel"] is None else min(bloco["nivel"], nivel)
            bloco["opcoes"].append(fid)
            total_mov += 1

        if not escolhas:
            continue
        classe["progressao"] = concedidas
        blocos = []
        for eixo, dados in sorted(escolhas.items()):
            # A progressao do Foundry lista so o que ELE modela: o Barbaro
            # aparecia com 1 instinct, o Mago com 14 escolas. O AoN conhece 16 e
            # 23. As opcoes reais sao a uniao -- o Foundry traz a mecanica, o AoN
            # traz a cobertura --, e cada eixo pertence a uma classe so, entao
            # nao ha risco de vazar opcao de outra.
            da_progressao = set(dados["opcoes"])
            # dedupe por NOME: a mesma escola existe como
            # `wb:class-feature/school-of-battle-magic` (com mecanica, do
            # Foundry) e como `wb:arcane-school/battle-magic` (do catalogo do
            # AoN). Unir por id somaria as duas e inflaria 14 + 23 = 37 opcoes
            # para uma classe que escolhe entre 23.
            nomes_com_mecanica = {norm((por_id.get(i) or {}).get("name"))
                                  for i in da_progressao}
            so_catalogo = [
                r["id"] for r in base
                if r.get("kind") == eixo and norm(r.get("name")) not in nomes_com_mecanica]
            blocos.append({
                "eixo": eixo, "nivel": dados["nivel"], "slot": "subclasse",
                "escolhe": 1,
                "opcoes": sorted(da_progressao | set(so_catalogo)),
                "com_mecanica": sorted(da_progressao),
                "so_catalogo": sorted(so_catalogo),
            })
        classe["subclasses"] = blocos
        classe.setdefault("prov", {})["subclasses"] = "aon (categoria propria por eixo)"
        relatorio.append(
            f"- **{classe.get('name')}**: progressao {len(prog)} -> "
            f"{len(concedidas)} concedidas; " +
            ", ".join(f"`{b['eixo']}` ({len(b['opcoes'])} opcoes no nivel "
                      f"{b['nivel']}: {len(b['com_mecanica'])} com mecanica, "
                      f"{len(b['so_catalogo'])} so catalogo)" for b in blocos))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    print(f"classes com sub-escolha separada: {len(relatorio)}")
    print(f"entradas movidas de concessao para opcao: {total_mov}")
    open(f"{BASE}/relatorio_subclasses.md", "w").write(
        "# Sub-escolhas de classe\n\n"
        "A progressao tem dois niveis: `classe -> feature -> sub-escolha`. Esta\n"
        "passada separa o que a classe **concede** do que ela manda **escolher**.\n"
        "Sem isso, `wb:class/wizard` declarava 37 features no nivel 1, entre elas\n"
        "todas as escolas de magia ao mesmo tempo.\n\n"
        f"- classes afetadas: **{len(relatorio)}**\n"
        f"- entradas movidas: **{total_mov}**\n\n## Por classe\n\n"
        + "\n".join(relatorio) + "\n")
    print("-> base/relatorio_subclasses.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
