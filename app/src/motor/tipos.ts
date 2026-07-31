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

/** Uma opção de `ChoiceSet` (spec `2026-07-29-choiceset.md`). `valor` é o que a
 * consequência cita no `predicate`; `rotulo` é o que a tela mostra; `grants` são
 * as consequências já aninhadas nesta opção -- 56 das 570 opções da base as
 * têm, e é por elas que escolher a opção muda número na ficha. */
export interface OpcaoDeGrant {
  rotulo: string;
  valor: string;
  grants?: unknown[];
}

/** Uma resistência, fraqueza ou imunidade na ficha. `valor` não existe em
 * imunidade. Spec `2026-07-30-resistencia-e-formula.md`. */
export interface LinhaDeResistencia {
  tipo: string;
  valor?: number;
  origem: string;
}

/** Um bônus somado a um total, com o tipo que decide se ele empilha. */
export interface BonusAplicado {
  tipo: unknown;
  valor: number;
  origem: string;
}

/** Uma linha de perícia ou salva com o total já calculado. Até 2026-07-30 esta
 * conta vivia em `PainelDireito.tsx` -- sem oráculo, sem paridade e sem onde
 * receber `flat_modifier`. Spec `2026-07-30-bonus-de-pericia-e-salva.md`. */
export interface LinhaDePericia {
  chave: string;
  nome: string;
  rank: Rank;
  atributo: string;
  mod_atributo: number;
  bonus_total: number;
  total: number;
  detalhe: string;
  bonus?: BonusAplicado[];
}

/** O detalhe por classe do orçamento de perícias livres (spec
 * `2026-07-29-pericias-livres.md`): quanto a classe deu, quanto sobrou. */
export interface DetalheDePericiaLivre {
  classe: string;
  orcamento: number;
  delta: number;
}

/** Um slot por preencher. E o roteiro do jogador -- a lista guia a tela. */
export interface SlotAberto {
  slot: string;
  em: number | "criacao" | null;
  kind: string | null;
  escolhe: number;
  rotulo: string;
  /** Duas leituras na MESMA chave, e é assim que o oráculo Python emite:
   * CONTAGEM de opções no eixo de `subclasse` (o motor guarda em
   * `slots_de_subclasse` e repassa), e as OPÇÕES do ChoiceSet na
   * `escolha_de_grant` -- `{rotulo, valor}`, onde `valor` é o caminho do
   * Foundry que a opção preenche, não um id da base. O tipo descreve o dado;
   * separar as duas exigiria mexer no gabarito, que é outra decisão. */
  opcoes?: number | OpcaoDeGrant[];
  /** `FonteDeBoost` em `boosts_livres`; `{classe, orcamento, delta}` em
   * `pericias_livres`. Mesma situação da chave acima. */
  fontes?: FonteDeBoost[] | DetalheDePericiaLivre[];
  /** o rótulo do ChoiceSet que a opção escolhida preenche (`escolha_de_grant`);
   * `null` quando a fonte não nomeia a escolha. */
  flag?: string | null;
  /** quem abriu o slot -- hoje só o concessor de ator (`grant_actor`) */
  origem?: string;
  /** ids que o concessor SUGERE. Ordenam a lista, não a filtram. */
  opcoes_ids?: string[];
}

/**
 * Companheiro, familiar ou eidolon com a ficha derivada.
 *
 * Os três têm ficha desde 2026-07-31. Antes disso só o companheiro tinha, e a
 * razão era o schema do AoN: `animal-companion` traz colunas numéricas nativas,
 * enquanto familiar e eidolon DERIVAM do mestre -- o que existe para eles é
 * fórmula, não tabela, e ela mora em `aon_dump/rules.json`, um arquivo que
 * nenhum extrator abria.
 *
 * As três fichas não têm os mesmos campos, e as ausências são deliberadas: o
 * familiar não tem `atributos` (a regra diz que ele não usa os próprios) e o
 * eidolon não tem `hp` (compartilha o pool do invocador).
 * Spec: `specs/2026-07-31-estatisticas-de-familiar-e-eidolon.md`
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
  /** ausente no FAMILIAR de proposito: ele "doesn't have or use its own
   * attribute modifiers". Ausencia e resposta -- a ficha diz isso em vez de
   * mostrar +0 em tudo. */
  atributos?: Record<string, number>;
  /** `null` no EIDOLON: ele nao tem HP proprio, compartilha o pool do
   * invocador. Ver `nota_de_hp`. */
  hp?: number | null;
  hp_detalhe?: string;
  nota_de_hp?: string;
  ac?: number | null;
  proficiencias?: Record<string, Rank>;
  /** sempre o TOTAL, nunca a linha inteira -- o cartao de ator mostra numero.
   * No familiar sao os do MESTRE, porque a regra diz "equal to yours". */
  saves?: Record<string, number | undefined>;
  percepcao?: number;
  /** familiar: `3 + nivel` ou o mod de conjuracao, e qual dos dois valeu */
  nota_de_pericia?: string;
  outras_pericias?: number;
  pericias?: unknown;
  /** eidolon: o array escolhido e os que existem */
  array?: string | null;
  arrays_possiveis?: Array<string | null>;
  arrays_pendente?: boolean;
  nota_de_array?: string;
  dex_cap?: number | null;
  tamanhos?: string[];
  tradicao?: unknown;
  pericias_do_invocador?: boolean;
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
  /** a prosa do proprio registro declara conceder um ator ADICIONAL (6 dos 30
   *  concessores). Ver `specs/2026-07-30-segundo-ator.md`. */
  adicional: boolean;
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
  /** quantas o eixo pede. 1 em 52 dos 53 blocos; 3 no eixo de ikon do Exemplar */
  escolhe: number;
  /** todas as escolhidas, na ordem da fonte. Spec `escolha-multipla-e-ikons` */
  escolhidos: string[];
  /** a primeira de `escolhidos` -- o que os blocos de `escolhe: 1` sempre foram */
  escolhido: string | null;
  nome: string | null;
  /** eixo por QUERY: o filtro do `ChoiceSet` do Foundry, verbatim, em vez de uma
   * lista congelada -- congelar dessincroniza na primeira mudanca de fonte.
   * Kineticist (`kinetic-gate`) e Commander (`tactic`) sao os dois primeiros.
   * Spec: `specs/2026-07-31-tag-e-eixo-por-query.md` */
  filtro?: unknown;
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
  /** contendores do bonus de ITEM da CA -- a armadura e os grants de item
   *  equipados disputam entre si, e vale o maior. Ver
   *  `specs/2026-07-30-bonus-de-item-equipado.md`. */
  bonus: BonusAplicado[];
}

