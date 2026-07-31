/**
 * O documento de personagem -- a unica fonte de verdade.
 *
 * A tela edita `escolhas[]` e nada mais. HP, proficiencia, slot, pendencia:
 * tudo e derivado pelo motor a cada mudanca, e nada derivado e guardado aqui.
 * E a mesma decisao que o motor Python ja tinha tomado, e a razao de mudanca
 * de regra re-derivar em vez de invalidar ficha salva.
 *
 * Persistencia e `localStorage`: sem backend, sem conta, sem sincronizacao --
 * o app roda offline por decisao, nao por limitacao. Exportar/importar JSON
 * cobre backup e troca de maquina.
 */
import type { Documento, Escolha } from "./motor/tipos";

const CHAVE = "waybuilder:personagens";
const ESQUEMA = "waybuilder/personagem@1";

export interface Salvo {
  id: string;
  nome: string;
  atualizado: string;
  doc: Documento;
}

export function novoDocumento(nome = "Sem nome"): Documento {
  return {
    esquema: ESQUEMA,
    identidade: { nome, jogador: "" },
    escolhas: [],
    atores: [],
    inventario: [],
    manual: {
      nota: "tudo aqui e escrito pelo jogador e nunca sobrescrito pelo motor",
      hp_bonus: 0,
      proficiencias_forcadas: {},
      itens_caseiros: [],
    },
  };
}

// -- edicao ----------------------------------------------------------------

/**
 * Poe uma escolha no slot, substituindo a que estiver no mesmo (slot, nivel).
 *
 * Slots que aceitam varias entradas no MESMO nivel -- `boosts_livres` e
 * `nivel_de_classe` -- nao passam por aqui: para eles a chave (slot, em) nao e
 * unica, e substituir apagaria escolha valida.
 */
export function escolher(
  doc: Documento,
  slot: string,
  em: number | "criacao",
  pega: string | string[],
): Documento {
  const escolhas = doc.escolhas.filter(
    (e) => !(e.slot === slot && e.em === em),
  );
  escolhas.push({ em, slot, pega });
  return { ...doc, escolhas: ordenar(escolhas) };
}

export function limpar(
  doc: Documento,
  slot: string,
  em: number | "criacao",
): Documento {
  return {
    ...doc,
    escolhas: doc.escolhas.filter((e) => !(e.slot === slot && e.em === em)),
  };
}

/**
 * O slot CONCEDIDO por um feat ou heranca -- identidade pela `flag`, nao pelo
 * nivel.
 *
 * `escolher()` substitui por `(slot, em)`, e isso nao serve aqui: dois
 * concessores podem cair no mesmo nivel (`Ancient Elf` e um `basic-arcana`), e
 * pela chave de nivel a segunda escolha apagaria a primeira. A `flag` e o
 * `rollOption` do ChoiceSet da fonte, e e ela que da identidade ao slot.
 * Ver `specs/2026-07-31-slot-concedido-generico.md`.
 */
const CONCEDIDO = "feat_concedido";

export function escolherConcedido(
  doc: Documento,
  em: number | "criacao",
  flag: string,
  pega: string,
): Documento {
  const escolhas = doc.escolhas.filter(
    (e) => !(e.slot === CONCEDIDO && e.flag === flag),
  );
  escolhas.push({ em, slot: CONCEDIDO, flag, pega });
  return { ...doc, escolhas: ordenar(escolhas) };
}

export function limparConcedido(doc: Documento, flag: string): Documento {
  return {
    ...doc,
    escolhas: doc.escolhas.filter((e) => !(e.slot === CONCEDIDO && e.flag === flag)),
  };
}

/** O que ja foi escolhido naquele slot concedido, ou `null`. */
export function concedidoDe(doc: Documento, flag: string): string | null {
  const e = doc.escolhas.find((x) => x.slot === CONCEDIDO && x.flag === flag);
  return typeof e?.pega === "string" ? e.pega : null;
}

/**
 * A houserule: cada nivel de personagem compra um nivel de UMA classe. E o
 * unico lugar do app onde a regra da casa aparece como escolha.
 */
