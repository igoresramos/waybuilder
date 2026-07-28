/**
 * Carrega o payload do pipeline no navegador.
 *
 * A BASE INTEIRA: 54 kinds, 19.705 registros, 1,09 MB gzip. Ate 2026-07-28
 * carregava so os oito kinds que montam ficha, para segurar a primeira carga em
 * 0,53 MB -- e o corte amputava o app em silencio. O motor sabe calcular ataque
 * e dano por arma, CA com cap de DEX e escudo, os slots das 11 classes
 * conjuradoras e a ficha do companheiro; sem `weapon`, `armor`, `shield`,
 * `spell` e `animal-companion` no payload, nada disso tinha como aparecer. A
 * aba de Ataques dizia "nenhuma arma equipada" para sempre.
 *
 * O gargalo real nunca foi o indice: a prosa sozinha tem 17,9 MB e continua
 * sendo buscada por registro, sob demanda.
 *
 * Sem backend: sao arquivos estaticos servidos junto com o app, e por isso o
 * construtor funciona offline depois da primeira visita.
 */
import { Base } from "./motor/base";
import type { Registro } from "./motor/tipos";

export interface BaseCarregada {
  base: Base;
  registros: number;
  kinds: string[];
  bytes: number;
}

interface Manifesto {
  registros?: number;
  kinds?: number;
  por_kind?: Record<string, { registros: number; gzip_bytes: number }>;
}

async function fatia(kind: string, raiz: string): Promise<Registro[]> {
  const r = await fetch(`${raiz}/por-kind/${kind}.json`);
  if (!r.ok) {
    throw new Error(`nao carregou o kind \`${kind}\` (HTTP ${r.status})`);
  }
  return (await r.json()) as Registro[];
}

/**
 * Carrega tudo. A lista de kinds vem do MANIFESTO, nao de uma constante daqui:
 * kind novo no pipeline passa a viajar sozinho, e nao existe mais a chance de
 * o app ficar sem um dado porque alguem esqueceu de editar um array.
 */
export async function carregarNucleo(
  raiz = `${import.meta.env.BASE_URL}base`,
): Promise<BaseCarregada> {
  const r = await fetch(`${raiz}/_manifesto.json`);
  if (!r.ok) throw new Error(`nao carregou o manifesto (HTTP ${r.status})`);
  const manifesto = (await r.json()) as Manifesto;
  const kinds = Object.keys(manifesto.por_kind ?? {});
  if (!kinds.length) throw new Error("manifesto sem `por_kind`");

  // em paralelo: sao arquivos independentes, e serializar multiplicaria a
  // latencia da primeira carga pelo numero de kinds
  const fatias = await Promise.all(kinds.map((k) => fatia(k, raiz)));
  const registros = fatias.flat();
  return {
    base: new Base(registros),
    registros: registros.length,
    kinds,
    bytes: fatias.reduce((n, f) => n + JSON.stringify(f).length, 0),
  };
}

/**
 * A prosa de um registro, buscada quando o jogador abre aquele registro.
 *
 * Ela sozinha e maior que o indice inteiro (17,9 MB contra 1,09 MB), e por
 * isso nunca viaja na carga inicial. O indice guarda so o ponteiro (`text`).
 */
const cacheDeProsa = new Map<string, Record<string, string>>();

export async function prosa(
  ponteiro: string | undefined,
  raiz = `${import.meta.env.BASE_URL}base`,
): Promise<string | null> {
  // formato: wb:text/<kind>/<slug>
  if (!ponteiro || !ponteiro.startsWith("wb:text/")) return null;
  const kind = ponteiro.slice("wb:text/".length).split("/")[0];
  if (!kind) return null;

  if (!cacheDeProsa.has(kind)) {
    try {
      const r = await fetch(`${raiz}/text/${kind}.json`);
      cacheDeProsa.set(kind, r.ok ? await r.json() : {});
    } catch {
      // prosa e enfeite: se nao carregar, a ficha continua funcionando
      cacheDeProsa.set(kind, {});
    }
  }
  return cacheDeProsa.get(kind)?.[ponteiro] ?? null;
}
