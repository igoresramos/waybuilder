/**
 * As travas da issue #1 -- a ficha orfa.
 *
 * O defeito, medido no codigo de 2026-08-01: `App.tsx:54` cunhava
 * `useState(() => doc.novoId())` a cada mount, `App.tsx:63-65` gravava sempre e
 * nunca lia de volta, e `doc.ts:229`/`doc.ts:254` (`listar`/`apagar`) nao tinham
 * um unico chamador no app. Resultado: UMA ENTRADA NOVA POR RECARGA na chave
 * `waybuilder:personagens`, crescimento ate a cota do navegador, e a ficha do
 * jogador nunca voltava.
 *
 * Este arquivo e a rede que impede o defeito de voltar. Cada `it` nomeia o que o
 * derrubaria; os tres primeiros blocos sao as travas obrigatorias (round-trip,
 * N recargas != N entradas, pin divergente avisa e nao recusa).
 *
 * Por que sem browser: o `localStorage` do navegador e um contrato sincrono
 * simples, e so com um duble em memoria da para ESGOTAR A COTA e CORROMPER A
 * CHAVE de proposito -- os dois caminhos onde a perda de ficha realmente mora.
 *
 * Spec: `specs/2026-08-01-persistencia-e-identidade-de-build.md`.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { beforeEach, describe, expect, it } from "vitest";
import type { Documento, PinDaBase } from "./motor/tipos";
import * as doc from "./doc";
import { pinDoManifesto } from "./carregarBase";

const CHAVE = "waybuilder:personagens";
const CHAVE_ULTIMA = "waybuilder:ultima";

/**
 * `localStorage` em memoria com cota ajustavel.
 *
 * A cota conta caracteres de chave + valor -- nao e a aritmetica exata de
 * nenhum navegador, e nao precisa ser: o que os testes exercitam e o CAMINHO do
 * `QuotaExceededError`, nao o numero em que ele acontece.
 */
class Memoria {
  private m = new Map<string, string>();
  limite = Number.POSITIVE_INFINITY;

  get length(): number { return this.m.size; }
  key(i: number): string | null { return [...this.m.keys()][i] ?? null; }
  getItem(k: string): string | null { return this.m.has(k) ? this.m.get(k)! : null; }
  removeItem(k: string): void { this.m.delete(k); }
  clear(): void { this.m.clear(); }
  chaves(): string[] { return [...this.m.keys()]; }

  setItem(k: string, v: string): void {
    let total = k.length + String(v).length;
    for (const [ck, cv] of this.m) if (ck !== k) total += ck.length + cv.length;
    if (total > this.limite) {
      const e = new Error("QuotaExceededError: a cota do armazenamento estourou");
      e.name = "QuotaExceededError";
      throw e;
    }
    this.m.set(k, String(v));
  }
}

let memoria: Memoria;
beforeEach(() => {
  memoria = new Memoria();
  Object.defineProperty(globalThis, "localStorage", {
    value: memoria, configurable: true, writable: true,
  });
});

const lerDisco = (): unknown[] => JSON.parse(memoria.getItem(CHAVE) ?? "[]");

/** Uma escolha qualquer -- o teste nao deriva ficha, so persiste documento. */
const comEscolha = (d: Documento, id: string) =>
  doc.escolher(d, "ancestralidade", "criacao", id);

/** A forma EXATA em que as fichas de hoje estao em disco (`doc.ts:242-252`). */
function entradaLegada(id: string, nome: string, escolhas: unknown[] = []) {
  return {
    id,
    nome,
    atualizado: `2026-07-${String(10 + (id.length % 10)).padStart(2, "0")}T12:00:00.000Z`,
    doc: {
      esquema: "waybuilder/personagem@1",
      identidade: { nome, jogador: "" },
      escolhas,
      atores: [],
      inventario: [],
      manual: { hp_bonus: 0 },
    },
  };
}

// -- TRAVA 1: round-trip -----------------------------------------------------

