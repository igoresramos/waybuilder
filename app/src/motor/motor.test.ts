/**
 * O CONTRATO DO PORTE.
 *
 * `motor/fixtures/*.json` foi gerado pelo motor Python (`motor/motor.py`, 95
 * testes, validado contra os iconics da Paizo) a partir dos mesmos documentos
 * em `motor/exemplos/*.json`. Aqui o TS roda os MESMOS documentos e compara
 * campo a campo: `visao`, depois `extras` (os derivados que não entram na visão
 * mas que uma tradução desatenta erra primeiro), depois `candidatos`.
 *
 * Divergência é falha. Sem tolerância, sem arredondamento -- e o erro aponta
 * QUAL campo divergiu, com os dois valores.
 *
 * Rodar: `cd app && npx vitest run`
 */
import { readFileSync, readdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { Base } from "./base.ts";
import { Personagem } from "./personagem.ts";
import { melhorRank, normSlug } from "./util.ts";
import type { Documento, Registro } from "./tipos.ts";

const AQUI = fileURLToPath(new URL(".", import.meta.url));
const RAIZ = join(AQUI, "..", "..", "..");            // app/src/motor -> projeto
const INDEX = join(RAIZ, "pipeline", "base", "app", "index.json");
const EXEMPLOS = join(RAIZ, "motor", "exemplos");
const FIXTURES = join(RAIZ, "motor", "fixtures");

function lerJson(caminho: string): unknown {
  return JSON.parse(readFileSync(caminho, "utf-8")) as unknown;
}

/**
 * O mesmo `normalizar` de `motor/gerar_fixtures.py`: `Map` e `Set` não
 * sobrevivem à serialização com forma estável, e `undefined` do JS é "chave
 * ausente" (o `None` do Python vira `null`, e a diferença entre os dois é
 * justamente o que se quer detectar).
 */
function normalizar(o: unknown): unknown {
  if (o instanceof Map) {
    const saida: Record<string, unknown> = {};
    for (const [k, v] of o) saida[String(k)] = normalizar(v);
    return saida;
  }
  if (o instanceof Set) return [...o].map(String).sort();
  if (Array.isArray(o)) return o.map(normalizar);
  if (typeof o === "object" && o !== null) {
    const saida: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(o)) {
      if (v === undefined) continue;      // chave ausente no Python
      saida[String(k)] = normalizar(v);
    }
    return saida;
  }
  return o;
}

/** Onde os dois lados divergem, em notação de caminho. `null` = idênticos. */
function primeiraDivergencia(caminho: string, tem: unknown, esperado: unknown):
    { campo: string; tem: unknown; esperado: unknown } | null {
  if (Array.isArray(esperado) || Array.isArray(tem)) {
    if (!Array.isArray(tem) || !Array.isArray(esperado)) {
      return { campo: caminho, tem, esperado };
    }
    const n = Math.min(tem.length, esperado.length);
    for (let i = 0; i < n; i += 1) {
      const d = primeiraDivergencia(`${caminho}[${i}]`, tem[i], esperado[i]);
      if (d !== null) return d;
    }
    if (tem.length !== esperado.length) {
      return { campo: `${caminho}.length`, tem: tem.length, esperado: esperado.length };
    }
    return null;
  }
  const objTem = typeof tem === "object" && tem !== null;
  const objEsp = typeof esperado === "object" && esperado !== null;
  if (objTem || objEsp) {
    if (!objTem || !objEsp) return { campo: caminho, tem, esperado };
    const a = tem as Record<string, unknown>;
    const b = esperado as Record<string, unknown>;
    for (const k of Object.keys(b)) {
      if (!Object.hasOwn(a, k)) {
        return { campo: `${caminho}.${k}`, tem: "<chave ausente no TS>", esperado: b[k] };
      }
      const d = primeiraDivergencia(`${caminho}.${k}`, a[k], b[k]);
      if (d !== null) return d;
    }
    for (const k of Object.keys(a)) {
      if (!Object.hasOwn(b, k)) {
        return { campo: `${caminho}.${k}`, tem: a[k], esperado: "<chave ausente no Python>" };
      }
    }
    return null;
  }
  if (!Object.is(tem, esperado)) return { campo: caminho, tem, esperado };
  return null;
}

function conferir(rotulo: string, tem: unknown, esperado: unknown): void {
  const d = primeiraDivergencia(rotulo, normalizar(tem), normalizar(esperado));
  if (d !== null) {
    throw new Error(
      `divergencia em \`${d.campo}\`\n`
      + `  TS     : ${JSON.stringify(d.tem)}\n`
      + `  Python : ${JSON.stringify(d.esperado)}`);
  }
}