export function definirClasseDoNivel(
  doc: Documento,
  nivel: number,
  classeId: string,
): Documento {
  const atual = doc.escolhas.find(
    (e) => e.slot === "nivel_de_classe" && e.em === nivel,
  );
  const trocou = atual !== undefined && atual.pega !== classeId;

  // trocar a classe deste nivel invalida o que foi escolhido a partir dele --
  // feat de classe e sub-escolha pertencem a UMA classe. E o que o Pathbuilder
  // faz, e sem isso a ficha guarda escolha impossivel.
  const partida = trocou ? limparDependentesDeClasse(doc, nivel) : doc;

  const escolhas = partida.escolhas.filter(
    (e) => !(e.slot === "nivel_de_classe" && e.em === nivel),
  );
  escolhas.push({ em: nivel, slot: "nivel_de_classe", pega: classeId });
  return { ...partida, escolhas: ordenar(escolhas) };
}

/**
 * Remove o nivel do topo. Junto vai tudo que foi escolhido NAQUELE nivel --
 * senao o documento fica com feat de nivel 5 num personagem de nivel 4, que o
 * motor sinaliza como erro com razao.
 */
export function removerUltimoNivel(doc: Documento): Documento {
  const niveis = doc.escolhas
    .filter((e) => e.slot === "nivel_de_classe" && typeof e.em === "number")
    .map((e) => e.em as number);
  if (!niveis.length) return doc;
  const topo = Math.max(...niveis);
  return {
    ...doc,
    escolhas: doc.escolhas.filter((e) => e.em !== topo),
  };
}

export function definirBoosts(
  doc: Documento,
  em: number | "criacao",
  indice: number,
  atributos: string[],
): Documento {
  const outros: Escolha[] = [];
  let vistos = 0;
  for (const e of doc.escolhas) {
    if (e.slot === "boosts_livres" && e.em === em) {
      if (vistos === indice) {
        vistos += 1;
        continue; // esta e a que estamos substituindo
      }
      vistos += 1;
    }
    outros.push(e);
  }
  outros.push({ em, slot: "boosts_livres", pega: atributos });
  return { ...doc, escolhas: ordenar(outros) };
}

/** `criacao` sempre antes de qualquer nivel numerado. */
function ordenar(escolhas: Escolha[]): Escolha[] {
  const chave = (e: Escolha) => (typeof e.em === "number" ? e.em : 0);
  return [...escolhas].sort((a, b) => chave(a) - chave(b));
}

export function nivelDoPersonagem(doc: Documento): number {
  return doc.escolhas.filter((e) => e.slot === "nivel_de_classe").length;
}

// -- persistencia ----------------------------------------------------------

export function listar(): Salvo[] {
  try {
    const cru = localStorage.getItem(CHAVE);
    if (!cru) return [];
    const lista = JSON.parse(cru);
    return Array.isArray(lista) ? lista : [];
  } catch {
    // localStorage corrompido nao pode derrubar o app -- o jogador perde a
    // lista, nao a sessao
    return [];
  }
}

export function salvar(id: string, doc: Documento): Salvo[] {
  const lista = listar().filter((s) => s.id !== id);
  lista.push({
    id,
    nome: doc.identidade?.nome || "Sem nome",
    atualizado: new Date().toISOString(),
    doc,
  });
  localStorage.setItem(CHAVE, JSON.stringify(lista));
  return lista;
}

export function apagar(id: string): Salvo[] {
  const lista = listar().filter((s) => s.id !== id);
  localStorage.setItem(CHAVE, JSON.stringify(lista));
  return lista;
}

export function novoId(): string {
  return `p${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`;
}

// -- export / import -------------------------------------------------------