describe("issue #1 -- salvar, recarregar, mesma ficha", () => {
  it("F5 volta na MESMA ficha, com o mesmo id e as mesmas escolhas", () => {
    // sessao 1: o app abre, o jogador escolhe, o app grava
    const s1 = doc.abrir("");
    expect(s1.nova).toBe(true);
    const editado = comEscolha(s1.doc, "wb:ancestry/dwarf");
    expect(doc.salvar(editado).ok).toBe(true);

    // sessao 2: outro mount do App -- era aqui que o id novo nascia
    const s2 = doc.abrir("");
    expect(s2.nova).toBe(false);
    expect(s2.doc.id).toBe(editado.id);
    expect(s2.doc.escolhas).toEqual(editado.escolhas);
    expect(s2.doc.identidade?.nome).toBe(editado.identidade?.nome);
  });

  it("o ponteiro `waybuilder:ultima` decide, e nao o maior `atualizado`", () => {
    const a = comEscolha(doc.novoDocumento("A"), "wb:ancestry/elf");
    doc.salvar(a);
    const b = comEscolha(doc.novoDocumento("B"), "wb:ancestry/gnome");
    doc.salvar(b); // B e o mais recente
    doc.marcarAberta(a.id!);
    expect(doc.abrir("").doc.id).toBe(a.id);
  });

  it("`#/p/<id>` abre aquela ficha, e nao a ultima global", () => {
    const a = comEscolha(doc.novoDocumento("A"), "wb:ancestry/elf");
    doc.salvar(a);
    const b = comEscolha(doc.novoDocumento("B"), "wb:ancestry/gnome");
    doc.salvar(b);
    doc.marcarAberta(b.id!);
    expect(doc.abrir(`#/p/${a.id}`).doc.id).toBe(a.id);
  });

  it("sem nada gravado, abre ficha nova e NAO grava", () => {
    const a = doc.abrir("");
    expect(a.nova).toBe(true);
    expect(doc.temConteudo(a.doc)).toBe(false);
    expect(memoria.getItem(CHAVE)).toBeNull();
  });
});

// -- TRAVA 2: N recargas != N entradas ---------------------------------------

describe("issue #1 -- recarregar N vezes nao cria N entradas", () => {
  it("50 ciclos de abrir + editar + gravar deixam UMA entrada", () => {
    let atual = comEscolha(doc.abrir("").doc, "wb:ancestry/human");
    expect(doc.salvar(atual).ok).toBe(true);
    const idOriginal = atual.id;

    for (let i = 0; i < 50; i += 1) {
      const s = doc.abrir(""); // = recarregar a pagina
      atual = doc.escolher(s.doc, "background", "criacao", `wb:background/b${i}`);
      expect(doc.salvar(atual).ok).toBe(true);
    }

    // hoje o mesmo roteiro deixava 50 entradas, uma por recarga
    expect(lerDisco()).toHaveLength(1);
    expect(doc.listar()).toHaveLength(1);
    expect(atual.id).toBe(idOriginal);
    expect(doc.abrir("").doc.id).toBe(idOriginal);
  });

  it("visita ociosa nao deixa entrada nenhuma", () => {
    for (let i = 0; i < 5; i += 1) {
      const s = doc.abrir("");
      expect(doc.temConteudo(s.doc)).toBe(false);
    }
    expect(memoria.getItem(CHAVE)).toBeNull();
  });

  it("existe caminho para a SEGUNDA ficha (nova ficha), sem tocar na primeira", () => {
    const a = comEscolha(doc.abrir("").doc, "wb:ancestry/human");
    doc.salvar(a);

    // o que o botao `nova ficha` faz
    doc.esquecerUltima();
    const b = comEscolha(doc.novoDocumento(), "wb:ancestry/orc");
    expect(b.id).not.toBe(a.id);
    doc.salvar(b);

    const lista = doc.listar();
    expect(lista).toHaveLength(2);
    expect(lista.find((s) => s.id === a.id)?.doc.escolhas)
      .toEqual([{ em: "criacao", slot: "ancestralidade", pega: "wb:ancestry/human" }]);
  });

  it("apagar tira UMA e deixa as outras", () => {
    const a = comEscolha(doc.novoDocumento("A"), "wb:ancestry/elf");
    doc.salvar(a);
    const b = comEscolha(doc.novoDocumento("B"), "wb:ancestry/gnome");
    doc.salvar(b);
    doc.marcarAberta(a.id!);

    const r = doc.apagar(a.id!);
    expect(r.ok).toBe(true);
    expect(r.lista.map((s) => s.id)).toEqual([b.id]);
    // o ponteiro nao pode continuar apontando para o que nao existe mais
    expect(memoria.getItem(CHAVE_ULTIMA)).toBeNull();
  });
});

