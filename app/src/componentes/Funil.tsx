/**
 * O filtro fino do picker -- o funil do Pathbuilder.
 *
 * As abas do topo cortam por CATEGORIA (feat de classe, dedicacao, arquetipo).
 * O funil corta pelo resto, e o resto e o que mais aparece na mesa: "so o que eu
 * consigo pegar", "so ate o nivel 5", "so os que tem trait `stance`".
 *
 * A lista de traits e derivada dos candidatos daquele slot, nao de um catalogo
 * fixo: num slot de feat de Guerreiro so aparecem os traits que os feats de
 * Guerreiro tem, e o filtro nunca oferece uma opcao que devolveria zero.
 *
 * Nada aqui e ligado por padrao. O picker abre mostrando tudo -- e o principio
 * zero do projeto: esconder e escolha do jogador, nunca do app.
 */
import { useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Candidato } from "../motor/tipos";
import { nomeDeTrait } from "../nomeDeTrait";

export interface EstadoDoFunil {
  soAtende: boolean;
  nivelMax: number | null;
  traits: string[];
}

export const FUNIL_VAZIO: EstadoDoFunil = {
  soAtende: false, nivelMax: null, traits: [],
};

export const funilLigado = (f: EstadoDoFunil) =>
  f.soAtende || f.nivelMax !== null || f.traits.length > 0;

/** Aplica o funil. Fora do componente para o teste poder exercitar sozinho. */
export function aplicarFunil(
  lista: Candidato[], f: EstadoDoFunil, base: Base,
): Candidato[] {
  return lista.filter((c) => {
    if (f.soAtende && !c.atende) return false;
    if (f.nivelMax !== null && (c.level ?? 0) > f.nivelMax) return false;
    if (f.traits.length) {
      const suas = (base.opcional(c.id)?.traits ?? []) as string[];
      // E, nao OU: marcar `stance` e `flourish` pede quem tem os dois
      if (!f.traits.every((t) => suas.includes(t))) return false;
    }
    return true;
  });
}

export function Funil({
  candidatos, base, estado, aoMudar,
}: {
  candidatos: Candidato[];
  base: Base;
  estado: EstadoDoFunil;
  aoMudar: (f: EstadoDoFunil) => void;
}) {
  const [aberto, setAberto] = useState(false);

  /** Os traits que ESTES candidatos tem, do mais comum para o menos. */
  const traits = useMemo(() => {
    const conta = new Map<string, number>();
    for (const c of candidatos) {
      for (const t of ((base.opcional(c.id)?.traits ?? []) as string[])) {
        conta.set(t, (conta.get(t) ?? 0) + 1);
      }
    }
    return [...conta.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .slice(0, 24);
  }, [candidatos, base]);

  const nomeDoTrait = (slug: string) => nomeDeTrait(base, slug);

  const alternarTrait = (t: string) =>
    aoMudar({
      ...estado,
      traits: estado.traits.includes(t)
        ? estado.traits.filter((x) => x !== t)
        : [...estado.traits, t],
    });

  return (
    <div className="funil">
      <button className={`funil-botao ${funilLigado(estado) ? "ligado" : ""}`}
              onClick={() => setAberto(!aberto)}
              aria-expanded={aberto} aria-label="filtros">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none"
             stroke="currentColor" strokeWidth="1.8" aria-hidden>
          <path d="M3 5h18l-7 8v6l-4 2v-8z" strokeLinejoin="round" />
        </svg>
        {funilLigado(estado) && <span className="funil-marca" />}
      </button>

      {aberto && (
        <div className="funil-painel">
          <label className="funil-linha">
            <input type="checkbox" checked={estado.soAtende}
                   onChange={(e) => aoMudar({ ...estado, soAtende: e.target.checked })} />
            so o que eu posso pegar agora
          </label>

          <label className="funil-linha">
            ate o nivel
            <input type="number" min={1} max={20} className="funil-nivel"
                   value={estado.nivelMax ?? ""}
                   placeholder="todos"
                   onChange={(e) => aoMudar({
                     ...estado,
                     nivelMax: e.target.value ? Number(e.target.value) : null,
                   })} />
          </label>

          {traits.length > 0 && (
            <>
              <div className="funil-titulo">traits</div>
              <div className="funil-traits">
                {traits.map(([t, n]) => (
                  <button key={t}
                          className={`trait ${estado.traits.includes(t) ? "sel" : ""}`}
                          onClick={() => alternarTrait(t)}
                          aria-pressed={estado.traits.includes(t)}>
                    {nomeDoTrait(t)} <span className="conta">{n}</span>
                  </button>
                ))}
              </div>
            </>
          )}

          {funilLigado(estado) && (
            <button className="funil-limpar" onClick={() => aoMudar(FUNIL_VAZIO)}>
              limpar filtros
            </button>
          )}
        </div>
      )}
    </div>
  );
}
