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
import type { Documento, Escolha, PinDaBase } from "./motor/tipos";

const CHAVE = "waybuilder:personagens";
const CHAVE_ULTIMA = "waybuilder:ultima";
/** onde os bytes de uma lista ilegivel sao copiados antes de a chave sumir */
const PREFIXO_RESGATE = `${CHAVE}:corrompido-`;

export const ESQUEMA_ATUAL = 2;
const ESQUEMA = `waybuilder/personagem@${ESQUEMA_ATUAL}`;

/** o nome que `novoDocumento()` da: presente no campo, ausente como conteudo */
const SEM_NOME = "Sem nome";

export interface Salvo {
  id: string;
  nome: string;
  atualizado: string;
  doc: Documento;
}

export function novoDocumento(nome = SEM_NOME): Documento {
  return {
    esquema: ESQUEMA,
    // o id nasce AQUI, uma vez, e viaja dentro do documento -- ate 2026-08-01
    // `App.tsx:54` o cunhava a cada mount e a ficha nunca voltava (issue #1)
    id: novoId(),
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
  return { ...doc, escolhas: ordenarEscolhas(escolhas) };
}

/**
 * Slot que aceita VARIAS escolhas no mesmo nivel, enderecadas por indice.
 *
 * `escolher()` nao serve: ele apaga toda escolha do par (slot, em) antes de
 * gravar, o que e certo para ancestralidade e errado para pericia treinada --
 * um Guerreiro escolhe TRES, e a segunda apagaria a primeira.
 *
 * `id === null` remove aquela posicao. As demais nao se deslocam: a posicao e
 * a identidade enquanto a tela estiver aberta.
 * Spec: specs/2026-07-31-slots-de-criacao-na-tela.md
 */
export function definirMultipla(
  doc: Documento,
  slot: string,
  em: number | "criacao",
  indice: number,
  id: string | null,
): Documento {
  const minhas = doc.escolhas.filter((e) => e.slot === slot && e.em === em);
  const outras = doc.escolhas.filter((e) => !(e.slot === slot && e.em === em));
  const valores = minhas.map((e) => e.pega as string);
  while (valores.length <= indice) valores.push("");
  valores[indice] = id ?? "";
  for (const v of valores) {
    if (v) outras.push({ em, slot, pega: v });
  }
  return { ...doc, escolhas: ordenarEscolhas(outras) };
}

/** As escolhas de um slot multiplo, na ordem -- `""` onde nada foi escolhido. */
export function multiplas(
  doc: Documento,
  slot: string,
  em: number | "criacao",
): string[] {
  return doc.escolhas
    .filter((e) => e.slot === slot && e.em === em)
    .map((e) => e.pega as string);
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
  return { ...doc, escolhas: ordenarEscolhas(escolhas) };
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
  return { ...partida, escolhas: ordenarEscolhas(escolhas) };
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
  return { ...doc, escolhas: ordenarEscolhas(outros) };
}

/** `criacao` sempre antes de qualquer nivel numerado. */
export function ordenarEscolhas(escolhas: Escolha[]): Escolha[] {
  const chave = (e: Escolha) => (typeof e.em === "number" ? e.em : 0);
  return [...escolhas].sort((a, b) => chave(a) - chave(b));
}

export function nivelDoPersonagem(doc: Documento): number {
  return doc.escolhas.filter((e) => e.slot === "nivel_de_classe").length;
}

// -- versao de esquema e migracao -------------------------------------------
//
// `doc.esquema` existia desde sempre e NUNCA era lido: `grep -rn esquema
// app/src` so achava escritas. Passa a decidir a migracao.
//
// `@1 -> @2` adiciona `id` e `base`. Nada e removido nem renomeado, e a
// migracao e idempotente: rodar duas vezes da o mesmo documento.

export function versaoDeEsquema(d: Documento): number {
  const m = /@(\d+)\s*$/.exec(String(d?.esquema ?? ""));
  // ausente ou ilegivel = `@1`: todo documento gravado ate 2026-08-01 e `@1`,
  // e um escrito a mao pode nao ter o campo
  return m ? Number(m[1]) : 1;
}

/**
 * Poe o documento na forma atual, ou explica por que nao pos.
 *
 * Documento de versao FUTURA abre assim mesmo, intacto e com aviso -- inclusive
 * o `esquema`, que nao e rebaixado: rebaixar destruiria a unica informacao de
 * que aquele documento veio de um app mais novo, e o campo desconhecido que ele
 * carrega e preservado pelo spread da gravacao.
 * Spec: `specs/2026-07-26-schema-personagem.md:175-176`.
 *
 * `idDeFallback` e o `id` da ENTRADA do indice: numa ficha `@1` ele ja existe,
 * ja e unico e ja e estavel em disco -- so nunca esteve dentro do documento.
 */
export function migrar(
  d: Documento,
  idDeFallback?: string,
): { doc: Documento; avisos: string[] } {
  const n = versaoDeEsquema(d);
  if (n > ESQUEMA_ATUAL) {
    return {
      doc: d,
      avisos: [
        `esta ficha foi gravada num esquema mais novo (@${n}); este app entende `
        + `ate @${ESQUEMA_ATUAL}. Ela abre inteira, e o que este app nao conhece `
        + "e preservado na gravacao.",
      ],
    };
  }
  if (n < 2) {
    return {
      doc: {
        ...d,
        id: d.id ?? idDeFallback ?? novoId(),
        // `pin: null` = montada sob base nao registrada. `nascida_em_pin: null`
        // PRESENTE e nulo: o carimbo so preenche o campo ausente, entao ficha
        // migrada nunca recebe a base de hoje como berco -- seria falso.
        base: d.base ?? { pin: null, origem: "desconhecido", nascida_em_pin: null },
        esquema: ESQUEMA,
      },
      avisos: [],
    };
  }
  // ja `@2`: so o id, se um documento escrito a mao chegou sem ele
  return { doc: d.id ? d : { ...d, id: idDeFallback ?? novoId() }, avisos: [] };
}

// -- persistencia ----------------------------------------------------------
//
// O `localStorage` E o banco: sem servidor, o que nao esta aqui nao existe.
// Duas regras mandam nesta secao, e as duas vem do principio 4 (nada e
// descartado):
//
//   1. entrada que nao se entende e PRESERVADA e pulada -- nunca descartada;
//   2. chave ilegivel e COPIADA antes de qualquer `setItem` que a substitua.
//
// A regra 2 fecha o unico caminho de perda total que sobrava: `listar()`
// devolvia `[]` para um JSON quebrado e a gravacao seguinte escrevia uma lista
// de um elemento por cima de tudo.

/** Uma entrada bem-formada tem um `doc` com `escolhas` -- o resto e lixo a preservar. */
function bemFormada(e: unknown): e is { id?: unknown; atualizado?: unknown; doc: Documento } {
  if (typeof e !== "object" || e === null) return false;
  const doc = (e as { doc?: unknown }).doc;
  return typeof doc === "object" && doc !== null
    && Array.isArray((doc as Documento).escolhas);
}

interface Leitura {
  /** o array cru, exatamente como esta em disco -- inclusive as malformadas */
  entradas: unknown[];
  /** indice no array cru -> id resolvido; so das bem-formadas */
  idPorIndice: Map<number, string>;
  salvos: Salvo[];
  ilegivel: boolean;
  cru: string | null;
}

function ler(): Leitura {
  const vazio: Leitura = {
    entradas: [], idPorIndice: new Map(), salvos: [], ilegivel: false, cru: null,
  };
  let cru: string | null = null;
  try {
    cru = localStorage.getItem(CHAVE);
  } catch {
    return vazio; // `localStorage` bloqueado (modo anonimo antigo): sem lista, com app
  }
  if (cru === null) return vazio;

  let lido: unknown;
  try {
    lido = JSON.parse(cru);
  } catch {
    return { ...vazio, ilegivel: true, cru };
  }
  if (!Array.isArray(lido)) return { ...vazio, ilegivel: true, cru };

  const idPorIndice = new Map<number, string>();
  const salvos: Salvo[] = [];
  const usados = new Set<string>();
  lido.forEach((entrada, i) => {
    if (!bemFormada(entrada)) return; // preservada em `entradas`, fora da lista
    const idEntrada =
      typeof entrada.id === "string" && entrada.id ? entrada.id : `p-sem-id-${i}`;
    // O DOCUMENTO GANHA na divergencia: ele e a fonte de verdade e o indice e
    // espelho. A excecao existe para nao criar duas fichas com o mesmo id --
    // quem chegou depois cede, e a ordem do array decide, o que torna a
    // resolucao deterministica (nada de id aleatorio no meio de uma leitura).
    let id = typeof entrada.doc.id === "string" && entrada.doc.id
      ? entrada.doc.id : idEntrada;
    if (usados.has(id)) id = idEntrada;
    if (usados.has(id)) id = `${idEntrada}#${i}`;
    usados.add(id);
    idPorIndice.set(i, id);

    const migrado = migrar(entrada.doc, id).doc;
    const doc = migrado.id === id ? migrado : { ...migrado, id };
    salvos.push({
      id,
      nome: doc.identidade?.nome || SEM_NOME,
      atualizado: typeof entrada.atualizado === "string" ? entrada.atualizado : "",
      doc,
    });
  });
  return { entradas: lido, idPorIndice, salvos, ilegivel: false, cru };
}

/**
 * As fichas em disco, ja migradas EM MEMORIA.
 *
 * A migracao so vai ao disco na proxima gravacao daquela ficha: reescrever as N
 * entradas de uma vez e uma unica escrita grande que, com a cota apertada --
 * exatamente o cenario que a issue #1 produzia --, falha levando tudo junto.
 */
export function listar(): Salvo[] {
  return ler().salvos;
}

export interface ResultadoDeGravacao {
  ok: boolean;
  lista: Salvo[];
  /** `cota` cobre `QuotaExceededError` e qualquer recusa do `setItem` */
  erro?: "cota" | "resgate";
  detalhe?: string;
}

/**
 * Copia os bytes de uma lista ilegivel para uma chave propria.
 *
 * Devolve `false` se a copia nao coube -- e ai a gravacao NAO acontece: perder
 * a chance de gravar e recuperavel, sobrescrever o que nao se conseguiu copiar
 * nao e.
 */
function resgatarIlegivel(l: Leitura): boolean {
  if (!l.ilegivel || l.cru === null) return true;
  try {
    localStorage.setItem(`${PREFIXO_RESGATE}${new Date().toISOString()}`, l.cru);
    return true;
  } catch {
    return false;
  }
}

/**
 * Grava a ficha. O id vem de DENTRO do documento -- passar id por fora foi o
 * que permitiu ao `App.tsx:54` inventar um a cada mount (issue #1).
 *
 * Nao lanca: cota estourada e caso normal de um banco que mora no navegador, e
 * quem chama precisa poder avisar sem perder a edicao.
 */
export function salvar(documento: Documento): ResultadoDeGravacao {
  const l = ler();
  const id = documento.id ?? novoId();
  const doc = documento.id ? documento : { ...documento, id };

  if (!resgatarIlegivel(l)) {
    return {
      ok: false, lista: l.salvos, erro: "resgate",
      detalhe: "a lista em disco esta ilegivel e a copia de resgate nao coube; "
        + "nada foi sobrescrito",
    };
  }

  // as OUTRAS entradas voltam ao disco como estavam, inclusive as malformadas
  const preservadas = l.entradas.filter((_, i) => l.idPorIndice.get(i) !== id);
  const lista = [
    ...preservadas,
    { id, nome: doc.identidade?.nome || SEM_NOME, atualizado: new Date().toISOString(), doc },
  ];
  try {
    localStorage.setItem(CHAVE, JSON.stringify(lista));
  } catch (e) {
    return { ok: false, lista: l.salvos, erro: "cota", detalhe: String(e) };
  }
  return { ok: true, lista: ler().salvos };
}

/** Apagar e ato do jogador. Nenhum caminho de codigo chama isto sem clique. */
export function apagar(id: string): ResultadoDeGravacao {
  const l = ler();
  if (!resgatarIlegivel(l)) {
    return { ok: false, lista: l.salvos, erro: "resgate", detalhe: "lista ilegivel" };
  }
  const restantes = l.entradas.filter((_, i) => l.idPorIndice.get(i) !== id);
  try {
    localStorage.setItem(CHAVE, JSON.stringify(restantes));
    if (ultimaAberta() === id) esquecerUltima();
  } catch (e) {
    return { ok: false, lista: l.salvos, erro: "cota", detalhe: String(e) };
  }
  return { ok: true, lista: ler().salvos };
}

export function novoId(): string {
  return `p${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`;
}

// -- qual ficha o app abre ---------------------------------------------------

/** O ponteiro da ultima ficha ABERTA -- decisao, nao derivacao de `atualizado`. */
export function ultimaAberta(): string | null {
  try {
    return localStorage.getItem(CHAVE_ULTIMA);
  } catch {
    return null;
  }
}

export function marcarAberta(id: string): void {
  try {
    localStorage.setItem(CHAVE_ULTIMA, id);
  } catch {
    // ponteiro e conveniencia: sem ele a precedencia cai no maior `atualizado`
  }
}

export function esquecerUltima(): void {
  try {
    localStorage.removeItem(CHAVE_ULTIMA);
  } catch {
    /* idem */
  }
}

/** `#/p/<id>` -- hash, e nao rota: nao exige nada do servidor nem do SW. */
export function idDoHash(hash: string): string | null {
  const m = /^#\/p\/([^/?#]+)$/.exec((hash ?? "").trim());
  return m ? decodeURIComponent(m[1]) : null;
}

export interface Abertura {
  doc: Documento;
  avisos: string[];
  /** `true` = documento novo, ainda NAO gravado */
  nova: boolean;
}

function abrirSalvo(s: Salvo, antes: string[]): Abertura {
  const { doc: d, avisos } = migrar(s.doc, s.id);
  marcarAberta(s.id);
  return { doc: d, avisos: [...antes, ...avisos], nova: false };
}

/**
 * A precedencia da carga. Primeira que resolve ganha:
 *
 *   1. `#/p/<id>` que nomeia uma entrada existente;
 *   2. o ponteiro `waybuilder:ultima`;
 *   3. a entrada de maior `atualizado` (a unica pista que a bagunca legada tem);
 *   4. documento novo, NAO gravado -- e o que impede a visita ociosa de deixar
 *      entrada, que e o defeito da issue #1 voltando por outra porta.
 *
 * Hash que nomeia ficha inexistente AVISA e cai no passo 4. Escorrer para o
 * passo 2 abriria uma ficha DIFERENTE com o endereco de outra, e o debounce
 * gravaria por cima dela em 500 ms.
 */
export function abrir(hash = hashAtual()): Abertura {
  const lista = listar();
  const porId = new Map(lista.map((s) => [s.id, s]));

  const pedido = idDoHash(hash);
  if (pedido) {
    const achado = porId.get(pedido);
    if (achado) return abrirSalvo(achado, []);
    return {
      doc: novoDocumento(),
      avisos: [`o endereco pede a ficha \`${pedido}\`, que nao existe neste `
        + "navegador; abrindo uma ficha nova em vez de outra qualquer"],
      nova: true,
    };
  }

  const ponteiro = ultimaAberta();
  const apontada = ponteiro ? porId.get(ponteiro) : undefined;
  if (apontada) return abrirSalvo(apontada, []);

  if (lista.length) {
    const recente = [...lista].sort(
      (a, b) => (a.atualizado < b.atualizado ? 1 : a.atualizado > b.atualizado ? -1 : 0),
    )[0];
    return abrirSalvo(recente, []);
  }
  return { doc: novoDocumento(), avisos: [], nova: true };
}

function hashAtual(): string {
  return typeof location === "undefined" ? "" : location.hash;
}

/**
 * O que conta como ficha a gravar.
 *
 * Visita que so abre o app nao pode deixar entrada -- era uma entrada nova por
 * recarga (issue #1). O nome default nao conta como conteudo: ele vem de
 * `novoDocumento()`, nao do jogador.
 */
export function temConteudo(d: Documento): boolean {
  if (d.escolhas.length) return true;
  if ((d.atores?.length ?? 0) > 0) return true;
  if ((d.inventario?.length ?? 0) > 0) return true;
  const nome = (d.identidade?.nome ?? "").trim();
  return nome !== "" && nome !== SEM_NOME;
}

// -- identidade de build -----------------------------------------------------

/**
 * Carimba no documento sob que base ele esta sendo editado.
 *
 * Pin nulo (`crypto.subtle` fora de secure context, ou ficha migrada) NAO
 * carimba nada: gravar `null` por cima de um pin real apagaria a unica
 * informacao boa que a ficha ja tinha.
 */
export function carimbarBase(d: Documento, atual: PinDaBase): Documento {
  if (!atual.pin) return d;
  const base = { ...(d.base ?? {}) };
  base.pin = atual.pin;
  base.origem = atual.origem;
  if (atual.registros !== undefined) base.registros = atual.registros;
  if (atual.kinds !== undefined) base.kinds = atual.kinds;
  base.visto_em = new Date().toISOString();
  // so o campo AUSENTE: `nascida_em_pin: null` de ficha migrada fica nulo
  if (!("nascida_em_pin" in base)) base.nascida_em_pin = atual.pin;
  return { ...d, base };
}

/**
 * O aviso de base divergente -- AVISA, nunca recusa (principio 1).
 *
 * So compara pin contra pin. Ficha sem pin (migrada, ou carregada sem
 * `crypto.subtle`) nao diverge de nada: afirmar divergencia sem ter os dois
 * lados seria inventar.
 */
export function avisoDePin(d: Documento, atual: PinDaBase): string | null {
  const antes = d.base?.pin;
  if (!antes || !atual.pin || antes === atual.pin) return null;
  const nAntes = d.base?.registros;
  const quantos = (n?: number) => (n === undefined ? "?" : n.toLocaleString("pt-BR"));
  return `esta ficha foi editada sobre outra base (${antes.slice(0, 8)}, `
    + `${quantos(nAntes)} registros); a atual e ${atual.pin.slice(0, 8)}, `
    + `${quantos(atual.registros)}. A ficha foi re-derivada, nada foi removido.`;
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
 *
 * Tres casos de `id`, e nenhum deles sobrescreve ficha existente: importar o
 * proprio backup por cima de uma ficha editada depois seria descartar trabalho
 * sem perguntar. Restaurar backup por cima passa a exigir apagar antes -- o que
 * so e aceitavel porque o seletor de fichas existe.
 */
export function importar(
  texto: string,
  existentes: string[] = listar().map((s) => s.id),
): { doc?: Documento; erro?: string; aviso?: string } {
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
  // o spread NAO descarta chave desconhecida -- propriedade contratual desde
  // esta spec, e o que faz um documento `@futuro` voltar inteiro na gravacao
  const bruto = { ...novoDocumento(), ...doc };
  const { doc: migrado, avisos } = migrar(bruto);
  const veioComId = typeof doc.id === "string" && doc.id !== "";
  if (veioComId && existentes.includes(doc.id as string)) {
    return {
      doc: { ...migrado, id: novoId() },
      aviso: "esta ficha ja existia neste navegador; entrou como copia",
    };
  }
  return { doc: migrado, aviso: avisos[0] };
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
  return { ...doc, escolhas: ordenarEscolhas(escolhas) };
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
  return { ...doc, escolhas: ordenarEscolhas(escolhas) };
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
