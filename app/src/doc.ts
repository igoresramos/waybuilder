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
 * A houserule: cada nivel de personagem compra um nivel de UMA classe. E o
 * unico lugar do app onde a regra da casa aparece como escolha.
 */
export function definirClasseDoNivel(
  doc: Documento,
  nivel: number,
  classeId: string,
): Documento {
  const escolhas = doc.escolhas.filter(
    (e) => !(e.slot === "nivel_de_classe" && e.em === nivel),
  );
  escolhas.push({ em: nivel, slot: "nivel_de_classe", pega: classeId });
  return { ...doc, escolhas: ordenar(escolhas) };
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
