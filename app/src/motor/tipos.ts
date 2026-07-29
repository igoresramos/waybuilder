/**
 * Contrato do motor no cliente.
 *
 * Estes tipos sao a fronteira entre o porte de `motor/motor.py` e a tela: a UI
 * so conhece o que esta aqui. Foi escrito ANTES do porte de proposito, para
 * que implementacao e interface pudessem andar em paralelo sem colidir.
 *
 * O gabarito do porte esta em `motor/fixtures/*.json`, gerado pelo Python.
 */

export type Rank = "untrained" | "trained" | "expert" | "master" | "legendary";

export const RANKS: Rank[] = [
  "untrained", "trained", "expert", "master", "legendary",
];

export const ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"] as const;
export type Atributo = (typeof ATRIBUTOS)[number];

/** Um registro da base canonica. Campos variam por `kind`; so estes sao certos. */
export interface Registro {
  id: string;
  kind?: string;
  name?: string;
  level?: number | null;
  traits?: string[];
  rarity?: string;
  requires?: unknown;
  grants?: unknown[];
  aliases?: string[];
  archetype?: string;
  text?: string;
  source?: { book?: string; page?: number; license?: string };
  [campo: string]: unknown;
}

/**
 * Uma escolha do jogador. `em` e o nivel de PERSONAGEM em que ela aconteceu --
 * ou "criacao", para o que vem antes do nivel 1.
 *
 * `pega` nem sempre e um id: `boosts_livres` guarda uma lista de atributos.
 */
export interface Escolha {
  em: number | "criacao";
  slot: string;
  pega?: string | string[];
  [campo: string]: unknown;
}

/**
 * O documento de personagem -- a UNICA fonte de verdade. Tudo mais e derivado
 * a cada mudanca; nada calculado e guardado aqui. E por isso que mudanca de
 * regra re-deriva em vez de invalidar ficha salva.
 */
export interface Documento {
  esquema?: string;
  base?: { versao?: string; pin_foundry?: string };
  identidade?: { nome?: string; jogador?: string; notas?: string };
  escolhas: Escolha[];
  atores?: unknown[];
  inventario?: Array<{
    item: string; qtd?: number; equipado?: boolean; potencia?: number;
  }>;
  manual?: Record<string, unknown>;
}

/** Um slot por preencher. E o roteiro do jogador -- a lista guia a tela. */
export interface SlotAberto {
  slot: string;
  em: number | "criacao" | null;
  kind: string | null;
  escolhe: number;
  rotulo: string;
  /** CONTAGEM de opções do eixo de subclasse, não a lista -- é o que o motor
   * guarda em `slots_de_subclasse` e repassa aqui. */
  opcoes?: number;
  fontes?: FonteDeBoost[];
  /** quem abriu o slot -- hoje só o concessor de ator (`grant_actor`) */
  origem?: string;
  /** ids que o concessor SUGERE. Ordenam a lista, não a filtram. */
  opcoes_ids?: string[];
}

/**
 * Companheiro, familiar ou eidolon com a ficha derivada. Os campos de stat só
 * existem para `tipo: "companheiro"` -- familiar e eidolon entram na lista sem
 * ficha, porque o modelo deles ainda não existe (ver a dívida na spec
 * `2026-07-29-companheiro-concedido`).
 */
export interface Ator {
  tipo: string;
  nome: string;
  concedido_por: string | null;
  em?: number | "criacao" | null;
  classe: string | null;
  nivel_de_classe: number;
  /** cap da regra 17b, ancorado na classe que CONCEDEU */
  nivel: number;
  nota: string | null;
  especie?: string;
  maturidade?: string;
  especializado?: boolean;
  grau_pendente?: boolean;
  tamanho?: string;
  /** `{land: 40, max: 40}` -- por modo de deslocamento, em pes */
  velocidade?: Record<string, number>;
  sentidos?: string;
  atributos?: Record<string, number>;
  hp?: number;
  hp_detalhe?: string;
  ac?: number;
  proficiencias?: Record<string, Rank>;
  saves?: Record<string, number>;
  percepcao?: number;
  ataques?: Array<{
    nome?: string; ataque: number; dano: string;
    tipo?: string | null; traits?: string[]; agil?: boolean;
  }>;
  support?: string | null;
  manobra_avancada?: string | null;
  /** espécie não encontrada na base -- a ficha não pôde ser montada */
  aviso?: string;
}

/** Um `grant_actor` ativo na ficha: o feat que concede o companheiro, o nível
 * em que foi pego (e portanto a classe que ancora o cap da regra 17b) e se a
 * espécie já foi escolhida. */