export function exportar(doc: Documento): void {
  const nome = (doc.identidade?.nome || "personagem")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  const blob = new Blob([JSON.stringify(doc, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${nome || "personagem"}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Aceita o documento e devolve o erro em vez de lancar: importar arquivo
 * errado e caso normal, nao excecao.
 */
export function importar(texto: string): { doc?: Documento; erro?: string } {
  let lido: unknown;
  try {
    lido = JSON.parse(texto);
  } catch {
    return { erro: "arquivo nao e JSON valido" };
  }
  if (typeof lido !== "object" || lido === null) {
    return { erro: "arquivo nao e um documento" };
  }
  const doc = lido as Documento;
  if (!Array.isArray(doc.escolhas)) {
    return { erro: "documento sem `escolhas` -- nao e uma ficha do Waybuilder" };
  }
  return { doc: { ...novoDocumento(), ...doc } };
}

// -- inventario -------------------------------------------------------------
//
// O motor le arma, armadura e escudo de `doc.inventario` e so conta o que esta
// `equipado`. Ate 2026-07-28 nenhuma tela escrevia aqui: o resultado era CA de
// personagem pelado e a aba de Ataques vazia para sempre, num motor que sabia
// calcular as duas coisas.

/** Poe um item no inventario, ja equipado -- que e o motivo de se adicionar. */
export function adicionarItem(doc: Documento, item: string): Documento {
  const inventario = [...(doc.inventario ?? [])];
  if (inventario.some((i) => i.item === item)) return doc;
  inventario.push({ item, qtd: 1, equipado: true });
  return { ...doc, inventario };
}

export function removerItem(doc: Documento, item: string): Documento {
  return {
    ...doc,
    inventario: (doc.inventario ?? []).filter((i) => i.item !== item),
  };
}

/** Guardar sem descartar: o item continua na ficha, fora do calculo. */
export function alternarEquipado(doc: Documento, item: string): Documento {
  return {
    ...doc,
    inventario: (doc.inventario ?? []).map(
      (i) => (i.item === item ? { ...i, equipado: !i.equipado } : i),
    ),
  };
}

// -- sub-escolha de classe ---------------------------------------------------
//
// Uma classe pode abrir VARIOS eixos de sub-escolha no mesmo nivel: o Campeao
// tem `cause` e dois blocos de `outras-opcoes` no nivel 1. Ate 2026-07-28 a tela
// gravava os tres com a mesma chave `(slot: "subclasse", em: 1)`, e `escolher()`
// substitui por essa chave -- entao escolher a causa sobrescrevia os outros dois
// e os tres apareciam com o MESMO valor.
//
// O eixo entra na chave. O motor nao muda: ele varre `_escolhas("subclasse")`
// inteiro e casa por `pega`, sem olhar `em` nem `eixo`.

const mesmaSub = (e: Escolha, nivel: number, eixo: string | null) =>
  e.slot === "subclasse" && e.em === nivel && (e.eixo ?? null) === eixo;

export function escolherSubclasse(
  doc: Documento, nivel: number, eixo: string | null, pega: string,
): Documento {
  const escolhas = doc.escolhas.filter((e) => !mesmaSub(e, nivel, eixo));
  escolhas.push({ em: nivel, slot: "subclasse", eixo, pega });
  return { ...doc, escolhas: ordenar(escolhas) };
}

export function limparSubclasse(
  doc: Documento, nivel: number, eixo: string | null,
): Documento {
  return { ...doc, escolhas: doc.escolhas.filter((e) => !mesmaSub(e, nivel, eixo)) };
}

export function subclasseEm(
  doc: Documento, nivel: number, eixo: string | null,
): string | null {
  const e = doc.escolhas.find((x) => mesmaSub(x, nivel, eixo));
  return typeof e?.pega === "string" ? e.pega : null;
}

// -- eixo que escolhe MAIS DE UMA -------------------------------------------
//
// `escolherSubclasse` SUBSTITUI por (nivel, eixo), que e o certo para os 52
// blocos de `escolhe: 1`. O eixo de ikon do Exemplar pede tres ("Select three
// ikons"), e substituir ali faria a segunda escolha apagar a primeira.
//
// A chave passa a ser o proprio `pega`: cada ikon e uma entrada, remover tira
// aquele, e escolher um que ja esta la nao duplica.
// Spec: specs/2026-07-30-escolha-multipla-e-ikons.md

export function subclassesEm(
  doc: Documento, nivel: number, eixo: string | null,
): string[] {
  return doc.escolhas.filter((x) => mesmaSub(x, nivel, eixo))
                     .map((x) => x.pega)
                     .filter((p): p is string => typeof p === "string");
}

export function adicionarSubclasse(
  doc: Documento, nivel: number, eixo: string | null, pega: string,
): Documento {
  if (subclassesEm(doc, nivel, eixo).includes(pega)) return doc;
  const escolhas = [...doc.escolhas, { em: nivel, slot: "subclasse", eixo, pega }];
  return { ...doc, escolhas: ordenar(escolhas) };
}

export function removerSubclasse(
  doc: Documento, nivel: number, eixo: string | null, pega: string,
): Documento {
  return {
    ...doc,
    escolhas: doc.escolhas.filter((e) => !(mesmaSub(e, nivel, eixo) && e.pega === pega)),
  };
}

// -- ator concedido por feat -------------------------------------------------
//
// O companheiro NAO vive em `escolhas`: ele e um ator, com nome, especie e
// escolhas proprias (o grau nimble/savage mora dentro dele). O que a tela faz
// aqui e casar o ator com a CONCESSAO que o abriu -- `concedido_por` + `em` --,
// que e o par que o motor procura em `_casar_ator_com_concessao`.

type Ator = {
  tipo: string;
  nome?: string;
  concedido_por?: string;
  em?: number | "criacao";
  escolhas?: Array<{ slot: string; pega: string | string[] }>;
  [campo: string]: unknown;
};

const mesmoAtor = (a: Ator, origem: string, em: number | "criacao") =>
  a.concedido_por === origem && (a.em ?? em) === em;

/** Escolhe a especie do ator daquela concessao, criando o ator se preciso. */
export function escolherAtor(
  doc: Documento,
  origem: string,
  em: number | "criacao",
  tipo: string,
  especie: string,
): Documento {
  const atores = ((doc.atores ?? []) as Ator[]).map((a) => ({ ...a }));
  const achado = atores.find((a) => mesmoAtor(a, origem, em));
  const escolha = { slot: "animal", pega: especie };
  if (achado) {
    achado.escolhas = [
      ...(achado.escolhas ?? []).filter((e) => e.slot !== "animal"),
      escolha,
    ];
  } else {
    atores.push({ tipo, nome: "", concedido_por: origem, em, escolhas: [escolha] });
  }
  return { ...doc, atores };
}

/** Nome que o jogador da ao bicho -- a unica parte que nao e derivada. */
export function renomearAtor(
  doc: Documento, origem: string, em: number | "criacao", nome: string,
): Documento {
  return {
    ...doc,
    atores: ((doc.atores ?? []) as Ator[]).map(
      (a) => (mesmoAtor(a, origem, em) ? { ...a, nome } : a)),
  };
}

/** Limpar o slot descarta o ator daquela concessao -- inclusive o nome. */
export function limparAtor(
  doc: Documento, origem: string, em: number | "criacao",
): Documento {
  return {
    ...doc,
    atores: ((doc.atores ?? []) as Ator[]).filter((a) => !mesmoAtor(a, origem, em)),
  };
}

/**
 * Escolhas que so fazem sentido por causa da classe daquele nivel.
 *
 * Trocar a classe de um nivel invalida o que foi escolhido a partir dali: um
 * feat de Alquimista nao pertence a um Campeao, e a sub-escolha de uma classe
 * nao existe na outra. O Pathbuilder zera esses blocos ao trocar, e sem isso a
 * ficha guarda escolha impossivel -- foi assim que um `Alchemical Familiar`
 * sobreviveu numa ficha de Campeao.
 *
 * Some do nivel alterado PARA A FRENTE, e so o que depende de classe. O que e
 * de ancestralidade, background ou pericia nao e tocado: continua valendo.
 */
const DEPENDEM_DA_CLASSE = new Set(["class_feat", "subclasse", "free_archetype"]);

export function limparDependentesDeClasse(
  doc: Documento, aPartirDe: number,
): Documento {
  return {
    ...doc,
    escolhas: doc.escolhas.filter((e) => {
      if (!DEPENDEM_DA_CLASSE.has(e.slot)) return true;
      return typeof e.em === "number" ? e.em < aPartirDe : true;
    }),
  };
}
