/**
 * O motor no cliente: documento -> visão calculada.
 *
 * Porte de `motor/motor.py`. O gabarito é `motor/fixtures/*.json`, gerado pelo
 * Python; `motor.test.ts` roda os mesmos documentos e compara campo a campo.
 * Divergência é falha, sem tolerância.
 *
 * O Python NÃO sai de cena com o porte: ele continua sendo o oráculo
 * (validação contra os iconics da Paizo, teste de carga, portões do pipeline).
 */
export { Base } from "./base.ts";
export { Personagem } from "./personagem.ts";
export { avaliar, comparar } from "./predicado.ts";
export type { ContextoDePredicado, ResultadoDeTermo } from "./predicado.ts";
export {
  RANK_BONUS, melhorRank, normChave, normSlug,
} from "./util.ts";
export * from "./tipos.ts";

import { Base } from "./base.ts";
import { Personagem } from "./personagem.ts";
import type { Documento, Registro } from "./tipos.ts";

/** Atalho: carrega a base uma vez e deriva um documento. */
export function derivar(doc: Documento, base: Base): Personagem {
  return new Personagem(doc, base);
}

/** A base a partir do payload cru de `pipeline/base/app/index.json`. */
export function carregarBase(registros: Registro[]): Base {
  return new Base(registros);
}