/** slot de feat que um feat ou heranca CONCEDEU (ChoiceSet do Foundry com
 *  `itemType: "feat"`). Ver `specs/2026-07-30-slot-de-feat-concedido.md`. */
export interface SlotConcedido {
  origem: string;
  origem_id: string;
  /** nivel em que o concessor entrou, ou `criacao` */
  em: number | "criacao";
  /** `rollOption` do ChoiceSet -- e ele que da identidade ao slot */
  flag: string | null;
  /** o filtro verbatim da fonte: lista de atomos e operadores */
  filtro: unknown;
}

/** Uma parcela do dano. `dados` traz `texto` (`"2d8"`); as outras, `valor`. */
export interface ParcelaDeDano {
  tipo: "dados" | "atributo" | "weapon_specialization" | "rage";
  texto?: string;
  valor?: number;
  origem: string | null;
}

/** Parcela que só vale sob uma condição de rolagem. NÃO entra no `total`:
 * aparece na ficha com a condição escrita. Princípio zero -- marca, nunca
 * esconde nem soma escondido. */
export interface DanoCondicional {
  valor: number;
  origem: string | null;
  condicao: string;
}

/** O dano decomposto. Até 2026-07-30 era só a string já concatenada
 * (`"2d8+4"`): o ataque tinha `detalhe`, o dano não tinha nada -- e estava
 * incompleta, faltando Weapon Specialization e dano de fúria.
 * Spec: `specs/2026-07-30-dano-de-furia.md` */
export interface DanoDecomposto {
  parcelas: ParcelaDeDano[];
  total: string;
  condicionais: DanoCondicional[];
}

export interface Ataque {
  arma: string | null;
  categoria: string;
  rank: Rank;
  ataque: number;
  atributo_do_ataque: "str" | "dex";
  dano: DanoDecomposto;
  tipo_de_dano: string | null;
  /** runas do item equipado: potência soma no ataque, striking soma DADOS de
   * dano, e as de propriedade só aparecem (o motor não roda o efeito delas).
   * O oráculo Python já emitia os três e o tipo não tinha sido atualizado. */
  potencia: number;
  striking: number;
  runas_de_propriedade: string[];
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
/**
 * A divindade na ficha. `dominios` e `arma_favorita` guardam id NA BASE, e a
 * tela mostra nome -- por isso o par `{id, nome}` em vez do id cru.
 * Spec: specs/2026-07-30-divindade-na-ficha.md
 */
export interface VisaoDeDivindade {
  id: string;
  nome: string;
  /** `heal`, `harm`, ou as duas (137 das 479 divindades permitem escolher) */
  fonte_divina: string[];
  atributo_divino: string[];
  dominios: Array<{ id: string; nome: string }>;
  dominios_alternativos: Array<{ id: string; nome: string }>;
  arma_favorita: Array<{ id: string; nome: string }>;
  santificacao: string | null;
}

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
  pericias: LinhaDePericia[];
  salvas: Record<string, LinhaDePericia>;
  pericias_livres: number;
  aumentos_de_pericia: { niveis: number[]; gastos: AumentoDePericia[] };
  boosts: { direito: number; declarados: number; fontes: FonteDeBoost[] };
  slots_abertos: SlotAberto[];
  slots: Record<string, number[]>;
  conjuracao: Conjuracao[];
  /** o que o personagem enxerga -- de `grants.sense`, que ninguém lia até 2026-07-29 */
  sentidos: Array<{ tipo: string | null; acuidade: string | null;
                    alcance: number | null; origem: string }>;
  atores: Ator[];
  concessoes_de_ator: ConcessaoDeAtor[];
  escolhas_de_feat: unknown;
  focus_pool: number;
  /** a divindade escolhida, com dominio e arma favorita ja resolvidos por nome */
  divindade: VisaoDeDivindade | null;
  ac: AC;
  /** por modo: `{land: 25, fly: 30}`. Spec `2026-07-30-velocidade.md` */
  velocidade: Record<string, number>;
  velocidade_detalhe: Array<Record<string, unknown>>;
  resistencias: LinhaDeResistencia[];
  fraquezas: LinhaDeResistencia[];
  imunidades: LinhaDeResistencia[];
  ataques: Ataque[];
  features: LinhaDeFeature[];
  concedidos: Concedido[];
  subclasses: SlotDeSubclasse[];
  fora_do_requisito: ForaDoRequisito[];
  avisos: string[];
}
