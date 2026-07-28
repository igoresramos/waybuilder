/**
 * Avaliação do predicado (`requires`). Porte de `Personagem.avaliar` e
 * `_comparar` em `motor/motor.py`.
 *
 * PRINCÍPIO ZERO: isto **nunca** é usado para negar uma escolha. `requires`
 * sugere e ordena, jamais bloqueia. Serve para o app dizer "estes combinam com
 * o que você tem" e para marcar o que está fora.
 */
import { ehDict, ehLista, inteiro, listaDe } from "./util.ts";

export function comparar(tenho: number, operador: unknown, alvo: unknown): boolean {
  const a = inteiro(alvo);
  if (operador === ">=") return tenho >= a;
  if (operador === "<=") return tenho <= a;
  if (operador === "==") return tenho === a;
  return true;          // operador desconhecido não reprova: o app não arbitra
}

/** O que um termo (`class_level`, `has`, `trait`...) devolve. */
export type ResultadoDeTermo = [boolean, string];

/**
 * Quem sabe responder por um termo. `null` = termo desconhecido, que NÃO
 * reprova -- é o `getattr(self, f"_termo_{termo}", None)` do Python.
 */
export interface ContextoDePredicado {
  termo(nome: string, valor: unknown): ResultadoDeTermo | null;
}

/** Devolve `[atende, motivos]`. */
export function avaliar(ctx: ContextoDePredicado, predicado: unknown): [boolean, string[]] {
  if (predicado === null || predicado === undefined) return [true, []];
  if (ehLista(predicado) && predicado.length === 0) return [true, []];
  if (!ehDict(predicado)) return [true, []];
  if (Object.keys(predicado).length === 0) return [true, []];

  if (Object.hasOwn(predicado, "all")) {
    const motivos: string[] = [];
    let ok = true;
    for (const c of listaDe(predicado["all"])) {
      const [passou, m] = avaliar(ctx, c);
      ok = ok && passou;
      motivos.push(...m);
    }
    return [ok, motivos];
  }
  if (Object.hasOwn(predicado, "any")) {
    const resultados = listaDe(predicado["any"]).map((c) => avaliar(ctx, c));
    if (resultados.some((r) => r[0])) return [true, []];
    return [false, resultados.flatMap((r) => r[1])];
  }
  if (Object.hasOwn(predicado, "not")) {
    const [passou] = avaliar(ctx, predicado["not"]);
    return [!passou, passou ? ["condicao proibida presente"] : []];
  }

  for (const [termo, valor] of Object.entries(predicado)) {
    const r = ctx.termo(termo, valor);
    if (r === null) continue;          // termo desconhecido não reprova
    const [passou, motivo] = r;
    if (!passou) return [false, [motivo]];
  }
  return [true, []];
}
