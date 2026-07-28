/**
 * A faixa de traits de um registro -- e ela que responde "quem pode pegar isto".
 *
 * Trait no PF2e nao e enfeite: e o gate. `Clan Dagger` carrega `dwarf`, e e so
 * por isso que ela e uma arma anã; `Natural Ambition` carrega `human`, e e so
 * por isso que so humano a pega. Entao a faixa mostra TODAS, com o nome
 * legivel da base (`Versatile B`, nao `versatile-b`) e a descricao oficial no
 * hover -- que e o que o AoN faz.
 *
 * As de ANCESTRALIDADE saem destacadas. O grupo vem do proprio registro da
 * trait (`trait_group`), nao de uma lista nossa: `dwarf` e
 * `['Ancestry','Weapon']`, `agile` e so `['Weapon']`.
 *
 * Heranca e o caso em que a fonte nao declara trait nenhuma -- 260 das 326 no
 * Foundry tem `traits.value` vazio, e o vinculo mora em `system.ancestry`. Esse
 * vinculo aparece marcado como vinculo, nunca disfarcado de trait: fabricar
 * `traits:['human']` faria o motor satisfazer requisito com dado inventado.
 */
import { useEffect, useState } from "react";
import type { Base } from "../motor/base";
import type { Registro } from "../motor/tipos";
import { prosa } from "../carregarBase";
import { nomeDeTrait } from "../nomeDeTrait";

/** O registro da trait, quando o kind `trait` esta carregado. */
const registroDaTrait = (base: Base, slug: string): Registro | null =>
  base.opcional(`wb:trait/${slug}`) ?? null;

const ehDeAncestria = (r: Registro | null): boolean =>
  (r?.trait_group as string[] | undefined)?.includes("Ancestry") ?? false;

function Chip({ base, slug }: { base: Base; slug: string }) {
  const reg = registroDaTrait(base, slug);
  const [texto, setTexto] = useState<string | null>(null);

  // a descricao da trait vem do mesmo arquivo de prosa das demais, e o cache
  // por kind faz a primeira buscar o arquivo e as outras 550 saírem de graca
  useEffect(() => {
    let vivo = true;
    prosa(reg?.text as string | undefined).then((t) => { if (vivo) setTexto(t); });
    return () => { vivo = false; };
  }, [reg]);

  const grupos = (reg?.trait_group as string[] | undefined) ?? [];
  const dica = [texto, grupos.length ? `grupo: ${grupos.join(", ")}` : null]
    .filter(Boolean).join("\n\n");

  return (
    <span className={`trait ${ehDeAncestria(reg) ? "ancestral" : ""}`}
          title={dica || undefined}>
      {nomeDeTrait(base, slug)}
    </span>
  );
}

export function Traits({ base, reg }: { base: Base; reg: Registro }) {
  const traits = reg.traits ?? [];
  const vinculo = typeof reg.ancestry === "string" ? reg.ancestry : null;

  return (
    <div className="traits">
      {reg.rarity && reg.rarity !== "common" && (
        <span className={`trait r-${reg.rarity}`}>{reg.rarity}</span>
      )}
      {traits.map((t) => <Chip key={t} base={base} slug={t} />)}
      {vinculo && (
        <span className="trait ancestral vinculo"
              title="vinculo declarado pela fonte; a heranca nao carrega trait propria">
          {base.opcional(vinculo)?.name ?? vinculo}
        </span>
      )}
      {!traits.length && !vinculo && (
        <span className="trait falta">sem trait na fonte</span>
      )}
    </div>
  );
}
