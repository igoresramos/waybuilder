/**
 * Carrega o payload do pipeline no navegador.
 *
 * Só o NUCLEO na primeira carga -- os oito kinds que montam ficha, 510 KB
 * gzip. Equipamento, magia e catalogo de referencia entram sob demanda, quando
 * a tela que os usa existir.
 *
 * Sem backend: sao arquivos estaticos servidos junto com o app, e por isso o
 * construtor funciona offline depois da primeira visita.
 */
import { Base } from "./motor/base";
import type { Registro } from "./motor/tipos";

const NUCLEO = [
  "class", "class-feature", "feat", "ancestry",
  "heritage", "background", "archetype", "skill",
] as const;

export interface BaseCarregada {
  base: Base;
  registros: number;
  kinds: string[];
  bytes: number;
}

async function fatia(kind: string, raiz: string): Promise<Registro[]> {
  const r = await fetch(`${raiz}/por-kind/${kind}.json`);
  if (!r.ok) {
    throw new Error(`nao carregou o kind \`${kind}\` (HTTP ${r.status})`);
  }
  return (await r.json()) as Registro[];
}

export async function carregarNucleo(
  raiz = `${import.meta.env.BASE_URL}base`,
): Promise<BaseCarregada> {
  // em paralelo: sao oito arquivos independentes, e serializar multiplicaria a
  // latencia da primeira carga por oito
  const fatias = await Promise.all(NUCLEO.map((k) => fatia(k, raiz)));
  const registros = fatias.flat();
  return {
    base: new Base(registros),
    registros: registros.length,
    kinds: [...NUCLEO],
    bytes: fatias.reduce((n, f) => n + JSON.stringify(f).length, 0),
  };
}

/**
 * A prosa de um registro, buscada quando o jogador abre aquele registro.
 *
 * Ela sozinha e maior que o indice inteiro (17,9 MB contra 1,04 MB), e por
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