// -- TRAVA 3: pin divergente avisa, nunca recusa ------------------------------

describe("issue #1 / achados 6-7-17 -- identidade de build", () => {
  const ATUAL: PinDaBase = {
    pin: "9f3c1a70b2d4e5f6", origem: "manifesto", registros: 20083, kinds: 58,
  };

  it("ficha com pin divergente CARREGA INTEIRA e com aviso", () => {
    let d: Documento = { ...doc.novoDocumento("Tuco"), base: { pin: "0000000000000000", origem: "manifesto", registros: 20000, nascida_em_pin: "0000000000000000" } };
    for (let i = 0; i < 13; i += 1) {
      d = doc.escolher(d, `slot${i}`, "criacao", `wb:feat/f${i}`);
    }
    expect(doc.salvar(d).ok).toBe(true);

    const aberta = doc.abrir("");
    // 1. abre inteira -- nada de tela de erro, nada de `escolhas` vazio
    expect(aberta.doc.escolhas).toHaveLength(13);
    expect(aberta.doc.id).toBe(d.id);
    // 2. e o aviso existe
    const aviso = doc.avisoDePin(aberta.doc, ATUAL);
    expect(aviso).toBeTruthy();
    expect(aviso).toContain("00000000");
    expect(aviso).toContain("9f3c1a70");
  });

  it("id que a base atual nao resolve continua no documento apos gravar", () => {
    const d = doc.escolher(doc.novoDocumento(), "class_feat", 1,
                           "wb:feat/inexistente-nesta-base");
    doc.salvar(doc.carimbarBase(d, ATUAL));
    const voltou = doc.abrir("").doc;
    expect(voltou.escolhas[0].pega).toBe("wb:feat/inexistente-nesta-base");
  });

  it("o carimbo atualiza `pin` e NUNCA mexe em `nascida_em_pin`", () => {
    const nasceu = doc.carimbarBase(doc.novoDocumento(), ATUAL);
    expect(nasceu.base?.nascida_em_pin).toBe(ATUAL.pin);

    const outra: PinDaBase = { ...ATUAL, pin: "e21b8c44aaaaaaaa", registros: 20089 };
    const depois = doc.carimbarBase(nasceu, outra);
    expect(depois.base?.pin).toBe("e21b8c44aaaaaaaa");
    expect(depois.base?.registros).toBe(20089);
    expect(depois.base?.nascida_em_pin).toBe(ATUAL.pin);
  });

  it("ficha migrada NUNCA ganha `nascida_em_pin`", () => {
    memoria.setItem(CHAVE, JSON.stringify([entradaLegada("pvelha", "Velha")]));
    const migrada = doc.listar()[0].doc;
    expect(migrada.base).toEqual({
      pin: null, origem: "desconhecido", nascida_em_pin: null,
    });
    const carimbada = doc.carimbarBase(migrada, ATUAL);
    expect(carimbada.base?.pin).toBe(ATUAL.pin);
    // presente-e-nulo: ela nasceu sob base que ninguem registrou, e carimbar a
    // base de HOJE como berco seria inventar
    expect(carimbada.base?.nascida_em_pin).toBeNull();
    // e sem os dois lados nao ha divergencia a afirmar
    expect(doc.avisoDePin(migrada, ATUAL)).toBeNull();
  });

  it("pin nulo (sem `crypto.subtle`) nao apaga o pin que a ficha ja tinha", () => {
    const d = doc.carimbarBase(doc.novoDocumento(), ATUAL);
    const semPin: PinDaBase = { pin: null, origem: "indisponivel" };
    expect(doc.carimbarBase(d, semPin).base?.pin).toBe(ATUAL.pin);
    expect(doc.avisoDePin(d, semPin)).toBeNull();
  });
});

