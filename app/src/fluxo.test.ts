/**
 * O criterio de pronto da fatia 1: montar um personagem do zero ate o nivel 4,
 * pelo MESMO caminho que a tela usa.
 *
 * Este teste nao renderiza React -- ele exercita `doc.ts` (as funcoes que os
 * botoes chamam) mais o motor. Se ele passa, o fluxo da tela funciona; o que
 * sobra e layout.
 *
 * Por que isso importa mais que um teste de componente: o defeito caro num
 * construtor nao e o botao no lugar errado, e o numero errado depois de seis
 * escolhas encadeadas.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { Base } from "./motor/base";
import { Personagem } from "./motor/personagem";
import type { Documento, Registro } from "./motor/tipos";
import * as doc from "./doc";

const RAIZ = join(__dirname, "..", "..");
const PAYLOAD = join(RAIZ, "pipeline", "base", "app", "por-kind");

const NUCLEO = [
  "class", "class-feature", "feat", "ancestry",
  "heritage", "background", "archetype", "skill",
];

function carregar(): Base {
  const registros: Registro[] = [];
  for (const kind of NUCLEO) {
    registros.push(...JSON.parse(readFileSync(join(PAYLOAD, `${kind}.json`), "utf-8")));
  }
  return new Base(registros);
}

const base = carregar();
const derivar = (d: Documento) => new Personagem(structuredClone(d), base);

describe("o payload que o app carrega", () => {
  it("tem os oito kinds do nucleo", () => {
    const arquivos = readdirSync(PAYLOAD).map((f) => f.replace(".json", ""));
    for (const k of NUCLEO) expect(arquivos).toContain(k);
  });

  it("basta para montar ficha -- nenhum kind do nucleo vem vazio", () => {
    for (const k of NUCLEO) {
      const n = [...base.por_id.values()].filter((r) => r.kind === k).length;
      expect(n, `kind ${k} vazio`).toBeGreaterThan(0);
    }
  });
});

describe("montar um Guerreiro 4 com Free Archetype, do zero", () => {
  it("percorre o fluxo inteiro e a ficha fecha", () => {
    // 1. documento novo -- o estado inicial do app
    let d = doc.novoDocumento("Bran");
    let p = derivar(d);
    expect(p.nivel).toBe(0);
    expect(p.hp).toBe(0);
    // nivel 0 deriva sem explodir: foi uma regressao real, hoje e teste
    expect(p.visao().slots_abertos.length).toBeGreaterThan(0);

    // 2. criacao
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    d = doc.escolher(d, "heranca", "criacao", "wb:heritage/versatile-human");
    d = doc.escolher(d, "background", "criacao", "wb:background/warrior");
    p = derivar(d);
    expect(p.hp).toBe(8); // so a ancestria, ainda sem classe

    // 3. quatro niveis de Guerreiro -- a houserule: nivel a nivel
    for (let n = 1; n <= 4; n += 1) {
      d = doc.definirClasseDoNivel(d, n, "wb:class/fighter");
    }
    p = derivar(d);
    expect(p.nivel).toBe(4);
    expect(doc.nivelDoPersonagem(d)).toBe(4);

    // 4. boosts -- 9 de direito num nivel 4 (2 ancestria + 2 background +
    //    1 chave + 4 criacao)
    expect(p.boosts_direito).toBe(9);
    d = doc.definirBoosts(d, "criacao", 0, ["str", "dex", "con", "wis"]);
    d = doc.definirBoosts(d, "criacao", 1, ["str", "dex", "con", "cha"]);
    d = doc.definirBoosts(d, "criacao", 2, ["str"]);
    p = derivar(d);
    expect(p.boosts_declarados).toBe(9);
    expect(p.avisos.filter((a) => a.includes("boosts de atributo"))).toEqual([]);

    // 5. os slots que o motor diz existirem -- a tela le exatamente isto
    const v = p.visao();
    expect(v.slots.free_archetype).toEqual([2, 4]); // regra 2, nivel par
    expect(v.slots.class).toContain(1);

    // 6. preencher pelo picker: candidato -> escolha
    const primeiroQueAtende = (slot: string, em: number) => {
      const c = p.candidatos(slot, em).filter((x) => x.atende && !x.ja_pego);
      expect(c.length, `sem candidato para ${slot}@${em}`).toBeGreaterThan(0);
      return c[0].id;
    };
    for (const em of v.slots.class ?? []) {
      d = doc.escolher(d, "class_feat", em, primeiroQueAtende("class_feat", em));
      p = derivar(d);
    }
    for (const em of v.slots.free_archetype ?? []) {
      d = doc.escolher(d, "free_archetype", em,
        primeiroQueAtende("free_archetype", em));
      p = derivar(d);
    }

    // 7. a ficha fecha
    const f = p.visao();
    expect(f.nivel).toBe(4);
    expect(f.hp).toBeGreaterThan(40);
    expect(f.ac.total).toBeGreaterThan(10);
    expect(Object.keys(f.proficiencias).length).toBeGreaterThan(5);
    expect(f.features.length).toBeGreaterThan(0);
    // o trilho gratuito nao comeu o de classe
    expect(p.gastos.get("class_feat")?.length).toBe((v.slots.class ?? []).length);
    expect(p.gastos.get("free_archetype")?.length).toBe(2);
  });

  it("o slot gratuito so oferece feat de arquetipo", () => {
    let d = doc.novoDocumento();
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    for (let n = 1; n <= 4; n += 1) {
      d = doc.definirClasseDoNivel(d, n, "wb:class/fighter");
    }
    const p = derivar(d);
    for (const c of p.candidatos("free_archetype", 2).slice(0, 40)) {
      expect(base.get(c.id).traits ?? []).toContain("archetype");
    }
  });

  it("o que nao atende aparece na lista, marcado -- principio zero", () => {
    let d = doc.novoDocumento();
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    d = doc.definirClasseDoNivel(d, 1, "wb:class/fighter");
    const p = derivar(d);
    const c = p.candidatos("free_archetype", 2);
    const fora = c.filter((x) => !x.atende);
    expect(fora.length, "nada fora do requisito num nivel 1").toBeGreaterThan(0);
    for (const x of fora.slice(0, 10)) expect(x.motivos.length).toBeGreaterThan(0);
  });
});

describe("subclasse pelo picker", () => {
  it("candidatos('subclasse') devolve os ids do eixo", () => {
    let d = doc.novoDocumento();
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    for (let n = 1; n <= 4; n += 1) {
      d = doc.definirClasseDoNivel(d, n, "wb:class/rogue");
    }
    const p = derivar(d);
    const c = p.candidatos("subclasse", 1);
    expect(c.length).toBe(6); // os seis rackets do Ladino
    expect(c.map((x) => x.nome)).toContain("Thief");
  });

  it("o Guerreiro nao pede subclasse nenhuma", () => {
    let d = doc.novoDocumento();
    for (let n = 1; n <= 4; n += 1) {
      d = doc.definirClasseDoNivel(d, n, "wb:class/fighter");
    }
    const p = derivar(d);
    expect(p.slots_de_subclasse).toEqual([]);
  });
});

describe("o documento e a unica fonte de verdade", () => {
  it("remover o ultimo nivel leva junto o que foi escolhido nele", () => {
    let d = doc.novoDocumento();
    for (let n = 1; n <= 4; n += 1) {
      d = doc.definirClasseDoNivel(d, n, "wb:class/fighter");
    }
    d = doc.escolher(d, "class_feat", 4, "wb:feat/dual-handed-assault");
    expect(d.escolhas.some((e) => e.em === 4)).toBe(true);

    d = doc.removerUltimoNivel(d);
    expect(doc.nivelDoPersonagem(d)).toBe(3);
    expect(d.escolhas.some((e) => e.em === 4)).toBe(false);
    // e a ficha nao fica reclamando de escolha em nivel que nao existe mais
    const p = derivar(d);
    expect(p.avisos.filter((a) => a.includes("nivel 4"))).toEqual([]);
  });

  it("exportar e importar preserva a ficha derivada", () => {
    let d = doc.novoDocumento("Vela");
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    d = doc.definirClasseDoNivel(d, 1, "wb:class/rogue");
    const antes = derivar(d).visao();

    const { doc: lido, erro } = doc.importar(JSON.stringify(d));
    expect(erro).toBeUndefined();
    expect(lido).toBeDefined();
    expect(derivar(lido!).visao()).toEqual(antes);
  });

  it("importar lixo devolve erro em vez de explodir", () => {
    expect(doc.importar("nao e json").erro).toBeTruthy();
    expect(doc.importar('{"foo": 1}').erro).toBeTruthy();
  });
});
