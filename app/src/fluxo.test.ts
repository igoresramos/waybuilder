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
import { limparMarcacao } from "./marcacao";
import { aplicarFunil, FUNIL_VAZIO } from "./componentes/Funil";
import { nomeDeTrait, formatarSlugDeTrait } from "./nomeDeTrait";

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
const ORFAS_CONHECIDAS: string[] = [
  // Vazia desde 2026-07-28. Eram 23 -- as 6 causas do Campeao, os 8 patronos
  // da Bruxa e 8 `-legacy` -- e nenhuma era conteudo faltando: a fusao do
  // remaster aposentou os ids e nao reescreveu quem os citava. O vinculo estava
  // no proprio dado, em `historico[].id_legado`.
  //
  // Mantida como lista, e nao como `toEqual([])` solto, porque a intencao e o
  // ratchet: se uma orfa nova aparecer, o teste falha e diz QUAL.
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

/**
 * A marcacao do Pf2eTools sobra em 53% dos requisitos e deixa o texto ilegivel
 * justo onde ele precisa ser lido de relance.
 */
describe("marcacao das fontes some do texto", () => {
  it("troca o link pelo rotulo", () => {
    expect(limparMarcacao("trained in {@skill Athletics|PC1}"))
      .toBe("trained in Athletics");
    expect(limparMarcacao("{@feat Everstand Stance|LOCG}"))
      .toBe("Everstand Stance");
    expect(limparMarcacao("{@feat Aggressive Block|PC1} or {@feat Brutish Shove|PC1}"))
      .toBe("Aggressive Block or Brutish Shove");
    expect(limparMarcacao("devotion spell ({@spell lay on hands})"))
      .toBe("devotion spell (lay on hands)");
  });

  it("respeita o apelido quando a fonte da um", () => {
    expect(limparMarcacao("{@feat Sudden Charge|PC1|carga subita}")).toBe("carga subita");
  });

  it("nao mexe em texto sem marcacao", () => {
    expect(limparMarcacao("Charisma 14")).toBe("Charisma 14");
  });

  it("nenhum requisito da base sobra com marcacao", () => {
    const sujos: string[] = [];
    for (const r of base.por_id.values()) {
      const t = r.requires_texto;
      if (typeof t === "string" && limparMarcacao(t).includes("{@")) sujos.push(r.id);
    }
    expect(sujos).toEqual([]);
  });
});

/**
 * A ficha mostra as 17 pericias do jogo, nao as 33 linhas do kind `skill`.
 *
 * As 16 de reino do Kingmaker vivem no mesmo kind, marcadas com `lore: true` e
 * sem `attribute`. Passavam pelo filtro da tela e apareciam somando +INT (o
 * fallback) ao lado das de verdade, numa ficha que nao joga regra de reino.
 */
describe("pericias da ficha", () => {
  const REINO = [
    "Agriculture", "Arts", "Boating", "Defense", "Engineering", "Exploration",
    "Folklore", "Industry", "Intrigue", "Magic", "Politics", "Scholarship",
    "Statecraft", "Trade", "Warfare", "Wilderness",
  ];

  const daFicha = () => [...base.por_id.values()]
    .filter((r) => r.kind === "skill" && r.lore !== true && r.id !== "wb:skill/lore")
    .map((r) => r.name);

  // 16 fixas. A 17a linha da coluna do Pathbuilder e a `Lore: Alcohol` que o
  // background concede -- ela vem de `proficiencias`, nao do catalogo.
  it("sao as 16 pericias do Player Core", () => {
    expect(daFicha()).toHaveLength(16);
    expect(daFicha()).toContain("Acrobatics");
    expect(daFicha()).toContain("Thievery");
  });

  it("nenhuma pericia de reino entra", () => {
    for (const r of REINO) expect(daFicha()).not.toContain(r);
  });

  it("as 16 tem atributo -- nenhuma cai no fallback", () => {
    for (const r of base.por_id.values()) {
      if (r.kind !== "skill" || r.lore === true) continue;
      expect(r.attribute, `${r.name} sem attribute`).toBeTruthy();
    }
  });
});

/**
 * O funil do picker. Nada ligado por padrao -- esconder e escolha do jogador.
 */
describe("filtro fino do picker", () => {
  const guerreiro = () => {
    let d = doc.novoDocumento("Teste");
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    d = doc.definirClasseDoNivel(d, 1, "wb:class/fighter");
    return derivar(d).candidatos("class_feat", 1);
  };

  it("vazio nao mexe na lista", () => {
    const todos = guerreiro();
    expect(aplicarFunil(todos, FUNIL_VAZIO, base)).toHaveLength(todos.length);
  });

  it("`so o que posso pegar` tira os marcados", () => {
    const todos = guerreiro();
    const so = aplicarFunil(todos, { ...FUNIL_VAZIO, soAtende: true }, base);
    expect(so.length).toBeLessThan(todos.length);
    expect(so.every((c) => c.atende)).toBe(true);
  });

  it("nivel maximo corta pelo nivel do feat", () => {
    const ate2 = aplicarFunil(guerreiro(), { ...FUNIL_VAZIO, nivelMax: 2 }, base);
    expect(ate2.length).toBeGreaterThan(0);
    expect(ate2.every((c) => (c.level ?? 0) <= 2)).toBe(true);
  });

  it("trait e E, nao OU", () => {
    const todos = guerreiro();
    const press = aplicarFunil(todos, { ...FUNIL_VAZIO, traits: ["press"] }, base);
    const dois = aplicarFunil(todos, { ...FUNIL_VAZIO, traits: ["press", "flourish"] }, base);
    expect(dois.length).toBeLessThanOrEqual(press.length);
    for (const c of dois) {
      const t = (base.opcional(c.id)?.traits ?? []) as string[];
      expect(t).toContain("press");
      expect(t).toContain("flourish");
    }
  });
});

describe("Lore na ficha", () => {
  it("o Lore generico nao e pericia do personagem", () => {
    const daFicha = [...base.por_id.values()]
      .filter((r) => r.kind === "skill" && r.lore !== true && r.id !== "wb:skill/lore");
    expect(daFicha).toHaveLength(16);
    expect(daFicha.map((r) => r.id)).not.toContain("wb:skill/lore");
  });

  it("o background concede a Lore com nome limpo, sem duplicar o sufixo", () => {
    let d = doc.novoDocumento("Teste");
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    d = doc.escolher(d, "background", "criacao", "wb:background/barkeep");
    const chaves = Object.keys(derivar(d).visao().proficiencias)
      .filter((k) => k.startsWith("lore:"));
    expect(chaves.length).toBeGreaterThan(0);
    // e a formatacao que a ficha usa
    const nome = (c: string) =>
      `Lore: ${c.slice(5).replace(/\s*\blore\b\s*$/i, "").trim()
        .replace(/\b\w/g, (x) => x.toUpperCase())}`;
    for (const c of chaves) {
      expect(nome(c)).not.toMatch(/Lore$/);
      expect(nome(c)).toMatch(/^Lore: \S/);
    }
  });
});

/**
 * RAW: feat de arquetipo pode ser gasto num slot de feat de CLASSE -- e assim
 * que se entra num arquetipo no PF2e oficial.
 *
 * Nenhuma das 226 dedicacoes carrega trait de classe, entao enquanto o slot
 * exigiu a trait da classe elas eram inalcancaveis por ali, e a unica porta
 * para dedicacao era o slot de Free Archetype. Num projeto cuja regra da casa
 * SUBSTITUI a dedicacao, o caminho RAW precisa existir para ser comparado.
 */
describe("dedicacao cabe no slot de feat de classe", () => {
  const guerreiro = (nivel = 2) => {
    let d = doc.novoDocumento("Teste");
    d = doc.escolher(d, "ancestralidade", "criacao", "wb:ancestry/human");
    for (let n = 1; n <= nivel; n++) d = doc.definirClasseDoNivel(d, n, "wb:class/fighter");
    return derivar(d);
  };

  it("a dedicacao aparece entre os candidatos", () => {
    const ids = guerreiro().candidatos("class_feat", 2).map((c) => c.id);
    expect(ids).toContain("wb:feat/rogue-dedication");
  });

  it("o feat da propria classe continua vindo", () => {
    const nomes = guerreiro().candidatos("class_feat", 1).map((c) => c.nome);
    expect(nomes).toContain("Sudden Charge");
  });

  it("regra 23: a dedicacao da PROPRIA classe aparece marcada, nao some", () => {
    const c = guerreiro().candidatos("class_feat", 2)
      .find((x) => x.id === "wb:feat/fighter-dedication");
    expect(c, "Fighter Dedication sumiu da lista").toBeTruthy();
    expect(c!.atende).toBe(false);
    expect(c!.motivos.join(" ")).toBeTruthy();
  });
});

/**
 * Nome de trait na tela: caixa correta, sempre.
 *
 * 62 slugs nao tem registro proprio -- sao os parametrizados de arma
 * (`two-hand-d8`, `versatile-p`, `deadly-d8`, `thrown-20`) -- e apareciam crus
 * e em minusculo no meio dos outros.
 */
describe("nome de trait", () => {
  it("usa o registro quando existe", () => {
    expect(nomeDeTrait(base, "dwarf")).toBe("Dwarf");
    expect(nomeDeTrait(base, "agile")).toBe("Agile");
  });

  it("formata os parametrizados de arma", () => {
    expect(formatarSlugDeTrait("two-hand-d8")).toBe("Two-Hand d8");
    expect(formatarSlugDeTrait("versatile-p")).toBe("Versatile P");
    expect(formatarSlugDeTrait("deadly-d10")).toBe("Deadly d10");
    expect(formatarSlugDeTrait("thrown-20")).toBe("Thrown 20 ft.");
    expect(formatarSlugDeTrait("jousting-d6")).toBe("Jousting d6");
  });

  it("nenhum trait da base inteira sai em minuscula", () => {
    const feios = new Set<string>();
    for (const r of base.por_id.values()) {
      for (const t of ((r.traits ?? []) as string[])) {
        const nome = nomeDeTrait(base, t);
        if (/^[a-z]/.test(nome)) feios.add(`${t} -> ${nome}`);
      }
    }
    expect([...feios]).toEqual([]);
  });
});

/**
 * Os consertos de dado aplicados em 2026-07-28, travados contra regressao.
 * Cada um veio de um achado da auditoria de arquetipos.
 */
describe("consertos da auditoria de arquetipos", () => {
  it("feat de arquetipo exige a dedicacao daquele arquetipo (regra do livro)", () => {
    const absorb = base.opcional("wb:feat/absorb-spell");
    expect(absorb, "feat sumiu da base").toBeTruthy();
    expect(JSON.stringify(absorb!.requires))
      .toContain("wb:feat/spellmaster-dedication");
  });

  it("nenhum requires cita id que nao existe na base", () => {
    const ids = new Set([...base.por_id.values()].map((r) => r.id));
    const orfas = new Set<string>();
    for (const r of base.por_id.values()) {
      const texto = JSON.stringify(r.requires ?? {});
      for (const m of texto.match(/wb:[a-z-]+\/[a-z0-9-]+/g) ?? []) {
        if (!ids.has(m)) orfas.add(m);
      }
    }
    // as 2 que sobram nao tem alias na base -- sao ruido de parse de prosa
    expect([...orfas].sort()).toEqual([
      "wb:heritage/versatile", "wb:heritage/you-have-a-versatile",
    ]);
  });

  it("Fighter Dedication treina simples E marciais, como o texto diz", () => {
    const fd = base.opcional("wb:feat/fighter-dedication");
    const prof = (fd!.grants as Array<Record<string, unknown>>)
      .find((g) => "proficiency" in g)?.proficiency as Record<string, string>;
    expect(prof.simple).toBe("trained");
    expect(prof.martial).toBe("trained");
  });

  it("`grants_completos` nao mente quando a fonte nao declarou mecanica", () => {
    const mentindo = [...base.por_id.values()].filter(
      (r) => r.mechanized === false && r.grants_completos === true,
    );
    expect(mentindo.map((r) => r.id)).toEqual([]);
  });
});
