/**
 * O nome de exibicao de um trait.
 *
 * Quase sempre basta o registro do kind `trait`, que traz o nome ja em caixa
 * correta (`Dwarf`, `Agile`, `Flourish`). Mas 62 slugs distintos NAO tem
 * registro proprio, e nenhum deles e descuido: sao os traits PARAMETRIZADOS de
 * arma, onde o parametro faz parte do nome --  `two-hand-d8` (155 usos),
 * `versatile-p` (71), `deadly-d8` (53), `thrown-20` (37).
 *
 * Sem tratamento eles apareciam crus e em minusculo no meio de traits em caixa
 * alta, que e feio e, pior, parece defeito de dado.
 *
 * As convencoes de caixa vem do proprio PF2e:
 *   - o dado fica minusculo:      `d8`, `d10`   (Deadly d8)
 *   - a letra de dano fica maiuscula: `P`, `S`, `B`  (Versatile P)
 *   - numero solto e distancia:   `thrown-20` -> `Thrown 20 ft.`
 */
import type { Base } from "./motor/base";

const DADO = /^d\d+$/i;
const NUMERO = /^\d+$/;

/** `two-hand-d8` -> `Two-Hand d8`; `versatile-p` -> `Versatile P`. */
export function formatarSlugDeTrait(slug: string): string {
  const partes = slug.split("-");
  const saida: string[] = [];

  partes.forEach((parte, i) => {
    if (DADO.test(parte)) {
      // o dado nao entra na juncao por hifen: `Deadly d8`, nao `Deadly-D8`
      saida.push(` ${parte.toLowerCase()}`);
      return;
    }
    if (NUMERO.test(parte)) {
      saida.push(` ${parte} ft.`);
      return;
    }
    const palavra = parte.length === 1
      ? parte.toUpperCase()                                  // Versatile P
      : parte.charAt(0).toUpperCase() + parte.slice(1);      // Two-Hand
    saida.push(i === 0 ? palavra : `-${palavra}`);
  });

  // uma letra solta depois de hifen e sufixo de dano, e vem separada por espaco
  return saida.join("").replace(/-([A-Z])(?![a-z])/g, " $1").trim();
}

export function nomeDeTrait(base: Base, slug: string): string {
  return base.opcional(`wb:trait/${slug}`)?.name ?? formatarSlugDeTrait(slug);
}
