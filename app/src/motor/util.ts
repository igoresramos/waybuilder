/**
 * Peças de fidelidade ao Python.
 *
 * Porte de `motor/motor.py`. Cada helper aqui existe porque uma tradução
 * ingênua de Python para JS erra o valor: divisão inteira, ordenação de
 * tupla, formatação de número com sinal, `repr` de lista dentro de f-string.
 * O contrato do porte é bater EXATAMENTE com `motor/fixtures/*.json`, então
 * "quase igual" é falha.
 */
import type { Rank } from "./tipos.ts";
import { RANKS } from "./tipos.ts";

export const RANK_BONUS: Record<Rank, number> = {
  untrained: 0, trained: 2, expert: 4, master: 6, legendary: 8,
};

// -- narrowing do dado da base (que é livre por definição) ------------------

export function ehDict(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

export function ehLista(v: unknown): v is unknown[] {
  return Array.isArray(v);
}

export function ehStr(v: unknown): v is string {
  return typeof v === "string";
}

/** `isinstance(x, int)` do Python: JSON `1` é int, `1.0` é float. */
export function ehInt(v: unknown): v is number {
  return typeof v === "number" && Number.isInteger(v);
}

/** `x or {}` do Python, para o caso normal de campo ausente ou nulo. */
export function dictDe(v: unknown): Record<string, unknown> {
  return ehDict(v) ? v : {};
}

/** `x or []` do Python. */
export function listaDe(v: unknown): unknown[] {
  return ehLista(v) ? v : [];
}

/**
 * `for x in (v or [])` do Python sobre valor VINDO DO DOCUMENTO, onde o jogador
 * pode ter escrito qualquer coisa.
 *
 * Não é o mesmo que `listaDe`: iterar uma string em Python entrega os
 * CARACTERES, e iterar um dict entrega as CHAVES. `{"slot": "boosts_livres",
 * "pega": "str"}` (string onde devia haver lista) soma +1 em `s`, `t` e `r` no
 * Python -- e o porte tem de errar igual, senão os dois motores discordam
 * justamente na ficha malformada, que é quando o jogador precisa do aviso.
 */
export function pyIterar(v: unknown): unknown[] {
  if (ehLista(v)) return v;
  if (ehStr(v)) return Array.from(v);
  if (ehDict(v)) return Object.keys(v);
  return [];
}

/** `.get(chave, padrao)`: o padrão vale só quando a CHAVE falta, nunca quando
 * o valor é nulo -- diferença que muda o texto de aviso e o campo da ficha. */
export function obter(obj: Record<string, unknown>, chave: string,
                      padrao: unknown = null): unknown {
  return Object.hasOwn(obj, chave) ? obj[chave] : padrao;
}

/** `(reg or {}).get("name", padrao)`, o padrão mais repetido do motor. */
export function nomeOu(reg: Record<string, unknown> | null | undefined,
                       padrao: string): string {
  const d = reg ?? {};
  if (!Object.hasOwn(d, "name")) return padrao;
  const n = d["name"];
  return ehStr(n) ? n : padrao;
}

/** `(reg or {}).get("name")` -- pode ser nulo, e o nulo importa na saída. */
export function nome(reg: Record<string, unknown> | null | undefined): string | null {
  const n = (reg ?? {})["name"];
  return ehStr(n) ? n : null;
}

/** `int(x or 0)` sobre dado da base. */
export function inteiro(v: unknown, padrao = 0): number {
  if (typeof v === "number" && Number.isFinite(v)) return Math.trunc(v);
  if (typeof v === "boolean") return v ? 1 : 0;
  if (typeof v === "string") {
    const n = Number(v.trim());
    if (Number.isFinite(n)) return Math.trunc(n);
  }
  return padrao;
}

/** Verdade do Python: 0, "", [], {}, None e False são falsos. */
export function verdadeiro(v: unknown): boolean {
  if (v === null || v === undefined || v === false || v === 0 || v === "") return false;
  if (ehLista(v)) return v.length > 0;
  if (ehDict(v)) return Object.keys(v).length > 0;
  return Boolean(v);
}

// -- formatação -------------------------------------------------------------

/** `f"{n:+d}"`: o zero sai `+0`, e é assim que a ficha do Python está escrita. */
export function comSinal(n: number): string {
  return n < 0 ? String(n) : `+${n}`;
}

/** `repr()` do Python. Aparece dentro de f-string sempre que se interpola uma
 * LISTA (`f"niveis validos: {niveis}"` vira `[1, 2, 4]`, não `1,2,4`). */
export function pyRepr(v: unknown): string {
  if (v === null || v === undefined) return "None";
  if (typeof v === "boolean") return v ? "True" : "False";
  if (typeof v === "number") return String(v);
  if (ehStr(v)) return `'${v.replace(/\\/g, "\\\\").replace(/'/g, "\\'")}'`;
  if (ehLista(v)) return `[${v.map(pyRepr).join(", ")}]`;
  if (ehDict(v)) {
    return `{${Object.entries(v).map(([k, x]) => `${pyRepr(k)}: ${pyRepr(x)}`).join(", ")}}`;
  }
  return String(v);
}

/** `str()` do Python -- o que uma f-string faz com o valor interpolado. */
export function pyStr(v: unknown): string {
  if (v === null || v === undefined) return "None";
  if (typeof v === "boolean") return v ? "True" : "False";
  if (ehStr(v)) return v;
  if (typeof v === "number") return String(v);
  return pyRepr(v);
}

// -- ordenação --------------------------------------------------------------

/** `sorted()` de string no Python é por CODE POINT; o `<` do JS é por unidade
 * UTF-16, e os dois discordam acima do BMP. */
export function cmpTexto(a: string, b: string): number {
  const ca = Array.from(a);
  const cb = Array.from(b);
  const n = Math.min(ca.length, cb.length);
  for (let i = 0; i < n; i += 1) {
    const x = ca[i].codePointAt(0) ?? 0;
    const y = cb[i].codePointAt(0) ?? 0;
    if (x !== y) return x < y ? -1 : 1;
  }
  return ca.length - cb.length;
}

export type ChaveDeOrdem = number | string | boolean;

function cmpChave(a: ChaveDeOrdem, b: ChaveDeOrdem): number {
  if (typeof a === "string" && typeof b === "string") return cmpTexto(a, b);
  const x = typeof a === "boolean" ? (a ? 1 : 0) : (a as number);
  const y = typeof b === "boolean" ? (b ? 1 : 0) : (b as number);
  return x === y ? 0 : x < y ? -1 : 1;
}

/**
 * `lista.sort(key=...)` do Python, com chave de tupla.
 *
 * `Array.sort()` sem comparador converte para string -- `[2, 10]` viraria
 * `[10, 2]`. Todo `sorted` do motor passa por aqui de propósito. A ordenação
 * do JS é estável desde ES2019, como a do Python, então empate preserva a
 * ordem de entrada (o que a lista de candidatos depende).
 */
export function ordenarPor<T>(itens: T[], chave: (x: T) => ChaveDeOrdem[]): T[] {
  return itens
    .map((x) => ({ x, k: chave(x) }))
    .sort((a, b) => {
      const n = Math.min(a.k.length, b.k.length);
      for (let i = 0; i < n; i += 1) {
        const c = cmpChave(a.k[i], b.k[i]);
        if (c !== 0) return c;
      }
      return 0;
    })
    .map((p) => p.x);
}

/** `sorted(lista_de_numeros)`. */
export function ordenarNumeros(v: Iterable<number>): number[] {
  return [...v].sort((a, b) => a - b);
}

/** `sorted(lista_de_strings)`. */
export function ordenarTextos(v: Iterable<string>): string[] {
  return [...v].sort(cmpTexto);
}

// -- defaultdict ------------------------------------------------------------

/** `defaultdict(list)`: a chave nasce na primeira escrita, nunca na leitura
 * feita por aqui -- e é isso que mantém `origem_proficiencia` sem chave vazia. */
export function empurrar<K, V>(m: Map<K, V[]>, chave: K, valor: V): void {
  const atual = m.get(chave);
  if (atual === undefined) m.set(chave, [valor]);
  else atual.push(valor);
}

/** `defaultdict(int)` com `+= n`. */
export function somar<K>(m: Map<K, number>, chave: K, delta: number): void {
  m.set(chave, (m.get(chave) ?? 0) + delta);
}

// -- as duas funções que aparecem em todo lugar -----------------------------

/** `'cloistered_cleric'` e `'cloistered-cleric'` são a mesma chave. */
export function normSlug(s: unknown): string {
  // `str(s or "")` do Python: valor falso (None, 0, "") vira string vazia
  const texto = verdadeiro(s) ? String(s) : "";
  return texto.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

export function normChave(registro: Record<string, unknown>): string {
  const n = registro["name"];
  if (verdadeiro(n)) return normSlug(n);
  const id = ehStr(registro["id"]) ? registro["id"] : "";
  const partes = id.split("/");
  return normSlug(partes[partes.length - 1]);
}

/** Regra 4: entre duas classes que concedem a mesma proficiência, vale a melhor. */
export function melhorRank(a: unknown, b: unknown): Rank {
  const lista: string[] = RANKS;
  const ia = ehStr(a) && lista.includes(a) ? lista.indexOf(a) : 0;
  const ib = ehStr(b) && lista.includes(b) ? lista.indexOf(b) : 0;
  return RANKS[Math.max(ia, ib)];
}

/** Índice do rank, com o mesmo fallback do Python (`0` para desconhecido). */
export function indiceDeRank(r: unknown): number {
  const lista: string[] = RANKS;
  return ehStr(r) && lista.includes(r) ? lista.indexOf(r) : 0;
}