describe("o pin derivado do manifesto", () => {
  const MANIFESTO = JSON.parse(readFileSync(
    join(__dirname, "..", "public", "base", "_manifesto.json"), "utf-8"));

  it("e estavel entre duas derivacoes do mesmo manifesto", async () => {
    const a = await pinDoManifesto(MANIFESTO);
    const b = await pinDoManifesto(MANIFESTO);
    expect(a.pin).toBe(b.pin);
    expect(a.pin).toMatch(/^[0-9a-f]{16}$/);
    expect(a.origem).toBe("manifesto");
    expect(a.registros).toBe(20083);
    expect(a.kinds).toBe(58);
  });

  it("MUDA quando o conteudo da base muda", async () => {
    const antes = await pinDoManifesto(MANIFESTO);
    const mexido = structuredClone(MANIFESTO);
    mexido.por_kind.feat.gzip_bytes += 1;
    expect((await pinDoManifesto(mexido)).pin).not.toBe(antes.pin);

    const maisUm = structuredClone(MANIFESTO);
    maisUm.registros += 1;
    expect((await pinDoManifesto(maisUm)).pin).not.toBe(antes.pin);
  });

  it("NAO muda so porque as chaves vieram em outra ordem", async () => {
    const antes = await pinDoManifesto(MANIFESTO);
    const invertido = Object.fromEntries(Object.entries(MANIFESTO).reverse());
    expect((await pinDoManifesto(invertido)).pin).toBe(antes.pin);
  });

  it("`hash` proprio do pipeline GANHA do derivado", async () => {
    const r = await pinDoManifesto({ ...MANIFESTO, hash: "abc123" });
    expect(r).toMatchObject({ pin: "abc123", origem: "pipeline" });
  });

  it("sem `crypto.subtle` devolve pin nulo em vez de estourar", async () => {
    const guardado = Object.getOwnPropertyDescriptor(globalThis, "crypto");
    Object.defineProperty(globalThis, "crypto", { value: {}, configurable: true });
    try {
      const r = await pinDoManifesto(MANIFESTO);
      expect(r.pin).toBeNull();
      expect(r.origem).toBe("indisponivel");
    } finally {
      if (guardado) Object.defineProperty(globalThis, "crypto", guardado);
    }
  });
});

// -- migracao e esquema ------------------------------------------------------

