#!/usr/bin/env python3
"""
Deriva o gate de nivel de cada feat -- `class_level` x `character_level`.

E aqui que a houserule inteira mora, e estava vazio: `class_level` aparecia em
**79 de 19.738 registros**. No PF2e oficial os dois numeros sao sempre iguais,
entao nenhuma fonte precisa distingui-los -- e por isso nenhuma distingue.

O dado, porem, ja esta na base. No PF2e o pre-requisito de um feat **nunca
menciona nivel**: o nivel do feat *e* o gate. Um feat com trait `bard` e
`level: 8` significa, em RAW, "voce e um Bardo de nivel 8". Sob a houserule isso
se parte em dois:

    trait de classe    ->  class_level[X] >= N      (regra 12)
    trait de ancestria ->  character_level >= N + ser daquela ancestria
    archetype          ->  character_level >= N     (regra 13)
    geral / pericia    ->  character_level >= N     (regra 14)

O `requires` que ja existe **nao e sobrescrito**: o gate entra como mais uma
clausula de um `all`. Predicado que a fonte declarou continua valendo.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_gate_nivel.md
"""
import json, os, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# Feat com trait de arquetipo nao pertence a classe nenhuma (regra 13), mesmo
# quando tambem carrega o trait de uma classe.
TRAIT_ARQUETIPO = "archetype"


def _chave(clausula):
    return json.dumps(clausula, sort_keys=True, ensure_ascii=False)


def ja_contem(predicado, gate):
    """O extrator pode ja ter escrito o mesmo gate.

    `hand-of-the-apprentice` saia com `class_level[wizard] >= 1` duas vezes --
    predicado redundante nao muda o resultado, mas polui a auditoria e faz o
    numero de clausulas mentir sobre a complexidade real do requisito.
    """
    alvo = _chave(gate)
    if _chave(predicado) == alvo:
        return True
    if isinstance(predicado, dict):
        for chave in ("all", "any"):
            if chave in predicado and isinstance(predicado[chave], list):
                if any(ja_contem(c, gate) for c in predicado[chave]):
                    return True
    return False


def combinar(existente, gate):
    """Adiciona o gate sem descartar o que a fonte declarou."""
    if not existente:
        return gate
    if ja_contem(existente, gate):
        return existente
    if isinstance(existente, dict) and "all" in existente:
        return {"all": list(existente["all"]) + [gate]}
    return {"all": [existente, gate]}


def main():
    base = json.load(open(f"{BASE}/index.json"))

    classes = {str(r.get("name") or "").lower(): r["id"]
               for r in base if r.get("kind") == "class"}
    ancestrias = {str(r.get("name") or "").lower(): r["id"]
                  for r in base if r.get("kind") == "ancestry"}

    contagem = collections.Counter()
    exemplos = {}

    for r in base:
        if r.get("kind") != "feat":
            continue
        nivel = r.get("level")
        if not isinstance(nivel, int):
            contagem["sem level -- pulado"] += 1
            continue
        traits = {str(t).lower() for t in (r.get("traits") or [])}

        # ordem importa: arquetipo vence trait de classe (regra 13)
        if TRAIT_ARQUETIPO in traits:
            gate = {"character_level": {">=": nivel}}
            grupo = "archetype"
        elif traits & set(classes):
            # UM feat pode pertencer a VARIAS classes, e ai a exigencia e
            # QUALQUER uma delas -- nunca a primeira em ordem alfabetica.
            # Ate 2026-07-27 isto era `sorted(...)[0]`, e o resultado era que
            # `Reach Spell` (bard/cleric/druid/oracle/sorcerer/witch/wizard)
            # saia como `class_level: {bard}`: pelo motor, um Mago nao podia
            # pegar Reach Spell. Eram 122 feats travados assim. Doi dobrado na
            # houserule, que e multiclasse por nivel -- e justo o feat que um
            # Guerreiro 2/Ladino 2 deveria alcancar pelos dois lados.
            nomes = sorted(traits & set(classes))
            gates = [{"class_level": {classes[n].split("/")[-1]: {">=": nivel}}}
                     for n in nomes]
            gate = gates[0] if len(gates) == 1 else {"any": gates}
            grupo = "classe" if len(gates) == 1 else "classe (varias)"
        elif traits & set(ancestrias):
            # mesma correcao: 8 feats tem trait de mais de uma ancestria
            nomes = sorted(traits & set(ancestrias))
            alvo = ({"has": ancestrias[nomes[0]]} if len(nomes) == 1
                    else {"any": [{"has": ancestrias[n]} for n in nomes]})
            gate = {"all": [{"character_level": {">=": nivel}}, alvo]}
            grupo = "ancestria" if len(nomes) == 1 else "ancestria (varias)"
        else:
            gate = {"character_level": {">=": nivel}}
            grupo = "geral"

        r["requires"] = combinar(r.get("requires"), gate)
        r.setdefault("prov", {})["requires"] = (
            (r.get("prov") or {}).get("requires", "") + "+derivado:gate-de-nivel"
        ).lstrip("+")
        r["gate_de_nivel"] = grupo
        contagem[grupo] += 1
        exemplos.setdefault(grupo, (r["id"], r.get("name"), nivel, gate))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    com_class_level = sum(
        1 for r in base if "class_level" in json.dumps(r.get("requires") or {}))
    com_character_level = sum(
        1 for r in base if "character_level" in json.dumps(r.get("requires") or {}))

    print(f"gates derivados: {sum(v for k, v in contagem.items() if 'pulado' not in k)}")
    for g, n in contagem.most_common():
        print(f"  {g:14} {n:>5}")
    print(f"\nregistros usando class_level:     {com_class_level}  (eram 79)")
    print(f"registros usando character_level: {com_character_level}")

    linhas = ["# Gate de nivel derivado", "",
              "No PF2e o pre-requisito de um feat nunca menciona nivel -- o nivel do",
              "feat **e** o gate. Sob a houserule isso se parte em dois numeros, e e",
              "onde a regra caseira inteira mora.", "",
              f"- gates derivados: **{sum(v for k, v in contagem.items() if 'pulado' not in k)}**",
              f"- registros usando `class_level`: **{com_class_level}** (eram 79)",
              f"- registros usando `character_level`: **{com_character_level}**", "",
              "## Por grupo", ""]
    linhas += [f"- `{g}`: {n}" for g, n in contagem.most_common()]
    linhas += ["", "## Exemplo de cada grupo", ""]
    for g, (wid, nome, nivel, gate) in sorted(exemplos.items()):
        linhas.append(f"- **{g}** -- `{wid}` ({nome}, nivel {nivel})")
        linhas.append(f"  ```json\n  {json.dumps(gate, ensure_ascii=False)}\n  ```")
    open(f"{BASE}/relatorio_gate_nivel.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_gate_nivel.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