export interface ConcessaoDeAtor {
  origem: string;
  origem_nome: string;
  em: unknown;
  tipo: string;
  escolhe: string;
  opcoes: string[];
  classe: string | null;
  preenchida: boolean;
  escolhido: string | null;
}

export interface FonteDeBoost {
  origem: string;
  origem_id: string | null;
  quantidade: number;
  /** `null` = livre entre os seis; lista = escolha restrita */
  opcoes: string[] | null;
  em: number | "criacao";
}

/**
 * Um candidato a um slot.
 *
 * PRINCIPIO ZERO: `atende: false` NAO some da lista -- aparece marcado, com o
 * motivo. O slot filtra por TIPO; o requisito so ordena. Uma tela que esconde
 * o que nao atende quebra a regra central do projeto.
 */
export interface Candidato {
  id: string;
  nome: string | null;
  level: number | null;
  atende: boolean;
  motivos: string[];
  ja_pego: boolean;
  /** o concessor cita esta opção pelo nome (Rough Rider -> Wolf). Só ordena. */
  sugerida?: boolean;
}

export interface LinhaDeFeature {
  id: string | null;
  nome: string | null;
  classe: string | null;
  origem?: string;
  nivel_de_classe: number | null;
  /** os `grants` crus do registro -- a cadeia os relê, e a visão os expõe */
  grants: unknown[];
  na_base: boolean;
  eixo?: string | null;
  raiz?: string;
  concedido_por?: string;
}

export interface Concedido {
  id: string;
  nome: string;
  /** nome de quem concedeu */
  por: string;
  por_id: string;
}

export interface ForaDoRequisito {
  feat: string;
  motivo: string;
}

export interface SlotDeSubclasse {
  classe: string;
  eixo: string | null;
  nivel: number | null;
  /** quantas opções o eixo tem */
  opcoes: number;
  /** e QUAIS -- `candidatos("subclasse")` precisa dos ids */
  opcoes_ids: string[];
  escolhido: string | null;
  nome: string | null;
}

export interface Conjuracao {
  classe: string;
  /** `null` na conjuração de arquétipo: ela não vem de nível de classe */
  nivel_de_classe: number | null;
  /** veio de uma dedicação, não de níveis -- e por isso NÃO eleva (regra 18) */
  de_arquetipo?: boolean;
  /** o feat que abriu a rota */
  origem?: string;
  tradicao: string | null;
  tipo: string | null;
  truques: number | null;
  slots: Record<string, number>;
  /** regra 16: vem do nível de CLASSE cru */
  max_rank_do_slot: number;
  /** regra 17: ceil(nivel_de_personagem / 2) */
  rank_efetivo: number;
  elevacao: number;
  /** regra 17b: teto do que cria criatura */
  rank_de_invocacao: number;
  dc: { rank: Rank; dc: number; ataque: number; nota: string };
}

/** AC e a armadura que a produziu. */
export interface AC {
  total: number;
  armadura: string | null;
  categoria: string;
  rank: Rank;
  detalhe: string;
  dex_perdida: number;
  check_penalty: number;
  escudo: { nome: string | null; ac: number } | null;
}

export interface Ataque {
  arma: string | null;
  categoria: string;
  rank: Rank;
  ataque: number;
  atributo_do_ataque: "str" | "dex";
  dano: string;
  tipo_de_dano: string | null;
  traits: string[];
  detalhe: string;
}

export interface AumentoDePericia {
  nivel: number | "criacao" | null;
  pericia: string;
  de: Rank;
  para: Rank;
}

/** A visao calculada. Cache, nunca fonte de verdade. */
export interface Visao {
  nivel: number;
  classes: Record<string, number>;
  ancestralidade?: string | null;
  heranca?: string | null;
  background?: string | null;
  atributos: Record<string, number>;
  modificadores: Record<string, number>;
  hp: number;
  proficiencias: Record<string, Rank>;
  pericias_livres: number;
  aumentos_de_pericia: { niveis: number[]; gastos: AumentoDePericia[] };
  boosts: { direito: number; declarados: number; fontes: FonteDeBoost[] };
  slots_abertos: SlotAberto[];
  slots: Record<string, number[]>;
  conjuracao: Conjuracao[];
  atores: Ator[];
  concessoes_de_ator: ConcessaoDeAtor[];
  escolhas_de_feat: unknown;
  focus_pool: number;
  ac: AC;
  ataques: Ataque[];
  features: LinhaDeFeature[];
  concedidos: Concedido[];
  subclasses: SlotDeSubclasse[];
  fora_do_requisito: ForaDoRequisito[];
  avisos: string[];
}