describe("as fichas que ja estao salvas hoje", () => {
  it("as 7 entradas legadas continuam listadas, com `doc.id === entrada.id`", () => {
    const semeadas = Array.from({ length: 7 }, (_, i) =>
      entradaLegada(`pold${i}`, `Ficha ${i}`,
                    [{ em: "criacao", slot: "ancestralidade", pega: `wb:ancestry/a${i}` }]));
    memoria.setItem(CHAVE, JSON.stringify(semeadas));

    // medido EM MEMORIA: a migracao e lazy por projeto, e em disco elas seguem
    // `@1` ate a proxima gravacao daquela ficha
    const lista = doc.listar();
    expect(lista).toHaveLength(7);
    lista.forEach((s, i) => {
      expect(s.doc.id).toBe(s.id);
      expect(s.id).toBe(`pold${i}`);
      expect(s.doc.esquema).toBe("waybuilder/personagem@2");
      expect(s.doc.escolhas).toEqual(semeadas[i].doc.escolhas);
    });

    // e gravar UMA nao mexe nas outras seis
    const uma = doc.carimbarBase(lista[3].doc,
      { pin: "9f3c1a70b2d4e5f6", origem: "manifesto", registros: 20083 });
    expect(doc.salvar(uma).ok).toBe(true);
    const disco = lerDisco() as Array<{ id: string; doc: Documento }>;
    expect(disco).toHaveLength(7);
    const gravada = disco.find((e) => e.id === "pold3")!;
    expect(gravada.doc.id).toBe("pold3");
    expect(gravada.doc.esquema).toBe("waybuilder/personagem@2");
    for (const e of disco) {
      if (e.id === "pold3") continue;
      expect(e.doc.esquema).toBe("waybuilder/personagem@1"); // intacta, nao reescrita
    }
  });

  it("entrada malformada e PRESERVADA e pulada -- nao derruba nem some", () => {
    memoria.setItem(CHAVE, JSON.stringify([
      entradaLegada("pa", "A"),
      { id: "ppodre", nome: "podre", atualizado: "2026-07-01T00:00:00.000Z", doc: null },
      entradaLegada("pb", "B"),
      "isto nem e um objeto",
    ]));
    const lista = doc.listar();
    expect(lista.map((s) => s.id)).toEqual(["pa", "pb"]);

    doc.salvar(comEscolha(lista[0].doc, "wb:ancestry/elf"));
    const disco = lerDisco();
    expect(disco).toHaveLength(4);
    expect(disco).toContainEqual("isto nem e um objeto");
    expect(disco.some((e) => (e as { id?: string })?.id === "ppodre")).toBe(true);
  });

  it("`doc.id` divergente de `entrada.id`: o DOCUMENTO ganha", () => {
    const e = entradaLegada("pindice", "A");
    (e.doc as Documento).id = "pdocumento";
    (e.doc as Documento).esquema = "waybuilder/personagem@2";
    memoria.setItem(CHAVE, JSON.stringify([e]));
    const [s] = doc.listar();
    expect(s.id).toBe("pdocumento");
    expect(s.doc.id).toBe("pdocumento");
  });

  it("colisao de `doc.id` nao funde fichas: quem chegou depois cede", () => {
    const a = entradaLegada("pa", "A");
    const b = entradaLegada("pb", "B");
    (a.doc as Documento).id = "pmesmo";
    (b.doc as Documento).id = "pmesmo";
    memoria.setItem(CHAVE, JSON.stringify([a, b]));
    const lista = doc.listar();
    expect(lista).toHaveLength(2);
    expect(lista[0].id).toBe("pmesmo");
    expect(lista[1].id).toBe("pb");
    // a invariante do espelho vale nas duas
    for (const s of lista) expect(s.doc.id).toBe(s.id);
  });

  it("chave ILEGIVEL e copiada antes de ser substituida", () => {
    memoria.setItem(CHAVE, "{lixo que nao parseia");
    expect(doc.listar()).toEqual([]); // nao lanca

    const d = comEscolha(doc.novoDocumento("Nova"), "wb:ancestry/elf");
    expect(doc.salvar(d).ok).toBe(true);

    const resgate = memoria.chaves().filter((k) => k.startsWith(`${CHAVE}:corrompido-`));
    expect(resgate).toHaveLength(1);
    expect(memoria.getItem(resgate[0])).toBe("{lixo que nao parseia");
    expect(lerDisco()).toHaveLength(1);
  });

  it("se a copia de resgate nao couber, NADA e sobrescrito", () => {
    memoria.setItem(CHAVE, "{lixo que nao parseia");
    memoria.limite = memoria.getItem(CHAVE)!.length + CHAVE.length + 10;
    const r = doc.salvar(comEscolha(doc.novoDocumento("Nova"), "wb:ancestry/elf"));
    expect(r.ok).toBe(false);
    expect(r.erro).toBe("resgate");
    expect(memoria.getItem(CHAVE)).toBe("{lixo que nao parseia");
  });

  it("`migrar()` e idempotente", () => {
    const uma = doc.migrar((entradaLegada("px", "X").doc as Documento), "px").doc;
    const duas = doc.migrar(uma, "px").doc;
    expect(JSON.stringify(duas)).toBe(JSON.stringify(uma));
  });

  it("esquema do FUTURO abre com aviso, e nao e rebaixado", () => {
    const futuro = {
      esquema: "waybuilder/personagem@99",
      id: "pfuturo",
      identidade: { nome: "Do futuro" },
      escolhas: [{ em: "criacao", slot: "ancestralidade", pega: "wb:ancestry/elf" }],
      bugiganga: { que: "este app nao conhece", n: 7 },
    } as unknown as Documento;
    memoria.setItem(CHAVE, JSON.stringify([
      { id: "pfuturo", nome: "Do futuro", atualizado: "2026-08-01T00:00:00.000Z", doc: futuro },
    ]));

    const aberta = doc.abrir("");
    expect(aberta.avisos.join(" ")).toContain("@99");
    expect(aberta.doc.escolhas).toHaveLength(1);

    expect(doc.salvar(aberta.doc).ok).toBe(true);
    const relida = doc.abrir("").doc as Documento & { bugiganga?: unknown };
    expect(relida.esquema).toBe("waybuilder/personagem@99"); // NAO rebaixado
    expect(relida.bugiganga).toEqual({ que: "este app nao conhece", n: 7 });
  });

  it("hash que nomeia ficha inexistente AVISA e nao abre outra", () => {
    const a = comEscolha(doc.novoDocumento("A"), "wb:ancestry/elf");
    doc.salvar(a);
    doc.marcarAberta(a.id!);

    const r = doc.abrir("#/p/pnaoexiste");
    expect(r.avisos.join(" ")).toContain("pnaoexiste");
    expect(r.nova).toBe(true);
    expect(r.doc.id).not.toBe(a.id);
    expect(r.doc.escolhas).toEqual([]);
  });
});

