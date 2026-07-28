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

/**
 * Carrega o payload INTEIRO, do jeito que o app carrega -- lendo o diretorio,
 * nao uma lista fixa. Ate 2026-07-28 aqui havia um array com oito kinds, igual
 * ao do app, e era exatamente por isso que o corte de payload passava por 77
 * testes verdes: o teste tinha o mesmo ponto cego que o codigo.
 */
function carregar(): Base {
  const registros: Registro[] = [];
  for (const arquivo of readdirSync(PAYLOAD)) {
    if (!arquivo.endsWith(".json")) continue;
    registros.push(...JSON.parse(readFileSync(join(PAYLOAD, arquivo), "utf-8")));
  }
  return new Base(registros);
}

const base = carregar();
const derivar = (d: Documento) => new Personagem(structuredClone(d), base);

/** Os kinds sem os quais nao ha ficha nem escolha -- o piso, nao a lista. */
const INDISPENSAVEIS = [
  "class", "class-feature", "feat", "ancestry", "heritage", "background",
  "archetype", "skill", "trait", "weapon", "armor", "shield",
];

describe("o payload que o app carrega", () => {
  it("leva a base inteira, nao uma fatia", () => {
    const arquivos = readdirSync(PAYLOAD).filter((f) => f.endsWith(".json"));
    expect(arquivos.length).toBeGreaterThan(40);
    for (const k of INDISPENSAVEIS) expect(arquivos).toContain(`${k}.json`);
  });

  it("nenhum kind indispensavel vem vazio", () => {
    for (const k of INDISPENSAVEIS) {
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


/**
 * O que o payload enxuto quebrava sem que teste nenhum reclamasse.
 *
 * O motor sempre soube calcular ataque por arma e CA por armadura; faltava o
 * dado no payload e a porta de entrada no documento. Nenhum teste dizia
 * "personagem com espada tem ataque", entao o app saiu amputado com a suite
 * inteira verde. Estes tres testes existem para que isso nao se repita em
 * silencio.
 */
describe("equipamento entra na conta", () => {
  const guerreiro = (): Documento => {
    let d = doc.novoDocumento("Teste");
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/dwarf");
    d = doc.definirClasseDoNivel(d, 1, "wb:class/fighter");
    return d;
  };

  it("arma equipada vira ataque com dano", () => {
    const semArma = derivar(guerreiro()).visao();
    expect(semArma.ataques).toHaveLength(0);

    const comArma = derivar(
      doc.adicionarItem(guerreiro(), "wb:weapon/clan-dagger"),
    ).visao();
    expect(comArma.ataques.length).toBeGreaterThan(0);
    expect(comArma.ataques[0].arma).toContain("Clan Dagger");
    expect(comArma.ataques[0].dano).toBeTruthy();
  });

  it("armadura equipada levanta a CA", () => {
    const pelado = derivar(guerreiro()).visao();
    const vestido = derivar(
      doc.adicionarItem(guerreiro(), "wb:armor/chain-mail"),
    ).visao();
    expect(vestido.ac.total).toBeGreaterThan(pelado.ac.total);
  });

  it("guardar tira da conta sem tirar da ficha", () => {
    let d = doc.adicionarItem(guerreiro(), "wb:weapon/clan-dagger");
    expect(derivar(d).visao().ataques.length).toBeGreaterThan(0);

    d = doc.alternarEquipado(d, "wb:weapon/clan-dagger");
    expect(d.inventario).toHaveLength(1);          // continua na ficha
    expect(derivar(d).visao().ataques).toHaveLength(0);  // fora da conta
  });
});

/**
 * Sub-escolhas que a base referencia e nao tem. NAO e defeito do payload -- o
 * registro nao existe em `index.json`. As `-legacy` sumiram na fusao
 * Remaster e a referencia ficou para tras; as demais nunca foram extraidas, e
 * entre elas estao as SEIS causas do Campeao (paladin, redeemer, liberator,
 * tyrant, desecrator, antipaladin) e os OITO patronos da Bruxa -- ou seja, as
 * duas classes hoje nao tem sub-escolha nenhuma para oferecer.
 */
const ORFAS_CONHECIDAS = [
  "wb:instinct/animal-legacy", "wb:instinct/dragon-legacy",
  "wb:instinct/fury-legacy", "wb:instinct/giant-legacy",
  "wb:instinct/spirit-legacy", "wb:instinct/superstition-legacy",
  "wb:cause/antipaladin", "wb:cause/desecrator", "wb:cause/liberator",
  "wb:cause/paladin", "wb:cause/redeemer", "wb:cause/tyrant",
  "wb:mystery/ash-legacy", "wb:lesson/lesson-of-the-elements-legacy",
  "wb:patron/curse", "wb:patron/fate", "wb:patron/fervor", "wb:patron/night",
  "wb:patron/pacts", "wb:patron/rune", "wb:patron/wild", "wb:patron/winter",
  "wb:arcane-thesis/metamagical-experimentation",
];

describe("o payload leva tudo que a base referencia", () => {
  it("toda opcao de subclasse resolve num registro", () => {
    const orfas: string[] = [];
    for (const r of base.por_id.values()) {
      if (r.kind !== "class") continue;
      for (const bloco of (r.subclasses as Array<Record<string, unknown>>) ?? []) {
        for (const opcao of (bloco.opcoes as string[]) ?? []) {
          if (typeof opcao === "string" && !base.opcional(opcao)) orfas.push(opcao);
        }
      }
    }
    // Com o payload de oito kinds eram 44. Sobraram 23 que sao buraco de DADO,
    // nao de payload: o registro nao existe na base. Travadas aqui uma a uma
    // para que o numero so possa cair -- se subir, e regressao; se descer, e
    // conserto e o teste cobra a atualizacao da lista.
    expect([...orfas].sort()).toEqual([...ORFAS_CONHECIDAS].sort());
  });
});

/**
 * Heranca pertence a uma ancestralidade -- nao existe Anao Elfico.
 *
 * Ate 2026-07-28 a tela montava este slot com a lista CRUA de heritage, e as
 * 334 herancas apareciam para qualquer ancestralidade. O motor sempre soube
 * fazer o gate (`_aceita_no_slot` ja fazia isso para feat de ancestria); o slot
 * e que nao passava por ele.
 */
describe("heranca combina com a ancestralidade", () => {
  const com = (ancestria: string): Documento =>
    doc.escolher(doc.novoDocumento("Teste"), "ancestralidade", "criacao", ancestria);

  const nomes = (d: Documento) =>
    derivar(d).candidatos("heranca").map((c) => c.nome ?? c.id);

  it("nao oferece heranca de outra ancestralidade", () => {
    const doAnao = nomes(com("wb:ancestry/dwarf"));
    const doElfo = nomes(com("wb:ancestry/elf"));

    expect(doAnao.length).toBeGreaterThan(0);
    expect(doElfo.length).toBeGreaterThan(0);
    // heranca especifica de elfo nao pode aparecer para o anao, e vice-versa
    expect(doAnao).not.toContain("Ancient Elf");
    expect(doElfo).not.toContain("Ancient-Blooded Dwarf");
    expect(doAnao).toContain("Ancient-Blooded Dwarf");
  });

  it("oferece as versateis para qualquer ancestralidade", () => {
    // as 25 sem campo `ancestry` sao as versateis do PF2e -- abertas a todos
    for (const a of ["wb:ancestry/dwarf", "wb:ancestry/elf", "wb:ancestry/human"]) {
      expect(nomes(com(a)), a).toContain("Dhampir");
    }
  });

  it("sem ancestralidade escolhida, mostra tudo em vez de lista vazia", () => {
    const todas = nomes(doc.novoDocumento("Teste"));
    expect(todas.length).toBeGreaterThan(300);
  });
});
