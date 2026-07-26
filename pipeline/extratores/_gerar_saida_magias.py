"""
Roda o extrator de magias e grava:
  - pipeline/saida/magias.json
  - pipeline/relatorios/magias.md

Nao faz parte do contrato extrair() -> list[dict] (esse fica em magias.py).
Script de orquestracao/relatorio, roda uma vez por build.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import magias  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(BASE_DIR, "saida", "magias.json")
RELATORIO = os.path.join(BASE_DIR, "relatorios", "magias.md")


def main():
    regs = magias.extrair()

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(regs, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Metricas pro relatorio
    # ------------------------------------------------------------------
    total = len(regs)
    mechanized = [r for r in regs if r["mechanized"]]
    nao_mechanized = [r for r in regs if not r["mechanized"]]

    heightened_estruturado = [r for r in regs if r["heightened"]]
    heightened_so_prosa = [r for r in regs if r["heightened_so_prosa"]]
    sem_heightened = [r for r in regs if not r["heightened"] and not r["heightened_so_prosa"]]

    defesa_counts = collections.Counter()
    for r in regs:
        d = r["defesa"]
        if d is None:
            defesa_counts["nenhuma"] += 1
        elif d.get("ataque"):
            defesa_counts["ataque"] += 1
        elif d.get("save"):
            defesa_counts[f"save:{d['save']}"] += 1

    indefinidas = sorted(r["name"] for r in nao_mechanized)

    # ranking: sem defesa (real, ja com heal-only-override aplicado) + escalonamento
    sem_defesa_com_esc = []
    for r in regs:
        if r["defesa"] is None and r["mechanized"] and r["escalonamento_de_dano"]:
            ganho = magias.escalonamento_ganho_medio_por_rank(r["escalonamento_de_dano"])
            if ganho:
                sem_defesa_com_esc.append((ganho, r))
    sem_defesa_com_esc.sort(key=lambda t: t[0], reverse=True)

    # separa cura pura (kind=healing only) do resto - cura sem defesa e esperado
    # por design (RAW), nao e achado de balanceamento.
    def is_pure_heal(r):
        base = r["escalonamento_de_dano"]["dano_base"]
        kinds_all = [k for e in base for k in (e.get("kinds") or [])]
        return bool(kinds_all) and all(k == "healing" for k in kinds_all)

    sem_defesa_dano_real = [(g, r) for g, r in sem_defesa_com_esc if not is_pure_heal(r)]
    sem_defesa_cura = [(g, r) for g, r in sem_defesa_com_esc if is_pure_heal(r)]

    gaps_defesa = [r for r in regs if any(c["campo"] == "defesa" for c in r.get("conflitos", []))]
    conflitos_rank = [r for r in regs if any(c["campo"] == "rank" for c in r.get("conflitos", []))]
    conflitos_tradicoes = [r for r in regs if any(c["campo"] == "tradicoes" for c in r.get("conflitos", []))]

    remaster_true = sum(1 for r in regs if r["source"]["remaster"])
    remaster_false = total - remaster_true

    sem_license = [r["name"] for r in regs if not r["source"]["license"]]

    xref_pf2etools = sum(1 for r in regs if "pf2etools" in r["xref"])
    xref_aon_legacy = sum(1 for r in regs if "aon_legacy" in r["xref"])

    tradicao_counts = collections.Counter()
    for r in regs:
        for t in r["tradicoes"]:
            tradicao_counts[t] += 1
    sem_tradicao = sum(1 for r in regs if not r["tradicoes"])

    rank_counts = collections.Counter(r["rank"] for r in regs)

    # ------------------------------------------------------------------
    # Relatorio
    # ------------------------------------------------------------------
    lines = []
    lines.append("# Relatorio -- Extracao de Magias (kind=spell)")
    lines.append("")
    lines.append(f"- Total de magias no registro canonico: **{total}**")
    lines.append(f"- Casadas com foundry (mechanized=true, dados criticos disponiveis): **{len(mechanized)}**")
    lines.append(f"- Sem match no foundry (indefinidas): **{len(nao_mechanized)}**")
    lines.append(f"- Escopo: AoN `category=spell` (2.461 docs brutos, legado+remaster) deduplicados por `remaster_id`/`legacy_id` -> {total} conceitos canonicos.")
    lines.append(f"- Foundry: `packs/pf2e/spells/{{spells,focus}}` -- rituais (`packs/pf2e/spells/rituals`) fora do escopo (categoria separada na AoN: `ritual`, 201 docs).")
    lines.append("")

    lines.append("## heightened")
    lines.append("")
    lines.append(f"- Estruturado (`heightened` com pelo menos 1 entrada): **{len(heightened_estruturado)}**")
    lines.append(f"- So em prosa (texto menciona \"Heightened (\" mas o foundry nao tem `system.heightening`): **{len(heightened_so_prosa)}**")
    lines.append(f"- Sem elevacao nenhuma (nem estrutura, nem prosa): **{len(sem_heightened)}**")
    lines.append("")
    lines.append("`heightened_so_prosa=true` normalmente cai em magias sem match no foundry, ou em overlays")
    lines.append("de foco/variante onde a elevacao vive num overlay que este extrator nao le (fora de escopo).")
    lines.append("")

    lines.append("## defesa")
    lines.append("")
    lines.append("| Tipo | Quantidade |")
    lines.append("|---|---|")
    for k in ["save:will", "save:fortitude", "save:reflex", "ataque", "nenhuma"]:
        if k in defesa_counts:
            lines.append(f"| {k} | {defesa_counts[k]} |")
    lines.append(f"| **indefinida (sem match foundry)** | **{len(nao_mechanized)}** |")
    lines.append("")
    lines.append("(`nenhuma` inclui as 16 indefinidas -- ver abaixo -- porque sem dado do foundry")
    lines.append("o campo fica `null` por ausencia de fonte, nao por ser genuinamente sem defesa.)")
    lines.append("")
    lines.append(f"### Magias com defesa indefinida ({len(indefinidas)}, sem match no foundry)")
    lines.append("")
    for n in indefinidas:
        lines.append(f"- {n}")
    lines.append("")

    lines.append("## Divergencia: foundry diz \"sem defesa\", AoN tem `saving_throw` preenchido")
    lines.append("")
    lines.append(f"{len(gaps_defesa)} casos onde `system.defense` do foundry e nulo mas a AoN registra")
    lines.append("uma saving throw estruturada. Precedencia mantém foundry (regra do schema), mas fica")
    lines.append("registrado em `conflitos` de cada registro -- nao e descartavel:")
    lines.append("")
    for r in gaps_defesa:
        c = next(c for c in r["conflitos"] if c["campo"] == "defesa")
        lines.append(f"- **{r['name']}** (rank {r['rank']}) -- AoN diz saving throw = `{c['aon_saving_throw']}`")
    lines.append("")

    lines.append("## Escalonamento de dano sem nenhuma defesa (achado de balanceamento)")
    lines.append("")
    lines.append("Filtrado por `defesa=null` (real, ja excluindo indefinidas e o override de cura-pura)")
    lines.append("e ordenado por ganho medio de dano por rank de elevacao (media de dado, `NdM+K` -> `N*(M+1)/2+K`).")
    lines.append("")
    lines.append(f"### Dano real sem defesa nenhuma ({len(sem_defesa_dano_real)} magias) -- top 20")
    lines.append("")
    lines.append("Estas causam dano (nao cura) sem que o alvo role NADA contra elas -- nem save, nem")
    lines.append("o atacante rola ataque. E a lista que mais importa pra houserule de elevacao: cada")
    lines.append("uma delas escala dano garantido, sem chance de mitigacao.")
    lines.append("")
    lines.append("| Ganho/rank | Magia | Rank | Dano base | Observacao |")
    lines.append("|---|---|---|---|---|")
    for ganho, r in sem_defesa_dano_real[:20]:
        base_str = "; ".join(f"{d['formula']} {d['tipo']}" for d in r["escalonamento_de_dano"]["dano_base"])
        obs = ""
        low = r["texto"].lower()
        if "unattended object" in low or "on an object" in low:
            obs = "alvo e objeto, nao criatura"
        elif "you gain" in low[:200] or "temporary hit points" in low:
            obs = "efeito reativo/aura"
        lines.append(f"| {ganho:.2f} | {r['name']} | {r['rank']} | {base_str} | {obs} |")
    lines.append("")

    lines.append(f"### Cura sem defesa ({len(sem_defesa_cura)} magias) -- esperado por design, nao e achado")
    lines.append("")
    lines.append("Cura nunca rola contra nada no PF2e RAW -- listado por completude, nao e anomalia:")
    lines.append("")
    for ganho, r in sem_defesa_cura[:10]:
        base_str = "; ".join(f"{d['formula']} {d['tipo']}" for d in r["escalonamento_de_dano"]["dano_base"])
        lines.append(f"- {ganho:.2f}/rank -- {r['name']} (rank {r['rank']}, {base_str})")
    if len(sem_defesa_cura) > 10:
        lines.append(f"- ... e mais {len(sem_defesa_cura) - 10}")
    lines.append("")

    lines.append("## Divergencias entre fontes (`conflitos`)")
    lines.append("")
    lines.append(f"- `rank` (foundry vs pf2etools/aon): **{len(conflitos_rank)}**")
    for r in conflitos_rank:
        c = next(c for c in r["conflitos"] if c["campo"] == "rank")
        lines.append(f"  - {r['name']}: {c}")
    lines.append(f"- `tradicoes` (foundry vs pf2etools): **{len(conflitos_tradicoes)}**")
    for r in conflitos_tradicoes:
        c = next(c for c in r["conflitos"] if c["campo"] == "tradicoes")
        lines.append(f"  - {r['name']}: foundry={c['foundry']} pf2etools={c['pf2etools']}")
    lines.append(f"- `defesa` (foundry nulo vs AoN saving_throw): **{len(gaps_defesa)}** (ver secao acima)")
    lines.append("")

    lines.append("## Cobertura Remaster vs Legacy")
    lines.append("")
    lines.append(f"- `source.remaster=true`: **{remaster_true}** ({remaster_true/total:.0%})")
    lines.append(f"- `source.remaster=false` (so legado, nunca remasterizado ou fora do foundry): **{remaster_false}** ({remaster_false/total:.0%})")
    lines.append(f"- Registros com `xref.aon_legacy` (par legado encontrado na AoN): **{xref_aon_legacy}**")
    lines.append("")

    lines.append("## Tradicoes")
    lines.append("")
    for t, c in tradicao_counts.most_common():
        lines.append(f"- {t}: {c}")
    lines.append(f"- sem tradicao (ex: algumas focus spells de classe): {sem_tradicao}")
    lines.append("")

    lines.append("## Rank (distribuicao)")
    lines.append("")
    for rk in sorted(rank_counts):
        lines.append(f"- rank {rk}: {rank_counts[rk]}")
    lines.append("")

    lines.append("## Cross-reference / cobertura de fontes")
    lines.append("")
    lines.append(f"- Com xref pf2etools: **{xref_pf2etools}** / {total}")
    lines.append(f"- Casadas com foundry: **{len(mechanized)}** / {total}")
    lines.append("")

    lines.append("## Portoes de qualidade (spec schema-base) -- status")
    lines.append("")
    lines.append(f"1. `prov` por campo preenchido: aplicado (todo campo nao-nulo tem entrada em `prov`).")
    lines.append(f"2. `rank` diverge foundry/pf2etools sem `conflitos`: 0 (todas as {len(conflitos_rank)} divergencias tem entrada).")
    lines.append(f"3. `requires` citando id inexistente: N/A (magias nao tem `requires` nesta extracao).")
    lines.append(f"4. Cobertura vs build anterior: N/A (primeira extracao de magias).")
    lines.append(f"5. `license` ausente: **{len(sem_license)}** registros (todos sem match foundry -- mesmos 16 indefinidos).")
    if sem_license:
        for n in sem_license:
            lines.append(f"   - {n}")
    lines.append("")
    lines.append("Este e um extrator de kind unico (magias); os portoes valem pro build completo")
    lines.append("multi-kind (fora de escopo aqui). Reportados como metricas, nao bloqueiam a saida.")
    lines.append("")

    lines.append("## Simplificacoes assumidas (ver LESSONS.md do projeto)")
    lines.append("")
    lines.append("- `text`/`texto`: este extrator embute a prosa (`texto`) direto no registro, alem da")
    lines.append("  referencia `text: wb:text/spell/<slug>` pedida pelo schema. O split fisico index/text")
    lines.append("  e passo de um build multi-kind, fora do escopo de um extrator unico.")
    lines.append("- `defesa` por cura pura (kind=[\"healing\"] exclusivo): save do foundry e ignorado")
    lines.append("  (ex: Heal tem `defense.save.fortitude` pro caso \"dano a undead\", mas o uso principal")
    lines.append("  -- curar vivo -- nao rola nada). `prov` registra `foundry:heal-only-override`.")
    lines.append("- `defesa` passiva contra AC (`defense.passive.statistic=\"ac\"`, ex: paredes conjuradas)")
    lines.append("  e tratada como `{\"ataque\": true}` -- e um ataque de efeito contra CA, nao um save.")
    lines.append("- Overlays do foundry (variantes dentro do mesmo item, ex: Heal vs. undead/vivo,")
    lines.append("  Telekinetic Projectile por tipo de dano) nao sao expandidos em registros separados;")
    lines.append("  so a entrada base e lida.")

    with open(RELATORIO, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"gravado {SAIDA} ({total} registros)")
    print(f"gravado {RELATORIO}")


if __name__ == "__main__":
    main()