// -- cota --------------------------------------------------------------------

describe("cota estourada nao come ficha", () => {
  it("a lista em disco fica intacta e a edicao continua em memoria", () => {
    const a = comEscolha(doc.novoDocumento("A"), "wb:ancestry/elf");
    expect(doc.salvar(a).ok).toBe(true);
    const antes = memoria.getItem(CHAVE)!;

    memoria.limite = antes.length + CHAVE.length; // nao cabe mais nada
    let grande = comEscolha(doc.novoDocumento("B"), "wb:ancestry/gnome");
    for (let i = 0; i < 20; i += 1) {
      grande = doc.escolher(grande, `slot${i}`, i + 1, `wb:feat/f${i}`);
    }
    const copia = structuredClone(grande);

    const r = doc.salvar(grande);
    expect(r.ok).toBe(false);
    expect(r.erro).toBe("cota");
    // nada perdido: o disco continua identico e a lista devolvida traz a ficha A
    expect(memoria.getItem(CHAVE)).toBe(antes);
    expect(r.lista.map((s) => s.id)).toEqual([a.id]);
    // e a edicao que nao coube continua inteira -- e o que `exportar()` levaria
    expect(grande).toEqual(copia);
    expect(grande.escolhas).toHaveLength(21);
  });
});

// -- export / import ---------------------------------------------------------

describe("export e import levam a identidade junto", () => {
  it("id e base viajam no documento exportado", () => {
    const d = doc.carimbarBase(comEscolha(doc.novoDocumento("Tuco"), "wb:ancestry/elf"),
      { pin: "9f3c1a70b2d4e5f6", origem: "manifesto", registros: 20083, kinds: 58 });
    const texto = JSON.stringify(d, null, 2); // o que `exportar()` serializa
    const { doc: lido } = doc.importar(texto, []);
    expect(lido?.id).toBe(d.id);
    expect(lido?.base?.pin).toBe("9f3c1a70b2d4e5f6");
  });

  it("reimportar o proprio backup entra como COPIA, nunca por cima", () => {
    const d = comEscolha(doc.novoDocumento("Tuco"), "wb:ancestry/elf");
    doc.salvar(d);
    const { doc: lido, aviso } = doc.importar(JSON.stringify(d));
    expect(lido?.id).not.toBe(d.id);
    expect(aviso).toContain("copia");
    expect(doc.listar()).toHaveLength(1); // o import nao gravou nada por cima
  });

  it("documento sem id ganha um; documento `@1` e migrado na entrada", () => {
    const legado = JSON.stringify(entradaLegada("pign", "Legada").doc);
    const { doc: lido } = doc.importar(legado, []);
    expect(lido?.id).toBeTruthy();
    expect(lido?.esquema).toBe("waybuilder/personagem@2");
  });
});

// -- o codigo morto morreu ---------------------------------------------------

describe("issue #1 -- o que o grep tem de dizer agora", () => {
  const fonte = (rel: string) =>
    readFileSync(join(__dirname, rel), "utf-8");

  it("`novoId()` saiu do App.tsx -- o id vem do documento carregado", () => {
    expect(fonte("App.tsx")).not.toContain("novoId");
  });

  it("`listar()` e `apagar()` tem chamador fora do doc.ts", () => {
    // por identificador, e nao por `doc.listar`: um `import { listar }` correto
    // reprovaria num grep de `doc.listar`
    const app = fonte("App.tsx") + fonte("componentes/Fichas.tsx");
    expect(app).toMatch(/\blistar\s*\(/);
    expect(app).toMatch(/\bapagar\s*\(/);
  });

  it("nenhum `apagar()` mora em efeito, migracao ou tratamento de cota", () => {
    // o unico chamador de `doc.apagar` e o handler `apagarFicha`, e o unico
    // caminho ate ele passa por um `confirm()` em Fichas.tsx
    expect(fonte("componentes/Fichas.tsx")).toContain("confirm(");
    const chamadas = [...fonte("App.tsx").matchAll(/doc\.apagar\(/g)];
    expect(chamadas).toHaveLength(1);
  });

  it("a chave do localStorage passa a ser MEDIDA por um teste", () => {
    expect(fonte("persistencia.test.ts")).toContain("waybuilder:personagens");
  });
});