// os mesmos campos que `motor/gerar_fixtures.py` congela em `extras`
const EXTRAS = [
  "hp_detalhe", "origem_proficiencia", "pericias_livres_detalhe",
  "aumentos_detalhe", "boosts_direito", "boosts_declarados",
  "boosts_pendentes", "gastos", "class_feat_nivel_1", "niveis_por_classe",
  "ordem_de_classe", "classe_do_nivel", "entrada_da_classe",
  "pericias_automaticas",
] as const;

const SLOTS_DE_CANDIDATO = ["class_feat", "skill_feat", "general_feat",
                            "ancestry_feat", "free_archetype"] as const;
const NIVEIS_DE_CANDIDATO = [1, 2, 4] as const;

// -- as duas funções usadas em toda parte, com teste próprio ---------------

describe("norm_slug", () => {
  it("achata separador e caixa", () => {
    expect(normSlug("cloistered_cleric")).toBe("cloistered-cleric");
    expect(normSlug("Cloistered Cleric")).toBe("cloistered-cleric");
    expect(normSlug("cloistered-cleric")).toBe("cloistered-cleric");
  });
  it("apara traco das pontas e colapsa repetido", () => {
    expect(normSlug("  Hunt   Prey!  ")).toBe("hunt-prey");
    expect(normSlug("--a--b--")).toBe("a-b");
  });
  it("valor falso vira string vazia, como `str(s or \"\")`", () => {
    expect(normSlug(null)).toBe("");
    expect(normSlug(undefined)).toBe("");
    expect(normSlug("")).toBe("");
    expect(normSlug(0)).toBe("");
  });
});

describe("melhor_rank", () => {
  it("regra 4: vale o melhor entre os dois", () => {
    expect(melhorRank("trained", "expert")).toBe("expert");
    expect(melhorRank("expert", "trained")).toBe("expert");
    expect(melhorRank("legendary", "master")).toBe("legendary");
  });
  it("nulo e desconhecido valem untrained (indice 0), nunca estouram", () => {
    expect(melhorRank(null, "master")).toBe("master");
    expect(melhorRank(null, null)).toBe("untrained");
    expect(melhorRank("nao-existe", "trained")).toBe("trained");
    expect(melhorRank("nao-existe", "nao-existe")).toBe("untrained");
  });
});

describe("divisao inteira do modificador", () => {
  it("trunca para -infinito, como o `//` do Python", () => {
    // caso real: defeito de ancestria derruba o atributo abaixo de 10.
    // `Math.trunc(-1/2)` daria 0 e o HP sairia `nivel` pontos alto.
    const mod = (v: number): number => Math.floor((v - 10) / 2);
    expect(mod(8)).toBe(-1);
    expect(mod(9)).toBe(-1);
    expect(mod(7)).toBe(-2);
    expect(mod(10)).toBe(0);
    expect(mod(11)).toBe(0);
    expect(mod(18)).toBe(4);
  });
});

// -- o gabarito ------------------------------------------------------------

const base = new Base(lerJson(INDEX) as Registro[]);
const fichas = readdirSync(EXEMPLOS)
  .filter((f) => f.endsWith(".json"))
  .map((f) => basename(f, ".json"))
  .sort();

describe("porte contra o gabarito do Python", () => {
  it("acha as 25 fichas de exemplo", () => {
    expect(fichas.length).toBe(25);
  });

  for (const ficha of fichas) {
    describe(ficha, () => {
      const doc = lerJson(join(EXEMPLOS, `${ficha}.json`)) as Documento;
      const fixture = lerJson(join(FIXTURES, `${ficha}.json`)) as Record<string, unknown>;
      const p = new Personagem(doc, base);

      it("visao", () => {
        const esperado = fixture["visao"] as Record<string, unknown>;
        const tem = p.visao() as unknown as Record<string, unknown>;
        // campo a campo: o erro aponta o campo, não um diff de 7 KB
        for (const campo of Object.keys(esperado).sort()) {
          conferir(`visao.${campo}`, tem[campo], esperado[campo]);
        }
        conferir("visao", tem, esperado);
      });

      it("extras", () => {
        const esperado = fixture["extras"] as Record<string, unknown>;
        const estado = p as unknown as Record<string, unknown>;
        // nenhum campo pode sumir em silencio: o gabarito tem os 14
        expect(Object.keys(esperado).sort()).toEqual([...EXTRAS].sort());
        for (const campo of EXTRAS) {
          conferir(`extras.${campo}`, estado[campo], esperado[campo]);
        }
      });

      it("candidatos", () => {
        const esperado = fixture["candidatos"] as Record<string, string[]>;
        for (const slot of SLOTS_DE_CANDIDATO) {
          for (const em of NIVEIS_DE_CANDIDATO) {
            const chave = `${slot}@${em}`;
            const ids = p.candidatos(slot, em).slice(0, 40).map((c) => c.id);
            conferir(`candidatos.${chave}`, ids, esperado[chave]);
          }
        }
      });
    });
  }
});
