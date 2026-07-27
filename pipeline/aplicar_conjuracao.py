#!/usr/bin/env python3
"""
Injeta a tabela de conjuracao nas classes da base.

`extratores/conjuracao.py` produz `saida/conjuracao.json` com slots por nivel de
classe, tradicao, tipo (prepared/spontaneous), progressao de proficiencia e
focus pool das 11 classes conjuradoras. Nada disso chegava a `base/index.json`:
o arquivo nao esta em `ENTRADA` do reconciliador -- e nao poderia estar, porque
e um mapa `{meta, classes}`, nao uma lista de registros com `id`.

Efeito pratico: `wb:class/wizard` saia com `spellcasting: true` e mais nada.
Sem numero de slots nao da para montar ficha de conjurador, e as regras 16 e 17
das houserules (slots pelo nivel de classe cru, elevacao por
`ceil(nivel_de_personagem / 2)`) nao tinham em que se apoiar.

Entrada: pipeline/base/index.json + pipeline/saida/conjuracao.json
Saida:   index.json reescrito
"""
import json, os, sys, unicodedata, re

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
CONJURACAO = f"{AQUI}/saida/conjuracao.json"


def slug(nome):
    s = unicodedata.normalize("NFKD", str(nome or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def main():
    if not os.path.exists(CONJURACAO):
        print(f"sem {CONJURACAO} -- rode extratores/conjuracao.py", file=sys.stderr)
        return 1

    conj = json.load(open(CONJURACAO))
    tabelas = conj.get("classes") or {}
    base = json.load(open(f"{BASE}/index.json"))
    por_id = {r["id"]: r for r in base}

    aplicadas, ausentes = 0, []
    for chave, dados in tabelas.items():
        alvo = por_id.get(f"wb:class/{slug(chave)}")
        if alvo is None:
            alvo = por_id.get(f"wb:class/{slug(dados.get('class'))}")
        if alvo is None:
            ausentes.append(chave)
            continue
        # `spellcasting` deixa de ser booleano e passa a carregar a tabela.
        # Quem so quer saber "conjura?" continua lendo verdade/falsidade do
        # dicionario nao vazio.
        alvo["spellcasting"] = {
            "tradition": dados.get("tradition"),
            "type": dados.get("type"),
            "proficiency": dados.get("proficiency"),
            "focus_pool": dados.get("focus_pool"),
            "slots_per_level": dados.get("slots_per_level"),
            "notas": dados.get("slots_footnotes"),
        }
        prov = alvo.setdefault("prov", {})
        prov["spellcasting"] = (dados.get("prov") or {}).get(
            "slots_per_level", "pf2etools")
        alvo.setdefault("xref", {}).update(
            {f"conjuracao_{k}": v for k, v in (dados.get("xref") or {}).items()})
        aplicadas += 1

    # classe sem tabela: marcar explicitamente em vez de deixar `true` mentindo
    for r in base:
        if r.get("kind") != "class":
            continue
        if r.get("spellcasting") is True:
            r["spellcasting"] = {"tradition": None, "type": None,
                                 "slots_per_level": None,
                                 "notas": "sem tabela em fonte nenhuma"}

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    conjuradoras = [r for r in base if r.get("kind") == "class"
                    and isinstance(r.get("spellcasting"), dict)
                    and r["spellcasting"].get("slots_per_level")]
    print(f"tabelas aplicadas: {aplicadas}")
    print(f"classes com slots na base: {len(conjuradoras)}")
    if ausentes:
        print(f"sem classe correspondente na base: {ausentes}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
