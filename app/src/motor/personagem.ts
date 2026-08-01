/**
 * Porte de `Personagem` em `motor/motor.py`: documento de personagem -> visão
 * calculada.
 *
 * O documento guarda **decisão**, nunca resultado. Tudo aqui é derivado e
 * descartável: some o motor, o personagem continua intacto no JSON.
 *
 * Regras implementadas (numeração da spec):
 *   1  nivel_de_personagem = SOMA(niveis_de_classe)
 *   3  bonus total = nivel_de_personagem + rank
 *   4  duas classes com a mesma proficiencia: vale o melhor rank
 *   5  class DC e por classe, com rank pelo nivel daquela classe
 *   7  nivel 1 de classe da o pacote cheio, de qualquer classe
 *   8  key ability boost e class feat de nivel 1 so da PRIMEIRA classe
 *   9  pericias automaticas da classe nova sao sempre concedidas
 *   10 escolhas livres por delta = max(0, orcamento(C) - livres_ja_concedidas)
 *   11 HP por nivel da classe que recebeu aquele nivel; ancestria no nivel 1
 *   12 class feat a cada nivel PAR de personagem
 *   14 cadencia basica segue o nivel de personagem
 *   16 slots e rank base vem do nivel de CLASSE cru
 *   17 elevacao: rank_efetivo = ceil(nivel_de_personagem / 2)
 *   18 elevacao nao vale para slots de arquetipo
 *   22 focus pool unico do personagem, teto 3
 *
 * Princípio zero: `requires` sugere, nunca bloqueia. O motor calcula e SINALIZA
 * o que está fora do requisito -- nunca recusa.
 *
 * Os nomes dos campos derivados são os MESMOS do Python (snake_case) de
 * propósito: `motor/fixtures/*.json` é o gabarito e as chaves de `extras` são
 * literalmente os atributos da classe Python. Renomear aqui quebraria a
 * rastreabilidade linha a linha, que é o que torna este porte verificável.
 */
import type { Base } from "./base.ts";
import type { ContextoDePredicado, ResultadoDeTermo } from "./predicado.ts";
import { avaliar as avaliarPredicado, comparar } from "./predicado.ts";
import type {
  AC, Ataque, Ator, AumentoDePericia, Candidato, Concedido, ConcessaoDeAtor,
  Conjuracao, DanoCondicional, DanoDecomposto, Documento, ForaDoRequisito,
  LinhaDeFeature, FonteDeBoost, ParcelaDeDano, Rank,
  BonusAplicado, DetalheDePericiaLivre, LinhaDePericia,
  LinhaDeResistencia, OpcaoDeGrant,
  Registro, SlotAberto, SlotConcedido, SlotDeSubclasse, Visao,
  VisaoDeDivindade,
} from "./tipos.ts";
import { ATRIBUTOS, RANKS } from "./tipos.ts";
import {
  RANK_BONUS, comSinal, dictDe, ehDict, ehInt, ehLista, ehStr,
  empurrar, indiceDeRank, inteiro, listaDe, melhorRank, melhorRankDe, nome, nomeOu,
  normChave, normSlug, obter, ordenarNumeros, ordenarPor, ordenarTextos,
  pyIterar, pyRepr, pyStr, somar, verdadeiro,
} from "./util.ts";

type Dict = Record<string, unknown>;

/** As quatro categorias que `weapon:*` varre. `unarmed` entra porque o RAW
 * trata ataque desarmado como proficiência de arma. */
const CATEGORIAS_DE_ARMA = ["simple", "martial", "advanced", "unarmed"];

/**
 * Cinto de segurança contra dado malformado, NÃO contra o jogador. Medido em
 * 2026-07-27 sobre os 19705 registros da base inteira: o grafo de
 * `grant_feat`/`grant_item` com alvo ESTÁTICO (sem uuid dinâmico `{...}`) não
 * tem NENHUM ciclo de 2+ nós, e a cadeia mais funda encontrada tem 3 nós. O
 * único padrão "circular" real são 31 registros que concedem A SI MESMOS (ex.:
 * `Rage`, `Hunt Prey` -- artefato do Foundry pra reaplicar o próprio efeito,
 * não um erro de dado), e esses já saem podados no primeiro passo porque a
 * origem entra em `visitados` antes de percorrer. Este teto é só a rede: se um
 * dado futuro formar uma cadeia mais funda, o motor CORTA e AVISA -- nunca
 * trava, nunca perde em silêncio.
 */
const MAX_PROFUNDIDADE_GRANTS = 8;

// as quatro do Remaster. Serve para separar tradição RESOLVIDA de prosa:
// Sorcerer, Summoner e Witch guardam a frase "variavel (definida pela escolha
// de ...)" no lugar do valor -- item 78.
const TRADICOES: string[] = ["arcane", "divine", "occult", "primal"];

/** Linha da lista de features, como o Python monta o dict. */
interface Feature extends LinhaDeFeature {
  grants: unknown[];
}

interface RegistroConcedido extends Feature {
  /** o que a cadeia concede sempre tem id -- é o alvo do `grant_feat` */
  id: string;
  nome: string;
  origem: string;
  concedido_por: string;
  raiz: string;
}

interface DetalheDeHP { origem: string | null; hp: number; nota: string }

function objetoDe<V>(m: Map<string, V>): Record<string, V> {
  const saida: Record<string, V> = {};
  for (const [k, v] of m) saida[k] = v;
  return saida;
}

export class Personagem implements ContextoDePredicado {
  readonly doc: Documento;
  readonly base: Base;
  avisos: string[] = [];

  // regra 1
  niveis_por_classe: Map<string, number> = new Map();
  ordem_de_classe: string[] = [];
  classe_do_nivel: Map<number, string> = new Map();
  nivel = 0;
  primeira_classe: string | null = null;
  entrada_da_classe: Map<string, number> = new Map();

  // identidade
  ancestria: Registro | null = null;
  heranca: Registro | null = null;
  background: Registro | null = null;

  // regra 7
  features: Feature[] = [];
  slots_de_subclasse: SlotDeSubclasse[] = [];

  // regras 3, 4, 5, 7, 9
  proficiencias: Map<string, Rank> = new Map();
  origem_proficiencia: Map<string, string[]> = new Map();
  /** expressão de proficiência que o resolvedor não conhece. Contada, nunca
   *  convertida em `untrained`. */
  proficiencia_ignorada: Record<string, number> = {};
  /** escolhas anotadas para um nível que o personagem ainda não tem */
  escolhas_de_nivel_futuro = 0;
  aplicacoes_de_proficiencia: Map<string, Array<[unknown, string | null]>> = new Map();
  pericias_automaticas: Map<string, string> = new Map();
  pericias_livres = 0;
  pericias_declaradas = 0;
  escolhas_de_grant: Array<{
    origem: string; nome: string; flag: string | null;
    opcoes: OpcaoDeGrant[]; escolhido: string | null;
  }> = [];
  pericias_livres_detalhe: DetalheDePericiaLivre[] = [];
  /** cache de `_remaps_de_arma`: `candidatos()` avalia milhares de feats por
   * slot, e varrer classes/features/feats a cada arma citada custaria caro. */
  private _remaps_cache: Array<[unknown, unknown]> | null = null;
  // memoizado porque a ultima linha ATRIBUI `bonus_ignorados` em vez de
  // acumular, e o terceiro chamador apagava o que os dois anteriores gravaram.
  private _bonusMemo: Map<string, BonusAplicado[]> | null = null;
  /** atomo de filtro de slot concedido que o avaliador nao conhece. Contado e
   *  nao silenciado, pela mesma razao de `bonus_ignorados`. */
  filtro_ignorado: Record<string, number> = {};
  slots_concedidos: SlotConcedido[] = [];
  pericias: LinhaDePericia[] = [];
  salvas: Record<string, LinhaDePericia> = {};
  bonus_ignorados: Record<string, number> = {};
  resistencias: LinhaDeResistencia[] = [];
  fraquezas: LinhaDeResistencia[] = [];
  imunidades: LinhaDeResistencia[] = [];
  velocidade: Record<string, number> = {};
  velocidade_detalhe: Dict[] = [];
  aumentos_de_pericia: number[] = [];
  aumentos_detalhe: AumentoDePericia[] = [];

  // regra 8
  boosts: Map<string, number> = new Map();
  origem_boost: string[] = [];
  boosts_pendentes: FonteDeBoost[] = [];
  boosts_direito = 0;
  boosts_declarados = 0;
  atributos: Record<string, number> = {};
  modificadores: Record<string, number> = {};

  // regra 11
  hp = 0;
  hp_detalhe: DetalheDeHP[] = [];

  // regras 12 e 14
  slots: Map<string, number[]> = new Map();
  class_feat_nivel_1 = false;
  gastos: Map<string, Dict[]> = new Map();

  // regras 16, 17, 18
  conjuracao: Conjuracao[] = [];

  // atores e resto
  atores: Dict[] = [];
  concessoes_de_ator: ConcessaoDeAtor[] = [];
  private _cache_sentidos: Map<string, Dict> | null = null;
  escolhas_de_feat: Dict[] = [];
  focus_pool = 0;
  ac: AC = {
    total: 0, armadura: null, categoria: "unarmored", rank: "untrained",
    detalhe: "", dex_perdida: 0, check_penalty: 0, escudo: null, bonus: [],
  };
  ataques: Ataque[] = [];
  fora_do_requisito: ForaDoRequisito[] = [];

  // cadeia de grants
  concedidos: RegistroConcedido[] = [];
  private _raizes: Map<string, string> = new Map();
  private _ja_tenho: Set<string> = new Set();
  /** estado opcional entre passos: o feat cujo requisito está sendo avaliado */
  private _avaliando: string | null = null;
  // o nível da escolha sob análise -- ver o recorte temporal em `_termo_has`
  private _avaliando_em: number | null = null;

  constructor(doc: Documento, base: Base) {
    this.doc = doc;
    this.base = base;
    this._derivar();
  }

  // -- escolhas -----------------------------------------------------------

  private _todas_escolhas(): Dict[] {
    return listaDe((this.doc as unknown as Dict)["escolhas"]).filter(ehDict);
  }

  private _escolhas(slot: string): Dict[] {
    return this._todas_escolhas().filter((e) => e["slot"] === slot);
  }

  private _derivar(): void {
    this._niveis_de_classe();
    this._ancestria_e_background();
    this._features_de_classe();
    // antes de `_proficiencias`: a cadeia de grants põe class-feature na lista
    // de features e feat na lista de feats efetivos, e as duas coisas são lidas
    // na derivação de proficiência, HP e requisito.
    this._grants_em_cadeia();
    // `_atributos` ANTES de `_proficiencias`: o orçamento de perícia é "N plus
    // your Intelligence modifier", e com a ordem antiga o INT ainda não existia
    // quando a conta era feita. Medido nos dois sentidos -- não há ciclo.
    // Spec: `specs/2026-07-30-int-no-orcamento-de-pericia.md`
    this._atributos();
    this._proficiencias();
    this._hp();
    this._slots_de_feat();
    this._conjuracao();
    this._focus();
    this._defesa();
    this._ataques();
    this._pericias_e_salvas();
    // `_atores` DEPOIS de `_defesa` e `_pericias_e_salvas`: a AC e os saves do
    // familiar são literalmente os do mestre ("equal to yours before applying
    // circumstance or status bonuses"), então ele os LÊ em vez de recalcular.
    // Na ordem antiga `this.ac` ainda não existia.
    this._atores();
    this._resistencias();
    this._velocidade();
    this._checar_requisitos();
  }

  // -- regra 1: estrutura -------------------------------------------------

  /** Regra 1: nível de personagem é a SOMA dos níveis de classe. */
  private _niveis_de_classe(): void {
    // ORDENAR POR NÍVEL, não pela ordem do array: a "primeira classe" de um
    // personagem é a que recebeu o NÍVEL 1, e não a que o jogador digitou
    // primeiro. Sem isto, reordenar o JSON muda `primeira_classe` e com ela a
    // regra 8 (o class feat de nível 1 só vem da primeira classe) -- a mesma
    // ficha derivava `slots['class'] = [1,2,4]` ou `[2,4]` conforme a ordem de
    // digitação. Achado pelo teste de embaralhamento, numa ficha multiclasse
    // (com classe única o defeito é invisível).
    const por_nivel = ordenarPor(this._escolhas("nivel_de_classe"),
                                 (e) => [ehInt(e["em"]) ? e["em"] : 0]);
    for (const e of por_nivel) {
      const cid = e["pega"];
      if (!ehStr(cid)) {
        this.avisos.push(`nivel_de_classe sem classe em \`pega\`: ${pyRepr(e)}`);
        continue;
      }
      if (this.base.opcional(cid) === null) {
        // barrar aqui é o que impede o id inválido de chegar nos passos
        // seguintes, que usam `base.get` e levantariam KeyError
        this.avisos.push(
          `nivel_de_classe aponta pra classe ausente da base: ${cid}`);
        continue;
      }
      const nivel_personagem = e["em"];
      if (!ehInt(nivel_personagem)) {
        this.avisos.push(`nivel_de_classe sem \`em\` numerico: ${pyRepr(e)}`);
        continue;
      }
      somar(this.niveis_por_classe, cid, 1);
      this.classe_do_nivel.set(nivel_personagem, cid);
      if (!this.ordem_de_classe.includes(cid)) this.ordem_de_classe.push(cid);
    }

    this.nivel = [...this.niveis_por_classe.values()].reduce((a, b) => a + b, 0);
    this.primeira_classe = this.ordem_de_classe[0] ?? null;

    // nível de PERSONAGEM em que cada classe entrou -- é o ponto de partida da
    // regra 15 (cadência extra só vale dali pra frente), usado tanto pelos
    // slots de feat quanto pelos aumentos de perícia
    for (const n of ordenarNumeros(this.classe_do_nivel.keys())) {
      const cid = this.classe_do_nivel.get(n) as string;
      if (!this.entrada_da_classe.has(cid)) this.entrada_da_classe.set(cid, n);
    }

    // sanidade: um nível de personagem, uma classe
    const vistos = new Set(this.classe_do_nivel.keys());
    const faltando: number[] = [];
    for (let n = 1; n <= this.nivel; n += 1) if (!vistos.has(n)) faltando.push(n);
    const sobrando = ordenarNumeros([...vistos].filter((n) => n < 1 || n > this.nivel));
    if (faltando.length > 0 || sobrando.length > 0) {
      if (faltando.length > 0) {
        this.avisos.push(
          `niveis de personagem sem classe atribuida: ${pyRepr(faltando)}`);
      }
      if (sobrando.length > 0) {
        this.avisos.push(`niveis fora da faixa 1..${this.nivel}: ${pyRepr(sobrando)}`);
      }
    }
  }

  nivel_de(classe_id: string): number {
    return this.niveis_por_classe.get(classe_id) ?? 0;
  }

  // -- ancestralidade, herança, background --------------------------------

  private _ancestria_e_background(): void {
    const um = (slot: string): Registro | null => {
      const esc = this._escolhas(slot);
      return esc.length > 0 ? this.base.opcional(esc[0]["pega"]) : null;
    };
    this.ancestria = um("ancestralidade");
    this.heranca = um("heranca");
    this.background = um("background");
    for (const [rotulo, reg] of [["ancestralidade", this.ancestria],
                                 ["background", this.background]] as const) {
      if (reg === null) this.avisos.push(`sem ${rotulo} escolhida`);
    }
  }

  // -- regra 7: identidade de classe --------------------------------------

  /**
   * Regra 7: o nível de classe compra IDENTIDADE, e ela vem inteira.
   *
   * É o argumento central da houserule: gastar nível de classe vale a pena
   * porque compra identidade, e nenhuma dedicação compra identidade íntegra.
   * Se as features não aparecem na ficha, a regra fica sem efeito visível.
   *
   * A progressão já vem separada em concedido vs escolhido: sem isso um Mago 1
   * receberia as 23 escolas de magia de uma vez.
   */
  private _features_de_classe(): void {
    const escolhidas = new Set(this._escolhas("subclasse").map((e) => e["pega"]));

    for (const cid of this.ordem_de_classe) {
      const classe = this.base.get(cid);
      const nivel_classe = this.nivel_de(cid);

      for (const p of listaDe(classe["progressao"])) {
        const passo = dictDe(p);
        // regra 16/7: a feature vem pelo nível DA CLASSE
        if (inteiro(passo["nivel"]) > nivel_classe) continue;
        const fid = obter(passo, "concede");
        const feature = this.base.opcional(fid);
        this.features.push({
          id: ehStr(fid) ? fid : null,
          nome: nomeOu(feature, pyStr(fid)),
          classe: nomeOu(classe, cid),
          nivel_de_classe: ehInt(passo["nivel"]) ? passo["nivel"] : null,
          grants: listaDe((feature ?? {})["grants"]),
          na_base: feature !== null,
        });
      }

      for (const b of listaDe(classe["subclasses"])) {
        const bloco = dictDe(b);
        const nivel_bloco = Object.hasOwn(bloco, "nivel") && verdadeiro(bloco["nivel"])
          ? inteiro(bloco["nivel"]) : 1;
        if (nivel_bloco > nivel_classe) continue;
        // eixo CONDICIONAL: quando todas as opções pedem a mesma sub-escolha, a
        // condição é do EIXO. Um Mago de Abjuração não tem um eixo de pecado
        // thassiloniano com tudo marcado -- ele NÃO TEM o eixo, e avisar "falta
        // escolher" seria ruído.
        // Spec: `specs/2026-07-31-escolha-aninhada-do-inventor.md`
        if (verdadeiro(bloco["requires"]) && !this.avaliar(bloco["requires"])[0]) {
          continue;
        }
        const opcoes = listaDe(bloco["opcoes"]);
        // `escolhe` existe no schema desde sempre e até 30/07 TODOS os 52
        // blocos usavam 1 -- o motor nem lia o campo. O eixo de ikon do
        // Exemplar é o primeiro com 3 ("Select three ikons", prosa oficial), e
        // pegar só a primeira perderia duas em SILÊNCIO.
        // Spec: specs/2026-07-30-escolha-multipla-e-ikons.md
        const quantas = Math.max(1, inteiro(bloco["escolhe"] ?? 1) || 1);
        const escolhidosDoBloco = opcoes.filter((o) => escolhidas.has(o))
                                        .filter(ehStr);
        const escolha = escolhidosDoBloco.length ? escolhidosDoBloco[0] : null;
        const reg = escolha === null ? null : this.base.opcional(escolha);
        this.slots_de_subclasse.push({
          classe: nomeOu(classe, cid),
          eixo: ehStr(bloco["eixo"]) ? bloco["eixo"] : null,
          nivel: ehInt(bloco["nivel"]) ? bloco["nivel"] : null,
          escolhe: quantas,
          escolhidos: escolhidosDoBloco,
          // a CONTAGEM acompanha `opcoes_ids`: no eixo por query a lista crua
          // é vazia de propósito, e a tela mostrava "0 opções" com 6 na frente.
          opcoes: opcoes.length > 0
            ? opcoes.length
            : this._ids_por_filtro(bloco["filtro"]).length,
          // a LISTA, alem da contagem: `candidatos("subclasse")` precisa dos
          // ids. Ate 2026-07-28 o Python iterava `opcoes` -- que e um int --
          // e levantava TypeError; nao explodia so porque nenhuma ficha de
          // exemplo exercitava o slot, e foi este porte que trouxe o caso a
          // tona.
          // eixo por QUERY: a base guarda o FILTRO em vez da lista, porque
          // congelar no build dessincroniza na primeira mudança de fonte. Quem
          // resolve é o MOTOR, aqui -- assim a tela continua consumindo
          // `opcoes_ids` sem saber que existe query.
          // Spec: `specs/2026-07-31-tag-e-eixo-por-query.md`
          opcoes_ids: opcoes.filter(ehStr).length > 0
            ? opcoes.filter(ehStr)
            : this._ids_por_filtro(bloco["filtro"]),
          filtro: bloco["filtro"] ?? null,
          escolhido: ehStr(escolha) ? escolha : null,
          nome: escolha === null ? null : nome(reg),
        });
        const faltamSub = quantas - escolhidosDoBloco.length;
        if (faltamSub > 0) {
          const quanto = quantas === 1
            ? `(${opcoes.length} opcoes)`
            : `(${faltamSub} de ${quantas})`;
          this.avisos.push(
            `${pyStr(nome(classe))}: falta escolher \`${pyStr(obter(bloco, "eixo"))}\` `
            + quanto);
        } else if (faltamSub < 0) {
          // escolha demais NÃO é corrigida: o motor diz, e não apaga.
          this.avisos.push(
            `${pyStr(nome(classe))}: \`${pyStr(obter(bloco, "eixo"))}\` tem `
            + `${escolhidosDoBloco.length} escolhas para ${quantas} vaga(s)`);
        }
        for (const pego of escolhidosDoBloco) {
          const r = this.base.opcional(pego);
          if (r === null) continue;
          this.features.push({
            id: pego,
            nome: nomeOu(r, pyStr(pego)),
            classe: nomeOu(classe, cid),
            nivel_de_classe: ehInt(bloco["nivel"]) ? bloco["nivel"] : null,
            grants: listaDe(r["grants"]),
            na_base: true,
            eixo: ehStr(bloco["eixo"]) ? bloco["eixo"] : null,
          });
        }
      }
    }
  }

  // -- regras 3, 4, 5, 7, 9: proficiências --------------------------------

  /**
   * Cada aplicação guarda o id de QUEM aplicou. É o que permite perguntar
   * depois "qual seria o rank sem este feat?" -- sem isso, um feat que concede
   * a mesma perícia que exige satisfaz o próprio requisito.
   */
  private _aplicar_proficiencia(chave: string, rank: unknown, origem: string,
                                origem_id: string | null = null): void {
    if (!RANKS.includes(rank as Rank)) {
      // 47 dos 1.071 valores de `proficiency` são expressão do VTT, e
      // `melhorRank` as rebaixava a `untrained` em silêncio -- um Azarketi
      // Guerreiro 13 saía untrained nas armas que o feat existe para elevar a
      // master. `untrained` errado é pior que ausência: é uma AFIRMAÇÃO.
      // Spec: `specs/2026-07-30-proficiencia-por-expressao.md`
      const resolvido = this._rank_de_expressao(rank);
      if (resolvido === null) return;
      rank = resolvido;
    }
    const anterior = this.proficiencias.get(chave);
    const novo = melhorRank(anterior, rank);
    this.proficiencias.set(chave, novo);
    empurrar(this.aplicacoes_de_proficiencia, chave, [rank, origem_id]);
    if (novo === rank && rank !== anterior) {
      this.origem_proficiencia.set(chave, [origem]);
    } else if (rank === novo) {
      empurrar(this.origem_proficiencia, chave, origem);
    }
  }

  /**
   * Regras 7 e 4: pacote cheio de cada classe, melhor rank entre elas.
   *
   * Regra 7 é deliberada e cara: nível 1 de QUALQUER classe entrega saves,
   * Percepção, armas e armadura completos. Um Monge 1 / Guerreiro 1 no nível 2
   * tem o melhor perfil defensivo do jogo -- aceito de olho aberto, porque o
   * nível fica gasto para sempre.
   */
  private _proficiencias(): void {
    for (const cid of this.ordem_de_classe) {
      const classe = this.base.get(cid);
      for (const g of this._grants_de(classe)) {
        if (ehDict(g) && Object.hasOwn(g, "proficiency")) {
          for (const [chave, rank] of Object.entries(dictDe(g["proficiency"]))) {
            this._aplicar_proficiencia(chave, rank, nomeOu(classe, cid), cid);
          }
        }
      }
    }

    // as features de identidade também elevam rank (Weapon Mastery, Expert
    // Spellcaster, Reflex Expertise...). Sem isto a regra 7 entrega a feature
    // na lista e não no número.
    for (const f of this.features) {
      for (const g of f.grants) {
        if (ehDict(g) && Object.hasOwn(g, "proficiency")) {
          for (const [chave, rank] of Object.entries(dictDe(g["proficiency"]))) {
            const de = verdadeiro(f.classe) ? f.classe : obter(f as unknown as Dict, "origem");
            const raiz = (f as unknown as Dict)["raiz"];
            this._aplicar_proficiencia(chave, rank, `${pyStr(f.nome)} (${pyStr(de)})`,
                                       verdadeiro(raiz) ? String(raiz) : f.id);
          }
        }
      }
    }

    // feat também eleva rank -- é a lacuna que deixava toda dedicação inerte.
    // `wizard-dedication` é `{proficiency: {arcana: trained}}`, exatamente a
    // mesma chave plana que classe e feature já usavam; são 342 feats com
    // `proficiency`, 72 deles dedicações.
    for (const [wb_id, feat, por] of this._feats_efetivos()) {
      let rotulo = nomeOu(feat, wb_id);
      if (verdadeiro(por)) rotulo = `${rotulo} (via ${pyStr(por)})`;
      // a RAIZ da cadeia, não o elo: se a dedicação X concedeu o feat Y, o que
      // Y aplica tem de ser descontado ao avaliar o requisito de X
      const raiz = this._raiz_de(wb_id);
      for (const g of this._grants_de(feat)) {
        if (!ehDict(g)) continue;
        for (const [chave, rank] of Object.entries(dictDe(g["proficiency"]))) {
          this._aplicar_proficiencia(chave, rank, rotulo, raiz);
        }
        for (const pericia of listaDe(dictDe(g["skill_training"])["auto"])) {
          this._aplicar_proficiencia(String(pericia), "trained", rotulo, raiz);
        }
      }
    }

    // regra 9: perícia automática da classe é identidade, sempre concedida
    for (const cid of this.ordem_de_classe) {
      const classe = this.base.get(cid);
      for (const g of this._grants_de(classe)) {
        for (const pericia of listaDe(dictDe(dictDe(g)["skill_training"])["auto"])) {
          this.pericias_automaticas.set(String(pericia), nomeOu(classe, cid));
          this._aplicar_proficiencia(String(pericia), "trained", nomeOu(classe, cid));
        }
      }
    }

    // background treina perícia também
    if (this.background !== null) {
      const treino = dictDe(this.background["skill_training"]);
      for (const pericia of listaDe(treino["skills"])) {
        this._aplicar_proficiencia(String(pericia), "trained",
                                   nomeOu(this.background, "background"));
      }
      for (const lore of listaDe(treino["lore"])) {
        this._aplicar_proficiencia(`lore:${pyStr(lore)}`, "trained",
                                   nomeOu(this.background, "background"));
      }
    }

    // regra 10: orçamento de perícia livre, por delta
    this._orcamento_de_pericia();
    this._gastar_pericias_livres();
    this._escolhas_de_grant();
    // o aumento de perícia por nível -- que todo personagem faz e o motor não
    // implementava
    this._aumentos_de_pericia();
  }

  /** teto RAW do aumento de perícia, por nível de PERSONAGEM */
  static readonly TETO_DE_RANK: Array<[number, Rank]> = [
    [15, "legendary"], [7, "master"], [1, "expert"],
  ];

  /**
   * Skill increase: sobe UM degrau numa perícia, nos níveis que a classe
   * declara.
   *
   * A cadência vem do dado, nunca de tabela escrita aqui: as 27 classes da base
   * declaram `{levels: [...]}` -- 25 no padrão [3,5,..,19] e 2 (Ladino e
   * Investigador) em todo nível de 2 a 20. Vale a regra 15: a cadência de uma
   * classe conta a partir do nível de personagem em que ela entrou.
   */
  private _aumentos_de_pericia(): void {
    const niveis = new Set<number>();
    for (const [cid, desde] of this.entrada_da_classe) {
      for (const g of this._grants_de(this.base.get(cid))) {
        if (!ehDict(g) || !Object.hasOwn(g, "skill_increase")) continue;
        for (const n of listaDe(dictDe(g["skill_increase"])["levels"])) {
          const v = inteiro(n);
          if (desde <= v && v <= this.nivel) niveis.add(v);
        }
      }
    }
    this.aumentos_de_pericia = ordenarNumeros(niveis);

    // o default importa: nível 0 é o ESTADO INICIAL do construtor (ainda sem
    // classe), e sem ele o `next` estoura StopIteration e o motor inteiro morre
    // antes de derivar qualquer coisa
    const teto: Rank = Personagem.TETO_DE_RANK.find(
      ([n]) => this.nivel >= n)?.[1] ?? "trained";
    // o recorte vale para a CHECAGEM e para a APLICAÇÃO: um Guerreiro 4 com
    // aumento anotado para o nível 8 ficava `trained` na perícia -- rank que
    // ele não tem. `_atributos` já não aplicava o boost futuro.
    // Spec: `specs/2026-07-30-escolha-de-nivel-futuro.md`
    const escolhas = ordenarPor(
      this._escolhas("skill_increase").filter((e) => !this._e_plano(e["em"])),
      (e) => [ehInt(e["em"]) ? e["em"] : 0]);

    if (escolhas.length > this.aumentos_de_pericia.length) {
      this.avisos.push(
        `skill_increase: ${escolhas.length} aumento(s) escolhido(s) para `
        + `${this.aumentos_de_pericia.length} disponivel(is) em `
        + `${pyRepr(this.aumentos_de_pericia)}`);
    }

    for (const e of escolhas) {
      const em = obter(e, "em");
      if (ehInt(em) && !this.aumentos_de_pericia.includes(em)) {
        this.avisos.push(
          `skill_increase: aumento no nivel ${em}, que nao tem aumento `
          + `(niveis validos: ${pyRepr(this.aumentos_de_pericia)})`);
      }
      const pegas = ehLista(e["pega"]) ? e["pega"] : [obter(e, "pega")];
      for (const pericia of pegas) {
        if (!ehStr(pericia)) continue;
        // sem esta checagem, um nome errado vira uma linha de proficiência
        // FANTASMA na ficha, sem nada apontando o erro. `lore:<algo>` é
        // legítimo -- Lore é aberto por definição.
        if (!pericia.startsWith("lore:")
            && this.base.opcional(`wb:skill/${normSlug(pericia)}`) === null) {
          this.avisos.push(
            `skill_increase: \`${pericia}\` nao e uma pericia da base `
            + `-- aumento aplicado assim mesmo, confira o nome`);
        }
        const atual = this.proficiencias.get(pericia) ?? "untrained";
        let proximo = RANKS[Math.min(indiceDeRank(atual) + 1, RANKS.length - 1)];
        if (indiceDeRank(proximo) > indiceDeRank(teto)) {
          this.avisos.push(
            `skill_increase: ${pericia} iria a ${proximo}, acima do teto `
            + `${teto} do nivel ${this.nivel}`);
          proximo = teto;
        }
        this._aplicar_proficiencia(pericia, proximo, `aumento de pericia (nivel ${pyStr(em)})`);
        this.aumentos_detalhe.push({
          nivel: em as number | "criacao" | null, pericia, de: atual, para: proximo,
        });
      }
    }
  }

  /**
   * Regra 10: delta = max(0, orçamento(C) - livres_já_concedidas).
   *
   * O `max` é o que torna a ordem das classes irrelevante para o total, e o que
   * impede o multiclasse de multiplicar orçamento de perícia. As automáticas da
   * regra 9 não entram na conta dos dois lados.
   */
  /** `@actor.system.proficiencies.<grupo>.<chave>.rank` -> a nossa chave. */
  private static CHAVE_DO_VTT: Record<string, string> = {
    "attacks.unarmed": "unarmed", "attacks.simple": "simple",
    "attacks.martial": "martial", "attacks.advanced": "advanced",
    "defenses.unarmored": "unarmored", "defenses.light": "light",
    "defenses.medium": "medium", "defenses.heavy": "heavy",
  };

  /**
   * Rank vindo de expressão do VTT, ou `null` quando não dá para saber.
   *
   * `null` é deliberado e NÃO é `untrained`: ausência faz a tela perguntar,
   * `untrained` faz o jogador atacar com o número errado. Mesma escolha do
   * `_resolver_valor` das resistências, que devolve `null` em vez de zero.
   *
   * Spec: `specs/2026-07-30-proficiencia-por-expressao.md`
   */
  private _rank_de_expressao(valor: unknown): Rank | null {
    if (ehInt(valor)) return (valor >= 0 && valor < RANKS.length) ? RANKS[valor] : null;
    if (!ehStr(valor)) {
      const k = pyStr(valor);
      this.proficiencia_ignorada[k] = (this.proficiencia_ignorada[k] ?? 0) + 1;
      return null;
    }
    const texto = valor.trim();
    if (RANKS.includes(texto as Rank)) return texto as Rank;

    let m = /^@actor\.system\.proficiencies\.([\w.]+)\.rank$/.exec(texto);
    if (m) {
      const chave = Personagem.CHAVE_DO_VTT[m[1]];
      return chave ? (this.proficiencias.get(chave) ?? null) : null;
    }

    m = /^max\((.+)\)$/.exec(texto);
    if (m) {
      const vivos = m[1].split(",")
        .map((x) => this._rank_de_expressao(x.trim()))
        .filter((x): x is Rank => x !== null);
      return vivos.length > 0 ? melhorRankDe(vivos) : null;
    }

    m = /^ternary\(gte\(@actor\.level,(\d+)\),(.+?),(.+)\)$/.exec(texto);
    if (m) {
      const ramo = (this.nivel >= Number(m[1]) ? m[2] : m[3]).trim();
      return this._rank_de_expressao(/^\d+$/.test(ramo) ? Number(ramo) : ramo);
    }

    this.proficiencia_ignorada[texto] = (this.proficiencia_ignorada[texto] ?? 0) + 1;
    return null;
  }

  private _orcamento_de_pericia(): void {
    let concedidas = 0;
    const detalhe: DetalheDePericiaLivre[] = [];
    for (const cid of this.ordem_de_classe) {
      const classe = this.base.get(cid);
      let livre = 0;
      for (const g of this._grants_de(classe)) {
        livre = Math.max(livre, inteiro(dictDe(dictDe(g)["skill_training"])["free"]));
      }
      // "a number of additional skills equal to N plus your Intelligence
      // modifier" -- a prosa de cada classe. O INT entra UMA vez por
      // personagem: somar em cada classe daria a um Mago 3/Ladino 3 o dobro.
      if (cid === this.primeira_classe) {
        livre = Math.max(0, livre + (this.modificadores["int"] ?? 0));
      }
      const delta = Math.max(0, livre - concedidas);
      concedidas += delta;
      detalhe.push({ classe: nomeOu(classe, cid), orcamento: livre, delta });
    }

    // feat que treina perícia a escolher SOMA (não entra no max da regra 10,
    // que existe só pra impedir o multiclasse de multiplicar o orçamento das
    // CLASSES). São 37 feats, entre eles dedicações como `battle-harbinger`.
    for (const [wb_id, feat] of this._feats_efetivos()) {
      for (const g of this._grants_de(feat)) {
        if (!ehDict(g)) continue;
        const livre = inteiro(dictDe(g["skill_training"])["free"]);
        if (livre) {
          concedidas += livre;
          detalhe.push({ classe: nomeOu(feat, wb_id), orcamento: livre, delta: livre });
        }
      }
    }

    this.pericias_livres = concedidas;
    this.pericias_livres_detalhe = detalhe;
  }

  /**
   * Aplica as perícias que o JOGADOR escolheu, e cobra o que falta.
   *
   * Até 2026-07-29 o orçamento era calculado (`pericias_livres: 3` aparecia na
   * ficha) e **nunca gasto**: não existia escolha de `pericias_livres` em lugar
   * nenhum do motor. Todo personagem saía sem nenhuma perícia treinada por
   * escolha, nas 27 classes, que dão de 2 a 7.
   *
   * Spec: `specs/2026-07-29-pericias-livres.md`
   */
  private _gastar_pericias_livres(): void {
    const escolhidas: string[] = [];
    for (const e of this._escolhas("pericias_livres")) {
      const em = obter(e, "em");
      if (ehInt(em) && em > this.nivel) continue;   // escolha de nível futuro
      const pegas = ehLista(e["pega"]) ? e["pega"] : [obter(e, "pega")];
      for (const p of pegas) if (ehStr(p)) escolhidas.push(p);
    }

    for (const p of escolhidas) {
      // regra 9: perícia que a classe já dá de graça. Aplicar não rebaixa (a
      // regra 4 mantém o melhor rank), mas a escolha foi jogada fora -- e na
      // mesa o mestre manda escolher outra. Avisa, não reprova.
      const automatica = this.pericias_automaticas.get(p);
      if (verdadeiro(automatica)) {
        this.avisos.push(
          `pericias livres: \`${p}\` ja vem da classe (${automatica}) `
          + "-- escolha desperdicada");
      }
      this._aplicar_proficiencia(p, "trained", "escolha do jogador");
    }

    this.pericias_declaradas = escolhidas.length;
    if (this.pericias_declaradas < this.pericias_livres) {
      const faltam = this.pericias_livres - this.pericias_declaradas;
      this.avisos.push(
        `pericias livres: ${this.pericias_declaradas} declarada(s) de `
        + `${this.pericias_livres} a que o personagem tem direito -- `
        + `faltam ${faltam}`);
    } else if (this.pericias_declaradas > this.pericias_livres) {
      this.avisos.push(
        `pericias livres: ${this.pericias_declaradas} declarada(s) para `
        + `${this.pericias_livres} de direito -- sobra `
        + `${this.pericias_declaradas - this.pericias_livres}`);
    }
  }

  /**
   * Escolha embutida em `grants` -- ex: Marshal Dedication, que dá UMA entre
   * Diplomacy e Intimidation.
   *
   * Até 2026-07-29 o extrator guardava só a CONTAGEM de opções e soltava as
   * consequências ao lado, então o personagem recebia TODAS. Agora as opções vêm
   * aninhadas com os grants de cada uma (spec `2026-07-29-choiceset.md`).
   *
   * ESTA FATIA SÓ MARCA -- o que a opção concede ainda não é aplicado, porque
   * `grants` é lido em 14 pontos do motor. Marcar antes de aplicar é
   * deliberado: sem isso a escolha sumiria em silêncio.
   */
  /**
   * Os grants de um registro, com a escolha do jogador já resolvida.
   *
   * Um `grants` pode conter `{"choice": {"flag": ..., "opcoes": [...]}}`, e cada
   * opção carrega os grants que dependem DELA (spec `2026-07-29-choiceset.md`).
   * Antes disso as consequências ficavam soltas na raiz e o personagem recebia
   * TODAS as opções -- Marshal Dedication dava Diplomacy E Intimidation.
   *
   * O marcador `choice` PERMANECE na lista, porque é ele que `slots_abertos`
   * usa para oferecer o picker. Sem escolha declarada, NENHUMA opção é aplicada.
   */
  private _grants_de(reg: Dict | null | undefined): unknown[] {
    const grants = listaDe(dictDe(reg)["grants"]);
    if (!grants.some((g) => "choice" in dictDe(g))) return grants;
    const escolhidos = new Set<string>();
    for (const e of this._escolhas("escolha_de_grant")) {
      if (ehStr(e["pega"])) escolhidos.add(e["pega"]);
    }
    const saida: unknown[] = [];
    for (const g of grants) {
      saida.push(g);
      const dict = dictDe(g);
      if (!("choice" in dict)) continue;
      const escolha = dictDe(dict["choice"]);
      const opcoes = escolha["opcoes"];
      if (!ehLista(opcoes)) continue;
      for (const o of opcoes) {
        const op = dictDe(o);
        if (escolhidos.has(`${pyStr(escolha["flag"])}:${pyStr(op["valor"])}`)) {
          for (const x of listaDe(op["grants"])) saida.push(x);
        }
      }
    }
    return saida;
  }

  private _escolhas_de_grant(): void {
    this.escolhas_de_grant = [];
    const vistos = new Set<string>();
    const fontes: Array<[string, string, unknown[]]> = [];
    for (const f of this.features) {
      fontes.push([pyStr(f["id"]), pyStr(f["nome"]), listaDe(f["grants"])]);
    }
    for (const [i, feat] of this._feats_efetivos()) {
      fontes.push([i, nomeOu(feat, i), listaDe(feat["grants"])]);
    }
    for (const [origem_id, nome, grants] of fontes) {
      for (const g of grants) {
        const dict = dictDe(g);
        if (!("choice" in dict)) continue;
        const escolha = dictDe(dict["choice"]);
        const opcoesCruas = escolha["opcoes"];
        if (!ehLista(opcoesCruas)) continue;   // forma resumida: nada a escolher
        // Medido na base inteira: a opção tem `{rotulo, valor}` em texto nas
        // 570, e 56 delas trazem TAMBÉM `grants` -- as consequências aninhadas,
        // que são justamente o que faz escolher a opção mudar número na ficha.
        // Reconstruir só rotulo/valor as apagava, e o gabarito do Python
        // acusou em quatro fichas. `flag` é texto ou nulo (292 e 2).
        const opcoes: OpcaoDeGrant[] = opcoesCruas.map((o) => {
          const d = dictDe(o);
          const op: OpcaoDeGrant = { rotulo: pyStr(d["rotulo"]), valor: pyStr(d["valor"]) };
          if ("grants" in d) op.grants = listaDe(d["grants"]);
          return op;
        });
        // o valor CRU vai para a saída (pode ser null, e o Python emite null);
        // a versão em texto só serve para montar chave e mensagem, onde o
        // Python interpola `None`. Trocar um pelo outro quebra a paridade.
        const flag = ehStr(escolha["flag"]) ? escolha["flag"] : null;
        const flagTexto = pyStr(flag);
        const chave = `${origem_id}:${flagTexto}`;
        if (vistos.has(chave)) continue;
        vistos.add(chave);
        let escolhido: string | null = null;
        for (const e of this._escolhas("escolha_de_grant")) {
          const pega = e["pega"];
          if (ehStr(pega) && pega.startsWith(`${flagTexto}:`)) { escolhido = pega; break; }
        }
        this.escolhas_de_grant.push(
          { origem: origem_id, nome, flag, opcoes, escolhido });
        if (escolhido === null) {
          const rotulos = opcoes
            .map((o) => pyStr(dictDe(o)["rotulo"] ?? dictDe(o)["valor"]))
            .join(", ");
          this.avisos.push(`${nome}: falta escolher \`${flagTexto}\` (${rotulos})`);
        }
      }
    }
  }

  // -- regra 8: atributos -------------------------------------------------

  /**
   * Os boosts livres do PF2e que NÃO vêm de `grants` -- são regra fixa do
   * sistema, iguais para toda classe, e por isso nenhum registro os declara.
   *
   * Na CRIAÇÃO são 4, aplicados depois de ancestria, background e classe
   * ("Step 6: Finish Attribute Modifiers"). Foi a parte que faltou na primeira
   * versão deste orçamento: sem eles o motor acusava "6 declarados de 5 de
   * direito" numa ficha que na verdade tinha direito a 9, e o aviso saía
   * invertido -- apontando excesso onde faltava.
   *
   * Depois, 4 a cada 5 níveis.
   */
  static readonly BOOSTS_DE_CRIACAO = 4;
  static readonly NIVEIS_DE_BOOST = [5, 10, 15, 20];
  static readonly BOOSTS_POR_NIVEL = 4;

  /** Regra 8: o boost de habilidade-chave vem SÓ da primeira classe. */
  private _atributos(): void {
    const aplicar_boosts = (lista: unknown, origem: string,
                            origem_id: string | null = null): void => {
      for (const b of listaDe(lista)) {
        const ab = ehDict(b) ? b["ability_boost"] : null;
        if (!verdadeiro(ab)) continue;
        const d = dictDe(ab);
        if (verdadeiro(d["livre"])) {
          const qtd = Object.hasOwn(d, "quantidade") ? inteiro(d["quantidade"]) : 1;
          this.origem_boost.push(`${origem}: ${qtd} livre(s)`);
          this.boosts_pendentes.push(
            { origem, origem_id, quantidade: qtd, opcoes: null, em: "criacao" });
          continue;
        }
        const opcoes = listaDe(d["opcoes"]).map(String);
        const qtd = Object.hasOwn(d, "quantidade") ? inteiro(d["quantidade"]) : 1;
        if (opcoes.length === 1) {
          somar(this.boosts, opcoes[0], qtd);
          this.origem_boost.push(`${origem}: +${opcoes[0]}`);
        } else {
          this.origem_boost.push(`${origem}: escolha entre ${pyRepr(opcoes)}`);
          this.boosts_pendentes.push(
            { origem, origem_id, quantidade: qtd, opcoes, em: "criacao" });
        }
      }
    };

    if (this.ancestria !== null) {
      aplicar_boosts(this.ancestria["boosts"], nomeOu(this.ancestria, "ancestria"));
      // `flaw` vem como DICT (`{"ability_flaw": {...}}`), não como lista.
      // Iterar um dict entrega as chaves -- strings --, o isinstance reprovava
      // e o defeito era descartado em silêncio. Achado ao comparar com os
      // iconics: todo personagem de ancestria com defeito de CON saía com 1
      // ponto de modificador a mais, e portanto `nivel` HP a mais.
      const bruto = this.ancestria["flaw"];
      const defeitos = ehDict(bruto) ? [bruto] : listaDe(bruto);
      for (const f of defeitos) {
        const ab = ehDict(f) ? f["ability_flaw"] : null;
        for (const op of listaDe(dictDe(ab)["opcoes"])) {
          somar(this.boosts, String(op), -1);
          this.origem_boost.push(
            `${pyStr(nome(this.ancestria))}: -${String(op)} (defeito)`);
        }
      }
    }
    if (this.background !== null) {
      aplicar_boosts(this.background["boosts"], nomeOu(this.background, "background"));
    }

    // regra 8: SÓ a primeira classe dá o boost de habilidade-chave
    if (this.primeira_classe !== null) {
      const classe = this.base.get(this.primeira_classe);
      const chaves = listaDe(classe["key_ability"]).map(String);
      if (chaves.length === 1) {
        somar(this.boosts, chaves[0], 1);
        this.origem_boost.push(`${pyStr(nome(classe))} (1a classe): +${chaves[0]}`);
      } else if (chaves.length > 0) {
        this.origem_boost.push(
          `${pyStr(nome(classe))} (1a classe): escolha entre ${pyRepr(chaves)}`);
        this.boosts_pendentes.push({
          origem: `${pyStr(nome(classe))} (habilidade-chave)`,
          origem_id: this.primeira_classe, quantidade: 1, opcoes: chaves, em: 1,
        });
      }
    }
    for (const cid of this.ordem_de_classe.slice(1)) {
      const classe = this.base.get(cid);
      this.origem_boost.push(
        `${pyStr(nome(classe))}: SEM boost de chave (regra 8 -- so a 1a classe)`);
    }

    // Boosts livres declarados no documento, **só até o nível atual**.
    // O documento pode carregar escolha de nível futuro -- planejamento de
    // progressão é caso normal, e o schema guarda decisão, não resultado.
    // Aplicar tudo faz um personagem de nível 3 andar com os atributos de nível
    // 5: achado comparando com os iconics, cujo arquivo de nível 3 já traz os
    // boosts do 5.
    for (const e of this._escolhas("boosts_livres")) {
      const quando = obter(e, "em");
      if (ehInt(quando) && quando > this.nivel) {
        this.avisos.push(
          `boosts de nivel ${quando} ignorados -- personagem tem nivel ${this.nivel}`);
        continue;
      }
      for (const atributo of pyIterar(e["pega"])) {
        somar(this.boosts, String(atributo), 1);
        this.origem_boost.push(`nivel ${pyStr(quando)}: +${String(atributo)} (livre)`);
      }
    }

    this._orcamento_de_boost();

    this.atributos = {};
    this.modificadores = {};
    for (const a of ATRIBUTOS) this.atributos[a] = 10 + 2 * (this.boosts.get(a) ?? 0);
    // `//` do Python trunca para -infinito. `Math.trunc` NÃO faz isso, e
    // atributo abaixo de 10 é caso real (defeito de ancestria).
    for (const a of ATRIBUTOS) this.modificadores[a] = Math.floor((this.atributos[a] - 10) / 2);
  }

  /**
   * Quantos boosts o personagem tem DIREITO contra quantos declarou.
   *
   * Mesma forma da higiene de slot e do orçamento de perícia: o motor já sabia
   * LER cada fonte de boost, mas nunca somava o direito nem confrontava com o
   * gasto. Resultado: ficha sem `boosts_livres` saía com tudo 10 e a suíte
   * inteira verde.
   */
  private _orcamento_de_boost(): void {
    this.boosts_pendentes.push({
      origem: "criacao (4 livres)", origem_id: null,
      quantidade: Personagem.BOOSTS_DE_CRIACAO, opcoes: null, em: "criacao",
    });
    for (const n of Personagem.NIVEIS_DE_BOOST) {
      if (n <= this.nivel) {
        this.boosts_pendentes.push({
          origem: `nivel ${n}`, origem_id: null,
          quantidade: Personagem.BOOSTS_POR_NIVEL, opcoes: null, em: n,
        });
      }
    }

    const direito = this.boosts_pendentes.reduce((s, b) => s + b.quantidade, 0);
    let declarado = 0;
    for (const e of this._escolhas("boosts_livres")) {
      const em = e["em"];
      if (ehInt(em) && em > this.nivel) continue;
      // `len(e.get("pega") or [])`: em string o Python conta CARACTERES
      declarado += pyIterar(e["pega"]).length;
    }

    this.boosts_direito = direito;
    this.boosts_declarados = declarado;
    if (declarado < direito) {
      const faltam = direito - declarado;
      const de_onde = this.boosts_pendentes
        .map((b) => `${b.origem} (${b.quantidade})`).join(", ");
      this.avisos.push(
        `boosts de atributo: ${declarado} declarado(s) de ${direito} a que o `
        + `personagem tem direito -- faltam ${faltam}. Fontes: ${de_onde}`);
    } else if (declarado > direito) {
      this.avisos.push(
        `boosts de atributo: ${declarado} declarado(s) para ${direito} de `
        + `direito -- ${declarado - direito} a mais`);
    }
  }

  // -- regra 11: HP -------------------------------------------------------

  /** Regra 11: HP por nível vem da classe que recebeu AQUELE nível. */
  private _hp(): void {
    let total = 0;
    if (this.ancestria !== null) {
      const hp_anc = inteiro(this.ancestria["hp"]);
      total += hp_anc;
      this.hp_detalhe.push(
        { origem: nome(this.ancestria), hp: hp_anc, nota: "ancestria" });
    }

    const con = this.modificadores["con"] ?? 0;
    for (const nivel of ordenarNumeros(this.classe_do_nivel.keys())) {
      const cid = this.classe_do_nivel.get(nivel) as string;
      const classe = this.base.get(cid);
      let por_nivel = 0;
      for (const g of this._grants_de(classe)) {
        if (ehDict(g) && Object.hasOwn(g, "hp_per_level")) por_nivel = inteiro(g["hp_per_level"]);
      }
      const ganho = por_nivel + con;
      total += ganho;
      this.hp_detalhe.push({
        origem: `nivel ${nivel} (${pyStr(nome(classe))})`,
        hp: ganho, nota: `${por_nivel} da classe + ${con} de CON`,
      });
    }

    // feat que concede HP -- `Toughness` é o caso clássico (`flat_modifier` com
    // selector `hp` e valor `@actor.level`). Sem isto o HP fica exatamente
    // `nivel` pontos abaixo do oficial, que foi como a validação contra os
    // iconics da Paizo achou esta lacuna.
    for (const [wb_id, feat, por] of this._feats_efetivos()) {
      for (const g of this._grants_de(feat)) {
        const fm = ehDict(g) ? g["flat_modifier"] : null;
        if (!verdadeiro(fm) || dictDe(fm)["selector"] !== "hp") continue;
        const valor = this._resolver_valor(dictDe(fm)["value"]);
        if (valor) {
          total += valor;
          this.hp_detalhe.push({
            origem: nomeOu(feat, wb_id), hp: valor,
            nota: `feat (${pyStr(obter(dictDe(fm), "value"))})`
                  + (verdadeiro(por) ? ` via ${pyStr(por)}` : ""),
          });
        }
      }
    }
    this.hp = total;
  }

  private *_feats_escolhidos(): Generator<[string, Registro]> {
    for (const e of this._todas_escolhas()) {
      const wb_id = e["pega"];
      if (ehStr(wb_id) && wb_id.startsWith("wb:feat/")) {
        const feat = this.base.opcional(wb_id);
        if (feat !== null) yield [wb_id, feat];
      }
    }
  }

  /**
   * Resolve a expressão do Foundry no valor deste personagem.
   *
   * Regra 19: em texto de regra impresso, "your level" significa **nível de
   * personagem** -- e `@actor.level` é exatamente isso.
   */
  /**
   * Resolve a expressão do Foundry no valor deste personagem.
   *
   * Devolve `null` para o que estiver FORA da gramática. Antes devolvia zero, e
   * zero é uma resposta: um `resistance` de `@actor.abilities.str.mod` saía como
   * "resistência 0" em vez de "não sei calcular".
   *
   * A gramática INTEIRA que a base usa: inteiro, `@actor.level`,
   * `@armor.system.runes.potency`, `+`, `/`, `floor()` e `max()`. Sem
   * multiplicação, sem subtração, e o único aninhamento é `max(1, floor(...))`.
   *
   * Spec: `specs/2026-07-30-resistencia-e-formula.md`
   */
  private _resolver_valor(expressao: unknown): number | null {
    if (typeof expressao === "boolean") return null;
    if (typeof expressao === "number") return Math.trunc(expressao);
    let texto = (verdadeiro(expressao) ? String(expressao) : "").trim();
    if (!texto) return null;
    texto = texto.replaceAll("@actor.details.level.value", String(this.nivel));
    texto = texto.replaceAll("@actor.level", String(this.nivel));
    if (texto.includes("@armor.system.runes.potency")) {
      texto = texto.replaceAll("@armor.system.runes.potency",
        String(this._potencia_de_armadura()));
    }
    if (!/^(?:floor|max|[\d\s+/(),])*$/.test(texto)) return null;
    return this._reduzir(texto);
  }

  /** A runa de potência da armadura EQUIPADA, ou 0 sem armadura. */
  private _potencia_de_armadura(): number {
    for (const entrada of listaDe(this.doc["inventario"])) {
      const e = dictDe(entrada);
      if (!verdadeiro(e["equipado"])) continue;
      const reg = dictDe(this.base.opcional(pyStr(e["item"])));
      if (reg["kind"] !== "armor") continue;
      return Math.max(inteiro(e["potencia"]), inteiro(dictDe(reg["runes"])["potency"]));
    }
    return 0;
  }

  private _reduzir(bruto: string): number | null {
    let texto = bruto.trim();
    // reduz a função mais INTERNA primeiro, para `max(1, floor(x/2))` sair
    let m = /(floor|max)\(([^()]*)\)/.exec(texto);
    while (m) {
      const args = m[2].split(",").map((a) => this._reduzir(a));
      if (args.some((a) => a === null)) return null;
      const nums = args as number[];
      const valor = m[1] === "floor" ? nums[0] : Math.max(...nums);
      texto = texto.slice(0, m.index) + String(valor) + texto.slice(m.index + m[0].length);
      m = /(floor|max)\(([^()]*)\)/.exec(texto);
    }
    if (texto.includes("(") || texto.includes(")")) return null;
    let total = 0;
    for (const parcela of texto.split("+")) {
      const limpa = parcela.trim();
      if (!limpa) return null;
      const partes = limpa.split("/").map((x) => Number.parseInt(x.trim(), 10));
      if (partes.some((x) => Number.isNaN(x))) return null;
      // divisão INTEIRA para baixo, que é o que `floor(a/b)` significa
      let valor = partes[0];
      for (const d of partes.slice(1)) {
        if (d === 0) return null;
        valor = Math.floor(valor / d);
      }
      total += valor;
    }
    return total;
  }

  // -- regras 12 e 14: slots de feat --------------------------------------

  /**
   * Regra 12: class feat a cada nível PAR de personagem, não por classe.
   * Regra 14: a cadência básica (ancestry, general, skill) segue o nível de
   * personagem, sem mudança.
   *
   * A conta é por PERSONAGEM. Somar as tabelas das classes multiplicaria os
   * slots e quebraria a regra 21 (a rota de nível nunca pode render mais que a
   * de dedicação... nem menos).
   */
  private _slots_de_feat(): void {
    const faixa: number[] = [];
    for (let n = 1; n <= this.nivel; n += 1) faixa.push(n);
    const basica = new Map<string, number[]>([
      ["class", faixa.filter((n) => n % 2 === 0)],
      ["skill", faixa.filter((n) => n % 2 === 0)],
      ["general", faixa.filter((n) => n % 4 === 3)],
      ["ancestry", faixa.filter((n) => n % 4 === 1)],
    ]);

    // Regra 15: quando uma CLASSE concede cadência extra, o extra passa a valer
    // a partir do nível de personagem em que aquela classe entrou. O Ladino
    // concede skill feat todo nível e o Investigador concede skill increase
    // todo nível -- usar só a cadência básica dava a eles metade dos slots.
    const extras = new Map<string, Set<number>>();
    for (const [k, v] of basica) extras.set(k, new Set(v));
    for (const [cid, desde] of this.entrada_da_classe) {
      const classe = this.base.get(cid);
      for (const g of this._grants_de(classe)) {
        const fs = ehDict(g) ? g["feat_slot"] : null;
        if (!verdadeiro(fs) || !verdadeiro(dictDe(fs)["kind"])) continue;
        const chave = String(dictDe(fs)["kind"]);
        if (!extras.has(chave)) extras.set(chave, new Set(basica.get(chave) ?? []));
        for (const bruto of listaDe(dictDe(fs)["levels"])) {
          const n = inteiro(bruto);
          // só conta a partir de quando a classe entrou (regra 15) e até o
          // nível atual
          if (desde <= n && n <= this.nivel) (extras.get(chave) as Set<number>).add(n);
        }
      }
    }

    this.slots = new Map();
    for (const [k, v] of extras) this.slots.set(k, ordenarNumeros(v));
    // regra 2: Free Archetype sempre ligado -- slot em todo nível par
    this.slots.set("free_archetype", faixa.filter((n) => n % 2 === 0));

    // regra 8: o class feat de nível 1 só vem da PRIMEIRA classe
    const dos_class = this.slots.get("class") ?? [];
    this.class_feat_nivel_1 = dos_class.includes(1);
    if (dos_class.includes(1) && this.primeira_classe !== null) {
      let concede = false;
      for (const g of this._grants_de(this.base.get(this.primeira_classe))) {
        if (!ehDict(g)) continue;
        const fs = dictDe(g["feat_slot"]);
        if (listaDe(fs["levels"]).some((n) => n === 1) && fs["kind"] === "class") {
          concede = true;
        }
      }
      if (!concede) {
        this.slots.set("class", dos_class.filter((n) => n !== 1));
        this.class_feat_nivel_1 = false;
      }
    }

    // Ha feat e heranca que CONCEDEM outro feat: `Ancient Elf` da a dedicacao
    // multiclasse, `Versatile Human` da um feat geral. E um slot novo, nao uma
    // cadencia, e o Foundry o escreve como ChoiceSet com `itemType: "feat"` e
    // um filtro. Sem este passo o jogador escolhia e nao era perguntado nada.
    // A familia vizinha ("when you gain an ancestry feat, you can choose...")
    // nao entra: ela alarga o pool de um slot existente, e trata-la como slot
    // daria feat de graca. A separacao vem da fonte, nao de heuristica.
    // Spec: `specs/2026-07-30-slot-de-feat-concedido.md`
    this.slots_concedidos = [];
    const fontesConc: Array<[Registro | Dict | null, number | "criacao"]> = [
      [this.heranca, "criacao"], [this.ancestria, "criacao"],
      [this.background, "criacao"],
    ];
    for (const [i, feat] of this._feats_efetivos()) {
      fontesConc.push([feat, this._nivel_do_feat(i)]);
    }
    for (const [reg, emQue] of fontesConc) {
      if (!reg) continue;
      for (const g of this._grants_de(dictDe(reg))) {
        const ch = dictDe(g)["choice"];
        // QUALQUER tipo, não só `feat`: são 69 blocos na base (feat 43,
        // spell 11, heritage 7, action 4, weapon 2, ancestry 1, deity 1) e
        // todos têm filtro. Até 2026-07-31 o motor filtrava por `feat` e as
        // outras 26 escolhas nunca eram perguntadas.
        // Spec: `specs/2026-07-31-slot-concedido-generico.md`
        if (!ehDict(ch) || !ch["tipo"] || !ch["filtro"]) continue;
        this.slots_concedidos.push({
          origem: pyStr(nome(dictDe(reg))), origem_id: pyStr(dictDe(reg)["id"]),
          em: emQue, flag: ch["flag"] === undefined ? null : pyStr(ch["flag"]),
          tipo: pyStr(ch["tipo"]), filtro: ch["filtro"],
        });
      }
    }

    // o que o documento realmente gastou
    for (const e of this._todas_escolhas()) {
      const slot = e["slot"];
      if (ehStr(slot) && ["class_feat", "skill_feat", "general_feat",
                          "ancestry_feat", "free_archetype"].includes(slot)) {
        empurrar(this.gastos, slot, e);
      }
    }

    this._higiene_de_slot();
  }

  /** cada slot do documento e a lista de níveis que o alimenta */
  static readonly SLOT_PARA_CADENCIA: Array<[string, string]> = [
    ["class_feat", "class"], ["skill_feat", "skill"], ["general_feat", "general"],
    ["ancestry_feat", "ancestry"], ["free_archetype", "free_archetype"],
  ];

  /**
   * Confronta o que foi GASTO com o que existe de slot.
   *
   * Até aqui o motor colecionava `gastos` e `slots` lado a lado sem nunca
   * compará-los: um pick de Free Archetype no nível 3 (onde não há slot), três
   * picks para dois slots, ou um class feat puro ocupando o slot gratuito
   * passavam os três em silêncio.
   *
   * Princípio zero: isto SINALIZA, nunca recusa. A escolha continua no documento
   * e a ficha continua derivando.
   */
  /** A escolha está acima do nível atual? Então é plano, não erro. Contado em
   *  `escolhas_de_nivel_futuro`: silenciar por decisão é diferente de silenciar
   *  por descuido, e só o contador distingue os dois depois. */
  private _e_plano(em: unknown): boolean {
    if (ehInt(em) && em > this.nivel) {
      this.escolhas_de_nivel_futuro += 1;
      return true;
    }
    return false;
  }

  private _higiene_de_slot(): void {
    for (const [slot, cadencia] of Personagem.SLOT_PARA_CADENCIA) {
      const niveis = this.slots.get(cadencia) ?? [];
      // escolha ACIMA do nível atual é PLANO, não erro: no nível 8 o
      // personagem vai ter o slot, e `niveis` só enumera os de hoje.
      const usados = (this.gastos.get(slot) ?? [])
        .filter((e) => !this._e_plano(obter(e, "em")));

      if (usados.length > niveis.length) {
        this.avisos.push(
          `slot ${slot}: ${usados.length} escolha(s) para ${niveis.length} `
          + `slot(s) disponivel(is) em ${pyRepr(niveis)}`);
      }

      for (const e of usados) {
        const em = obter(e, "em");
        // `em` não-inteiro DESLIGAVA a checagem: um feat posto em `criacao` por
        // engano passava calado. As cinco cadências são todas por nível.
        if (!ehInt(em)) {
          this.avisos.push(
            `slot ${slot}: escolha com nivel ${pyRepr(em)}, que nao e nivel `
            + `-- este slot so existe por nivel (${pyRepr(niveis)})`);
          continue;
        }
        if (!niveis.includes(em)) {
          this.avisos.push(
            `slot ${slot}: escolha no nivel ${em}, que nao tem slot desse tipo `
            + `(niveis validos: ${pyRepr(niveis)})`);
        }
      }
    }

    // o slot de Free Archetype (regra 2) só aceita feat de ARQUÉTIPO -- é a
    // única coisa que o distingue do slot de class feat. Sem esta checagem ele
    // vira um segundo class feat de graça em toda ficha.
    for (const e of this.gastos.get("free_archetype") ?? []) {
      const wb_id = e["pega"];
      if (!ehStr(wb_id)) continue;
      const feat = this.base.opcional(wb_id);
      if (feat === null) continue;
      if (!listaDe(feat["traits"]).includes("archetype")) {
        this.avisos.push(
          `slot free_archetype: ${nomeOu(feat, wb_id)} nao tem trait `
          + `\`archetype\` -- o slot gratuito so aceita feat de arquetipo`);
      }
    }
  }

  // -- regras 16, 17, 18: conjuração --------------------------------------

  /**
   * Regra 16: slots pelo nível de CLASSE cru, tabela nativa do PF2e.
   * Regra 17: rank efetivo = ceil(nivel_de_personagem / 2).
   *
   * É aqui que a houserule inteira aparece. Um Mago 2 dentro de um personagem
   * de nível 5 tem os SLOTS de um Mago 2 (2 de rank 1) mas conjura no rank 3 --
   * o slot vem da classe, a potência vem do personagem. Sem os dois números
   * separados não há como expressar isso.
   */
  private _conjuracao(): void {
    for (const cid of this.ordem_de_classe) {
      const classe = this.base.get(cid);
      const sc = classe["spellcasting"];
      if (!ehDict(sc) || !verdadeiro(sc["slots_per_level"])) continue;
      const nivel_classe = this.nivel_de(cid);
      const tabela = dictDe(sc["slots_per_level"])[String(nivel_classe)];
      if (!verdadeiro(tabela)) {
        this.avisos.push(
          `${pyStr(nome(classe))}: sem linha de slots para nivel de classe ${nivel_classe}`);
        continue;
      }
      const t = dictDe(tabela);
      const rank_efetivo = Math.ceil(this.nivel / 2);          // regra 17
      const max_rank_cru = inteiro(t["max_rank"]);             // regra 16
      const ranks: Record<string, number> = {};
      for (const [k, v] of Object.entries(dictDe(t["ranks"]))) ranks[k] = inteiro(v);
      // Feiticeiro, Bruxa e Invocador nao tem tradicao fixa: a classe traz uma
      // FRASE ("variavel (definida pela escolha de bloodline...)") e quem
      // responde e a subclasse. Sem esta resolucao a frase ia crua para a
      // ficha, no campo que decide quais magias ele pode aprender.
      // Spec: `specs/2026-07-30-tradicao-por-subclasse.md`
      let tradicao = obter(sc, "tradition") as string | null;
      if (!ehStr(tradicao) || !["arcane", "divine", "occult", "primal"].includes(tradicao)) {
        tradicao = this._tradicao_por_escolha(classe, { de: "subclasse" }, nomeOu(classe, cid));
      }
      this.conjuracao.push({
        classe: nomeOu(classe, cid),
        nivel_de_classe: nivel_classe,
        tradicao,
        tipo: obter(sc, "type") as string | null,
        slots: ranks,
        truques: obter(t, "cantrips") as number | null,
        max_rank_do_slot: max_rank_cru,
        rank_efetivo,
        elevacao: Math.max(0, rank_efetivo - max_rank_cru),
        rank_de_invocacao: this.cap_invocacao(nivel_classe),   // regra 17b
        dc: this._dc_de_conjuracao(classe, nivel_classe, sc),
      });
    }
    this._conjuracao_de_arquetipo();
  }

  /**
   * A rota de conjuração que a dedicação abre -- até 2026-07-29, invisível.
   *
   * 13 dedicações prometem conjuração na prosa e a ficha não mostrava nada.
   * Sob Free Archetype (regra 2, sempre ligada) essa é a rota mais comum de um
   * personagem não-conjurador.
   *
   * O rank vem do FEAT que o personagem pegou, não do nível dele: a tabela
   * `RANK_DEDICACAO` descreve a rota completa e serve de piso para a regra 21,
   * mas na ficha real quem só tem Basic para no rank 3 mesmo no nível 20.
   * Spec: specs/2026-07-29-spellcasting-de-arquetipo.md.
   */
  private _conjuracao_de_arquetipo(): void {
    for (const [origem_id, reg] of this._feats_efetivos()) {
      for (const g of this._grants_de(reg)) {
        if (!ehDict(g) || !("grant_spellcasting" in g)) continue;
        const gs = dictDe(g["grant_spellcasting"]);
        const degraus = dictDe(gs["degraus"]);
        let teto = 0;
        for (const [degrau, fid] of Object.entries(degraus)) {
          if (this._tem_feat(ehStr(fid) ? fid : null)) {
            teto = Math.max(teto, Personagem.TETO_DO_DEGRAU[degrau] ?? 0);
          }
        }
        // a tabela oficial, limitada pelo degrau que ele realmente tem
        const rank = Math.min(this.rank_de_dedicacao(), teto);
        let tradicao = ehStr(gs["tradicao"]) ? gs["tradicao"] : null;
        if (tradicao === "escolha") tradicao = this._tradicao_por_escolha(reg, gs);
        const slots: Record<string, number> = {};
        for (let r = 1; r <= rank; r++) slots[String(r)] = 1;
        const cadeia = ehStr(gs["cadeia"]) ? this.base.opcional(gs["cadeia"]) : null;
        this.conjuracao.push({
          classe: nome(cadeia) ?? nomeOu(reg, ""),
          de_arquetipo: true,
          origem: origem_id,
          nivel_de_classe: null,
          tradicao,
          tipo: ehStr(gs["tipo"]) ? gs["tipo"] : null,
          slots,
          truques: Object.hasOwn(gs, "truques") ? inteiro(gs["truques"]) : 2,
          max_rank_do_slot: rank,
          // regra 18: arquétipo roda RAW puro, então NÃO eleva
          rank_efetivo: rank,
          elevacao: 0,
          rank_de_invocacao: rank,
          dc: this._dc_de_arquetipo(),
        });
      }
    }
  }

  private _tem_feat(feat_id: string | null): boolean {
    if (!feat_id) return false;
    const alvo = this.base.resolver(feat_id);
    for (const [i] of this._feats_efetivos()) {
      if (this.base.resolver(i) === alvo) return true;
    }
    return false;
  }

  /**
   * Sorcerer usa a tradição do bloodline; a Bruxa, a do patron.
   *
   * Sem a escolha feita não dá para saber, e ARBITRAR aqui poria uma tradição
   * errada na ficha em silêncio -- mesmo tratamento do grau do companheiro:
   * avisa e devolve `null`.
   */
  /**
   * `classe` e o NOME da classe cuja conjuracao esta sendo resolvida, e sem ele
   * um Feiticeiro 5 / Bruxa 3 sai com a mesma tradicao nas duas linhas: a
   * varredura devolvia a primeira escolha de subclasse que tivesse tradicao,
   * qualquer que fosse a classe dona. A rota de arquetipo nao passa o filtro
   * porque ali a escolha e unica por cadeia.
   *
   * Spec: `specs/2026-07-30-tradicao-por-subclasse.md`
   */
  private _tradicao_por_escolha(reg: Dict, gs: Dict, classe: string | null = null): string | null {
    const eixo = ehStr(gs["de"]) ? gs["de"] : null;
    for (const e of this._todas_escolhas()) {
      if (e["slot"] !== "subclasse") continue;
      const pega = e["pega"];
      const escolhido = dictDe(ehStr(pega) ? this.base.opcional(pega) : null);
      if (classe) {
        const donas = escolhido["class"];
        if (Array.isArray(donas) && !donas.includes(classe)) continue;
      }
      const trad = dictDe(escolhido["spellcasting"])["tradition"] ?? escolhido["tradition"];
      if (ehStr(trad) && ["arcane", "divine", "occult", "primal"].includes(trad)) {
        return trad;
      }
    }
    this.avisos.push(
      `${nomeOu(reg, "")}: a tradicao vem da escolha de ${eixo ?? "subclasse"}, `
      + `que ainda nao foi feita -- slots sem tradicao ate resolver`);
    return null;
  }

  /**
   * Regra 3, como todo o resto: nível de PERSONAGEM + rank.
   *
   * A dedicação concede `trained` na tradição e não sobe sozinha -- quem sobe é
   * a cadeia, quando a prosa diz. Até haver dado disso, trained.
   */
  private _dc_de_arquetipo(): Conjuracao["dc"] {
    const rank: Rank = "trained";
    return {
      rank,
      dc: 10 + this.nivel + RANK_BONUS[rank],
      ataque: this.nivel + RANK_BONUS[rank],
      nota: "conjuracao de arquetipo: trained pela dedicacao",
    };
  }

  // teto de rank por degrau da cadeia, RAW ("Spellcasting Archetypes"): Basic
  // vai até rank 3, Expert até 6, Master até 8. Só a dedicação, sem nenhum
  // degrau, dá cantrip e nada de slot.
  static readonly TETO_DO_DEGRAU: Record<string, number> = {
    basic: 3, expert: 6, master: 8,
  };

  // -- regra 17b: teto para o que cria criatura ---------------------------

  /**
   * Rank de slot que a dedicação de conjuração concede, por nível de
   * PERSONAGEM. Citado verbatim da regra "Spellcasting Archetypes" (Player
   * Core): "Basic Spellcasting Feat: usually available at 4th level, these
   * feats grant a 1st-rank spell slot. At 6th level, a 2nd-rank spell slot. At
   * 8th level, a 3rd-rank spell slot. Expert: 12th -> 4th-rank, 14th -> 5th,
   * 16th -> 6th. Master: 18th -> 7th-rank, 20th -> 8th-rank."
   */
  static readonly RANK_DEDICACAO: Array<[number, number]> = [
    [20, 8], [18, 7], [16, 6], [14, 5], [12, 4], [8, 3], [6, 2], [4, 1],
  ];

  /**
   * O que a rota GRATUITA entrega neste nível de personagem.
   *
   * Sob Free Archetype (regra 2, sempre ligada) a dedicação não custa nada além
   * do slot gratuito de arquétipo, e pela regra 18 ela roda RAW puro. É por
   * isso que ela é o piso: qualquer coisa que custe nível de classe tem de
   * render pelo menos isto.
   */
  rank_de_dedicacao(nivel_personagem: number | null = null): number {
    const n = nivel_personagem === null ? this.nivel : nivel_personagem;
    return Personagem.RANK_DEDICACAO.find(([lvl]) => n >= lvl)?.[1] ?? 0;
  }

  /**
   * Rank máximo de magia com trait `summon` ou `incarnate` (regra 17b).
   *
   *     min( max( ceil(class_level/2) + 2 , rank_de_dedicacao ), ceil(nivel/2) )
   *
   * Três termos, cada um com um trabalho:
   *
   * - `ceil(class_level/2) + 2` -- a folga que a houserule concede a quem gastou
   *   nível de classe;
   * - `rank_de_dedicacao` -- o PISO da regra 21: gastar um nível inteiro de
   *   personagem tem de render pelo menos o que a dedicação entrega de graça sob
   *   Free Archetype. Sem ele a simulação de 2026-07-27 achou 50 de 204 pares
   *   violando, com o dip chegando a **0%** da dedicação no nível 20;
   * - `ceil(nivel/2)` -- o teto de heightened, que vale para tudo e faz a regra
   *   se autoproteger: com classe única os dois níveis são iguais, nem a folga
   *   nem o piso chegam a valer, e o RAW sai intacto sem caso especial.
   */
  cap_invocacao(nivel_classe: number): number {
    const folga = Math.ceil(nivel_classe / 2) + 2;
    return Math.min(Math.max(folga, this.rank_de_dedicacao()), Math.ceil(this.nivel / 2));
  }

  /**
   * Nível máximo de companheiro, familiar ou eidolon.
   *
   * Sem o `/2`, de propósito. Rank de magia já nasce em escala de metade do
   * nível; nível de criatura está na mesma escala do nível de personagem.
   * Dividir por dois faria um Ranger 12 PURO cair para companheiro nível 6,
   * quebrando classe única == RAW.
   */
  cap_ator(nivel_classe: number): number {
    return Math.min(nivel_classe + 2, this.nivel);
  }

  /**
   * A magia cria criatura que age sozinha? Deriva só de trait.
   *
   * `summon` (14 magias) e `incarnate` (23) não têm intersecção -- a segunda
   * cobre as invocações de rank 4 a 10. Spirit Link e Protector Tree NÃO
   * entram: não criam nada, são efeito contínuo.
   */
  eleva_por_invocacao(magia: Dict): boolean {
    const traits = listaDe(magia["traits"]);
    return traits.includes("summon") || traits.includes("incarnate");
  }

  /**
   * Avanço do companheiro, RAW (Player Core p.206 e 211). `nimble` e `savage`
   * partem de `mature`, então os ajustes são cumulativos com ele.
   */
  static readonly AVANCO: Record<string, {
    attr: Record<string, number>; dados: number; dano_extra: number;
    pericias: Record<string, string>;
  }> = {
    young: { attr: {}, dados: 1, dano_extra: 0, pericias: {} },
    mature: {
      attr: { str: 1, dex: 1, con: 1, wis: 1 }, dados: 2, dano_extra: 0,
      pericias: {
        perception: "expert", fortitude: "expert", reflex: "expert",
        will: "expert", intimidation: "trained", stealth: "trained",
        survival: "trained",
      },
    },
    nimble: {
      attr: { str: 2, dex: 3, con: 2, wis: 2 }, dados: 2, dano_extra: 2,
      pericias: {
        perception: "expert", fortitude: "expert", reflex: "expert",
        will: "expert", intimidation: "trained", stealth: "trained",
        survival: "trained", acrobatics: "expert",
      },
    },
    savage: {
      attr: { str: 3, dex: 2, con: 2, wis: 2 }, dados: 2, dano_extra: 3,
      pericias: {
        perception: "expert", fortitude: "expert", reflex: "expert",
        will: "expert", intimidation: "trained", stealth: "trained",
        survival: "trained", athletics: "expert",
      },
    },
  };

  /** RAW: "trained in its unarmed attacks, unarmored defense, barding, all
   * saving throws, Perception, Acrobatics, and Athletics" */
  static readonly PROF_BASE = ["unarmed", "unarmored", "barding", "fortitude",
                               "reflex", "will", "perception", "acrobatics",
                               "athletics"];

  /**
   * Feats reais na base que concedem cada avanço. Usados para DERIVAR o teto de
   * maturidade em vez de ler `ator["maturidade"]` como resultado pronto. Cada
   * lista cobre aliases duplicados que a base carrega para o mesmo feat (ex.:
   * "Mature Animal Companion" e "Mature Animal Companion (Druid)" são o mesmo
   * texto, mesma fonte, dois ids -- artefato do dump, não duas regras).
   */
  static readonly FEATS_MATURIDADE: Record<string, Record<string, string[]>> = {
    mature: {
      "wb:class/druid": ["wb:feat/mature-animal-companion",
                         "wb:feat/mature-animal-companion-druid"],
      "wb:class/ranger": ["wb:feat/mature-animal-companion-ranger"],
    },
    incredible: {
      "wb:class/druid": ["wb:feat/incredible-companion",
                         "wb:feat/incredible-companion-druid"],
      "wb:class/ranger": ["wb:feat/incredible-companion-ranger"],
    },
    specialized: {
      "wb:class/druid": ["wb:feat/specialized-companion-druid"],
      "wb:class/ranger": ["wb:feat/specialized-companion-ranger"],
    },
  };

  /**
   * Arquétipo Animal Trainer: trilha PRÓPRIA, gate por character_level -- isso é
   * RAW normal de arquétipo, não houserule, e essa trilha não passa pelas feats
   * de Druid/Ranger acima.
   */
  static readonly FEATS_MATURIDADE_ARQUETIPO: Record<string, string[]> = {
    mature: ["wb:feat/mature-trained-companion"],
    incredible: ["wb:feat/splendid-companion"],
    specialized: ["wb:feat/specialized-companion-animal-trainer"],
  };

  static readonly ORDEM_TIER = ["young", "mature", "incredible"];

  /**
   * RAW (Player Core p.211, "Specialized Animal Companions"): o dano extra
   * sempre DOBRA (nimble 2->4, savage 3->6) -- por isso o código multiplica em
   * vez de gravar os dois números na tabela.
   *
   * O "extra benefit" por TIPO de especialização NÃO está aqui: é escolha do
   * jogador sem campo no schema nem na base, então não dá pra derivar.
   */
  static readonly SPECIALIZADO = {
    attr_delta: { dex: 1, int: 2 } as Record<string, number>,
    dados: 3,
    pericias_upgrade: {
      unarmed: "expert", perception: "master", fortitude: "master",
      reflex: "master", will: "master",
    } as Record<string, string>,
  };

  /**
   * Deriva o teto de maturidade dos feats de avanço REALMENTE escolhidos (não
   * só presentes no requisito -- escolhidos de fato), conferindo o requisito de
   * cada um contra o nível de CLASSE que concedeu o companheiro. É a houserule
   * central deste ponto: um Ranger 6 dentro de um personagem 20 só passa disso
   * se tiver 6 níveis de Ranger, porque `class_level` no `requires` do feat é
   * comparado com `nivel_de(cid)`, nunca com `nivel`.
   */
  private _maturidade_do_companheiro(cid: string | null): [string, boolean] {
    const escolhidos = new Set<string>();
    for (const [wb_id] of this._feats_escolhidos()) escolhidos.add(wb_id);

    const valido = (feat_ids: string[]): boolean => {
      for (const fid of feat_ids) {
        if (!escolhidos.has(fid)) continue;
        const feat = this.base.opcional(fid);
        if (feat !== null && this.avaliar(feat["requires"])[0]) return true;
      }
      return false;
    };

    const maior = (a: string, b: string): string =>
      Personagem.ORDEM_TIER.indexOf(b) > Personagem.ORDEM_TIER.indexOf(a) ? b : a;

    let tier = "young";
    if (cid !== null && valido(Personagem.FEATS_MATURIDADE["mature"][cid] ?? [])) {
      tier = "mature";
      if (valido(Personagem.FEATS_MATURIDADE["incredible"][cid] ?? [])) tier = "incredible";
    }
    if (valido(Personagem.FEATS_MATURIDADE_ARQUETIPO["mature"])) {
      tier = maior(tier, "mature");
      if (valido(Personagem.FEATS_MATURIDADE_ARQUETIPO["incredible"])) {
        tier = maior(tier, "incredible");
      }
    }

    let especializado = false;
    if (tier === "incredible") {
      if (cid !== null && valido(Personagem.FEATS_MATURIDADE["specialized"][cid] ?? [])) {
        especializado = true;
      }
      if (valido(Personagem.FEATS_MATURIDADE_ARQUETIPO["specialized"])) especializado = true;
    }
    return [tier, especializado];
  }

  /**
   * Feats que ABREM ESCOLHA (nimble ou savage) em vez de decidir sozinhos -- o
   * mesmo padrão de `ChoiceSet` que o Foundry usa em ~243 dos 6.044 feats. A
   * base ainda não extrai esse tipo de escolha PARA FEATS (só para eixo de
   * subclasse), então aqui o feat é citado à mão.
   */
  static readonly FEATS_QUE_ABREM_ESCOLHA: Record<string, string[]> = {
    "wb:feat/incredible-companion": ["nimble", "savage"],
    "wb:feat/incredible-companion-druid": ["nimble", "savage"],
    "wb:feat/incredible-companion-ranger": ["nimble", "savage"],
    "wb:feat/splendid-companion": ["nimble", "savage"],
  };

  /**
   * `tier` já vem derivado dos feats. Incredible Companion (e Splendid
   * Companion) não dizem sozinhos se o companheiro fica nimble ou savage -- é
   * escolha do jogador, aberta pelo feat.
   *
   * Registrada com o MESMO vocabulário que o eixo de subclasse já usa, para o
   * front poder reusar o mesmo componente de picker.
   *
   * SEM escolha feita, `grau` vem null -- não há default silencioso para nimble
   * nem para young. Escolha não feita é estado legítimo.
   */
  private _resolver_grau_incredible(ator: Dict, tier: string): [string | null, Dict | null] {
    if (tier !== "incredible") return [tier, null];

    const escolhidos = new Set<string>();
    for (const [wb_id] of this._feats_escolhidos()) escolhidos.add(wb_id);
    const feat_id = Object.keys(Personagem.FEATS_QUE_ABREM_ESCOLHA)
      .find((fid) => escolhidos.has(fid)) ?? null;
    const feat = feat_id !== null ? this.base.opcional(feat_id) : null;
    const opcoes = (feat_id !== null
      ? Personagem.FEATS_QUE_ABREM_ESCOLHA[feat_id] : undefined) ?? ["nimble", "savage"];

    const declarado = listaDe(ator["escolhas"]).filter(ehDict)
      .find((e) => e["slot"] === "grau_avancado")?.["pega"] ?? null;
    const escolhido = ehStr(declarado) && opcoes.includes(declarado) ? declarado : null;

    const entrada: Dict = {
      origem: "feat",
      feat: feat_id,
      nome_do_feat: nomeOu(feat, pyStr(feat_id)),
      ator: verdadeiro(ator["nome"]) ? ator["nome"] : "",
      eixo: "grau-incredible-companion",
      nivel: obter(feat ?? {}, "level"),
      slot: "grau_avancado",
      escolhe: 1,
      opcoes,
      escolhido,
    };
    if (escolhido === null) {
      this.avisos.push(
        `companheiro ${verdadeiro(ator["nome"]) ? pyStr(ator["nome"]) : ""}: `
        + `${pyStr(entrada["nome_do_feat"])} aberto, falta escolher entre `
        + `${opcoes.join("/")} (slot \`grau_avancado\` no \`escolhas\` do ator)`);
    }
    return [escolhido, entrada];
  }

  /**
   * Ficha do companheiro, familiar e eidolon.
   *
   * Nível pela regra 17b; o resto é RAW puro -- "animal companions calculate
   * their modifiers and DCs just as you do", então bônus = nível + rank +
   * atributo, exatamente como o personagem.
   */
  /**
   * Quem, nesta ficha, CONCEDE um ator -- e em que nível.
   *
   * Sem isto o companheiro só entrava por `doc["atores"]` escrito à mão: pegar
   * `Animal Companion` no nível 1 não mudava nada na ficha e não gerava aviso.
   * O termo `grant_actor` vem do passo 7f do pipeline, derivado da prosa.
   *
   * A `classe` sai do NÍVEL em que o feat foi pego, e não de casar nome de
   * classe com o id do feat -- `wb:feat/animal-companion` não carrega a classe
   * no nome, e o cap da regra 17b depende dela.
   */
  private _concessoes_de_ator(): void {
    const em_de = new Map<string, unknown>();
    for (const e of this._todas_escolhas()) {
      const pega = e["pega"];
      if (ehStr(pega) && ehInt(e["em"]) && !em_de.has(pega)) em_de.set(pega, e["em"]);
    }

    const vistos = new Set<string>();
    for (const [origem_id, reg] of this._feats_efetivos()) {
      vistos.add(origem_id);
      this._coletar_grant_actor(origem_id, reg, em_de.get(origem_id) ?? null);
    }
    for (const f of this.features) {
      const fid = f["id"];
      if (ehStr(fid) && !vistos.has(fid)) {
        vistos.add(fid);
        this._coletar_grant_actor(fid, dictDe(this.base.opcional(fid) ?? f),
                                  em_de.get(fid) ?? null);
      }
    }
  }

  /** A classe DESTA ficha cuja progressão traz esta class-feature.
   *
   * Exata, e não chute: se duas classes do personagem concedessem a mesma
   * feature, a de MENOR nível manda, porque é a que aperta o cap da regra 17b
   * -- o oposto seria escolher o cap mais frouxo por acaso de ordem. */
  /** Os ids que casam com o filtro do `ChoiceSet`, ordenados por nome.
   *
   * A base guarda o filtro; a resolução é AQUI, por personagem, e não no build
   * -- lista congelada dessincroniza na primeira mudança de fonte. */
  private _ids_por_filtro(filtro: unknown): string[] {
    if (!verdadeiro(filtro)) return [];
    const casam: Registro[] = [];
    for (const r of this.base.por_id.values()) {
      if (this._casa_filtro(r, filtro)) casam.push(r);
    }
    casam.sort((a, b) => (a.name ?? "").localeCompare(b.name ?? ""));
    return casam.map((r) => r.id);
  }

  private _classe_que_concede(feature_id: string): string | null {
    const donas: string[] = [];
    for (const cid of this.ordem_de_classe) {
      const classe = dictDe(this.base.opcional(cid));
      const prog = listaDe(classe["progressao"]);
      if (prog.some((e) => dictDe(e)["concede"] === feature_id)) donas.push(cid);
    }
    if (donas.length === 0) return null;
    return donas.reduce((a, c) => this.nivel_de(c) < this.nivel_de(a) ? c : a);
  }

  /** Em que nível de PERSONAGEM esta class-feature chegou.
   *
   * A feature guarda `nivel_de_classe`, e a tela pergunta por nível de
   * personagem -- com a houserule os dois números são diferentes. */
  private _nivel_de_personagem_da_feature(feature_id: string): number | null {
    const cid = this._classe_que_concede(feature_id);
    if (cid === null) return null;
    const f = this.features.find((x) => x.id === feature_id);
    const alvo = f === undefined ? null : f.nivel_de_classe;
    if (!ehInt(alvo)) return null;
    let contados = 0;
    for (const n of [...this.classe_do_nivel.keys()].sort((a, b) => a - b)) {
      if (this.classe_do_nivel.get(n) === cid) {
        contados += 1;
        if (contados === alvo) return n;
      }
    }
    return null;
  }

  private _coletar_grant_actor(origem_id: string, reg: Dict, em: unknown): void {
    for (const g of this._grants_de(reg)) {
      if (!ehDict(g) || !("grant_actor" in g)) continue;
      const ga = dictDe(g["grant_actor"]);
      // feature vinda da PROGRESSÃO não foi "pega" em nível nenhum, então `em`
      // chegava null -- e a tela só desenha a concessão no bloco em que
      // `em === n`. Resultado: o familiar da Bruxa nunca aparecia como slot.
      if (em === null || em === undefined) {
        em = this._nivel_de_personagem_da_feature(origem_id);
      }
      this.concessoes_de_ator.push({
        origem: origem_id,
        origem_nome: nomeOu(reg, origem_id),
        em,
        tipo: ehStr(ga["tipo"]) ? ga["tipo"] : "companheiro",
        escolhe: ehStr(ga["escolhe"]) ? ga["escolhe"] : "animal-companion",
        opcoes: listaDe(ga["opcoes"]).filter(ehStr),
        // o nível em que foi PEGO diz a classe -- mas feature vinda da
        // PROGRESSÃO não foi pega em nível nenhum, e aí o `em` é null. Nesse
        // caso a classe é exata: é a que traz a feature na `progressao`. Sem
        // isto a regra 17b não aplicava a NENHUM familiar concedido por classe.
        classe: ehInt(em) ? (this.classe_do_nivel.get(em) ?? null)
                          : this._classe_que_concede(origem_id),
        preenchida: false,
        // a fonte declara as PROPRIAS excecoes a regra de um ator por vez:
        // "Contrary to the usual rules for animal companions, this feat can
        // grant you a SECOND animal companion". 6 dos 30 concessores.
        // Spec: `specs/2026-07-30-segundo-ator.md`
        adicional: verdadeiro(ga["adicional"]),
        escolhido: null,
      });
    }
  }

  /**
   * `concedido_por` + `em`. O `em` desempata quando o mesmo feat concede duas
   * vezes (Mammoth Lord dá um segundo companheiro) e é opcional: ator antigo,
   * sem `em`, casa com a primeira concessão daquela origem.
   */
  /**
   * Mais de um ator do mesmo tipo sem nenhuma fonte que autorize.
   *
   * AVISO e nao bloqueio: bloquear apagaria escolha ja feita pelo jogador, e
   * este projeto marca em vez de sumir. A regra geral esta na fonte
   * (`Familiars`, AoN: "You can have only one familiar at a time").
   */
  private _avisar_ator_duplicado(): void {
    const porTipo = new Map<string, ConcessaoDeAtor[]>();
    for (const c of this.concessoes_de_ator) {
      const lista = porTipo.get(c.tipo) ?? [];
      lista.push(c);
      porTipo.set(c.tipo, lista);
    }
    for (const tipo of [...porTipo.keys()].sort()) {
      const lista = porTipo.get(tipo) ?? [];
      if (lista.length < 2 || lista.some((c) => c.adicional)) continue;
      const origens = lista.map((c) => c.origem_nome || "?").sort().join(", ");
      this.avisos.push(
        `${lista.length} fontes de ${tipo} na ficha (${origens}) e nenhuma `
        + `delas declara conceder um adicional -- pelo livro vale um por vez`);
    }
  }

  private _casar_ator_com_concessao(ator: Dict): ConcessaoDeAtor | null {
    const origem = ator["concedido_por"];
    if (!verdadeiro(origem)) return null;
    let candidatas = this.concessoes_de_ator.filter(
      (c) => c.origem === String(origem) && !c.preenchida);
    if (ator["em"] !== undefined && ator["em"] !== null) {
      const exatas = candidatas.filter((c) => c.em === ator["em"]);
      if (exatas.length > 0) candidatas = exatas;
    }
    if (candidatas.length === 0) return null;
    const escolhida = candidatas[0];
    escolhida.preenchida = true;
    const pega = listaDe(ator["escolhas"]).filter(ehDict)
      .find((e) => e["slot"] === "animal")?.["pega"];
    escolhida.escolhido = ehStr(pega) ? pega : null;
    return escolhida;
  }

  private _atores(): void {
    this._concessoes_de_ator();
    this._avisar_ator_duplicado();
    for (const bruto of listaDe((this.doc as unknown as Dict)["atores"])) {
      const a = dictDe(bruto);
      const concessao = this._casar_ator_com_concessao(a);
      if (verdadeiro(a["concedido_por"]) && concessao === null) {
        this.avisos.push(
          `ator ${verdadeiro(a["nome"]) ? pyStr(a["nome"]) : ""}: `
          + `\`concedido_por\` aponta para ${String(a["concedido_por"])}, que nao `
          + `esta na ficha ou nao concede ator -- o feat pode ter sido removido depois`);
      }
      const [cid, nota] = this._classe_do_ator(a, concessao);
      const nivel_classe = cid !== null ? this.nivel_de(cid) : this.nivel;
      const ator: Dict = {
        tipo: obter(a, "tipo"),
        nome: verdadeiro(a["nome"]) ? a["nome"] : "",
        concedido_por: obter(a, "concedido_por"),
        em: obter(a, "em"),
        classe: cid !== null ? nome(this.base.opcional(cid)) : null,
        nivel_de_classe: nivel_classe,
        nivel: this.cap_ator(nivel_classe),
        nota,
        escolhas: listaDe(a["escolhas"]),
      };
      if (a["tipo"] === "companheiro") {
        const [tier, temEspecializado] = this._maturidade_do_companheiro(cid);
        let especializado = temEspecializado;
        const [grau, pendente] = this._resolver_grau_incredible(a, tier);
        if (pendente !== null) this.escolhas_de_feat.push(pendente);
        if (grau === null && especializado) {
          this.avisos.push(
            `companheiro ${verdadeiro(a["nome"]) ? pyStr(a["nome"]) : ""}: `
            + `Specialized Companion detectado, mas o grau nimble/savage ainda `
            + `nao foi escolhido -- specialized nao aplicado ate resolver`);
        }
        if (grau === null) especializado = false;
        ator["grau_pendente"] = grau === null;
        Object.assign(ator, this._ficha_de_companheiro(
          a, ator["nivel"] as number, grau ?? "mature", especializado));
      } else if (a["tipo"] === "familiar") {
        Object.assign(ator, this._ficha_de_familiar(ator["nivel"] as number));
      } else if (a["tipo"] === "eidolon") {
        Object.assign(ator, this._ficha_de_eidolon(a));
      }
      this.atores.push(ator);
    }
  }

  // -- familiar e eidolon ---------------------------------------------------
  //
  // Ao contrário do companheiro animal, que tem colunas numéricas nativas no
  // AoN, estes dois DERIVAM do mestre -- o que existe é fórmula, não tabela, e
  // é por isso que procurar tabela nunca achou nada. A fórmula vem da base
  // (`wb:stat-formula/*`), lida de `aon_dump/rules.json` e do feat `Pet`.
  // Spec: `specs/2026-07-31-estatisticas-de-familiar-e-eidolon.md`

  private _formula(qual: string): Dict {
    return dictDe(dictDe(this.base.opcional(`wb:stat-formula/${qual}`))["formula"]);
  }

  /** O maior modificador de atributo de conjuração entre as classes.
   *
   * Sai de `key_ability` da CLASSE, e não de `this.conjuracao`: a visão de
   * conjuração não expõe o modificador em campo próprio -- ele só aparece
   * dentro do texto de `dc.nota`. Ler dali seria parsear a própria saída. */
  private _mod_de_conjuracao(): number {
    let melhor = 0;
    for (const cid of this.ordem_de_classe) {
      const classe = dictDe(this.base.opcional(cid));
      if (!verdadeiro(classe["spellcasting"])) continue;
      const chaves = listaDe(classe["key_ability"]).map((k) => String(k));
      const mod = Math.max(0, ...chaves.map((k) => this.modificadores[k] ?? 0));
      if (mod > melhor) melhor = mod;
    }
    return melhor;
  }

  private _ficha_de_familiar(nivel: number): Dict {
    const f = this._formula("familiar");
    if (Object.keys(f).length === 0) {
      return { aviso: "formula do familiar ausente na base" };
    }
    const base_pericia = inteiro(f["pericia_base"]);
    const mod = verdadeiro(f["usa_mod_de_conjuracao_se_maior"])
      ? this._mod_de_conjuracao() : 0;
    const usado = Math.max(base_pericia, mod);
    return {
      // AC e saves são os do MESTRE, não recalculados
      ac: dictDe(this.ac)["total"] ?? null,
      // o TOTAL, e não a linha inteira: o cartão de ator mostra número, e o
      // companheiro já emite número. Copiar `salvas` cru punha
      // `[object Object]` na ficha -- achado pela verificação no navegador.
      saves: Object.fromEntries(Object.entries(this.salvas ?? {}).map(
        ([k, v]) => [k, ehDict(v) ? v["total"] : v])),
      hp: inteiro(f["hp_por_nivel"]) * nivel,
      percepcao: usado + nivel,
      pericias: { acrobatics: usado + nivel, stealth: usado + nivel },
      outras_pericias: nivel,
      velocidade: { land: inteiro(f["velocidade"]) },
      tamanho: f["tamanho"] ?? null,
      sentidos: "low-light vision",
      nota_de_pericia: usado === base_pericia ? "3 + nivel"
        : `mod de conjuracao ${comSinal(mod)} + nivel (maior que ${base_pericia})`,
    };
  }

  // sem `nivel` de proposito: o eidolon nao tem nivel proprio, ele usa o do
  // personagem (`this.nivel`) tanto no AC quanto nas salvas. O parametro
  // entrou por simetria com `_ficha_de_familiar`, que USA o dele nas pericias,
  // e ficou vestigial nos dois motores -- no TS ele quebrava `tsc -b`.
  private _ficha_de_eidolon(ator: Dict): Dict {
    const f = this._formula("eidolon");
    if (Object.keys(f).length === 0) {
      return { aviso: "formula do eidolon ausente na base" };
    }
    const pega = listaDe(ator["escolhas"])
      .map((e) => dictDe(e))
      .find((e) => e["slot"] === "eidolon")?.["pega"] ?? null;
    const tipo = dictDe(this.base.opcional(String(pega ?? "")));
    const prof = dictDe(f["proficiencias"]);
    const saves: Record<string, number> = {};
    for (const k of ["fortitude", "reflex", "will"]) {
      if (verdadeiro(prof[k])) {
        saves[k] = this.nivel + RANK_BONUS[String(prof[k]) as Rank];
      }
    }
    const saida: Dict = {
      hp: null,                       // compartilha o pool do invocador
      nota_de_hp: "sem HP proprio -- compartilha o pool do invocador",
      proficiencias: { ...prof },
      saves,
      pericias_do_invocador: verdadeiro(f["compartilha_pericias_do_invocador"]),
    };
    if (Object.keys(tipo).length === 0) {
      saida["aviso"] = pega === null ? "tipo de eidolon ainda nao escolhido"
        : `tipo de eidolon nao encontrado: ${pega}`;
      return saida;
    }
    const st = dictDe(tipo["stats"]);
    // `arrays` é o que ESTA SPEC acrescentou; `stats` sozinho já existia com
    // outra forma, então o teste tem de ser pelo campo novo.
    const arrays = listaDe(st["arrays"]).map((a) => dictDe(a));
    if (arrays.length === 0) {
      saida["aviso"] = `${nomeOu(tipo, "")}: `
        + `${tipo["stats_ausente"] ?? "sem array na fonte"}`;
      saida["velocidade"] = st["velocidade"] ?? null;
      return saida;
    }
    const escolhido = arrays.find((a) => a["nome"] === ator["array"]) ?? arrays[0];
    const attr = dictDe(escolhido["atributos"]);
    const dex = Math.min(inteiro(attr["dex"]), inteiro(escolhido["dex_cap"]));
    Object.assign(saida, {
      array: escolhido["nome"] ?? null,
      arrays_possiveis: arrays.map((a) => a["nome"] ?? null),
      atributos: { ...attr },
      // 10 + nível + prof(unarmored, trained) + DEX capado + bônus de item
      ac: 10 + this.nivel + RANK_BONUS["trained"] + dex
        + inteiro(escolhido["ac_item"]),
      dex_cap: escolhido["dex_cap"] ?? null,
      pericias: listaDe(st["pericias"]).map((p) => String(p).toLowerCase()),
      tamanhos: listaDe(st["tamanhos"]).map((s) => String(s)),
      // o que o extrator de companheiros já trazia, preservado
      velocidade: st["velocidade"] ?? null,
      tradicao: st["tradicao"] ?? null,
    });
    if (arrays.length > 1 && !verdadeiro(ator["array"])) {
      saida["nota_de_array"] = `${arrays.length} arrays possiveis e nenhum `
        + `escolhido; mostrando ${escolhido["nome"]}`;
    }
    return saida;
  }

  /**
   * RAW, Player Core p.206: atributos do stat block com os ajustes de avanço;
   * HP de ancestria mais (6 + CON) por nível; proficiência treinada na lista
   * base, elevada pelo avanço. `grau` e `especializado` já vêm DERIVADOS dos
   * feats -- aqui é só aplicar os números.
   */
  private _ficha_de_companheiro(ator: Dict, nivel: number, grau: string,
                                especializado: boolean): Dict {
    const pega = listaDe(ator["escolhas"]).filter(ehDict)
      .find((e) => e["slot"] === "animal")?.["pega"] ?? null;
    const especie = dictDe(this.base.opcional(ehStr(pega) ? pega : ""));
    const st = dictDe(especie["stats"]);
    if (Object.keys(st).length === 0) {
      return { aviso: `especie do companheiro nao encontrada: ${pyStr(pega)}` };
    }

    const av = Personagem.AVANCO[grau] ?? Personagem.AVANCO["young"];
    const attr = new Map<string, number>();
    for (const [k, v] of Object.entries(dictDe(st["atributos"]))) attr.set(k, inteiro(v));
    for (const [k, v] of Object.entries(av.attr)) attr.set(k, (attr.get(k) ?? 0) + v);
    let dados = av.dados;
    let dano_extra = av.dano_extra;
    const pericias_av = new Map(Object.entries(av.pericias));

    // Specialized Animal Companions (Player Core p.211): delta por cima do
    // nimble/savage já acumulado
    if (especializado) {
      for (const [k, v] of Object.entries(Personagem.SPECIALIZADO.attr_delta)) {
        attr.set(k, (attr.get(k) ?? 0) + v);
      }
      dados = Personagem.SPECIALIZADO.dados;
      dano_extra *= 2;
      for (const [k, v] of Object.entries(Personagem.SPECIALIZADO.pericias_upgrade)) {
        pericias_av.set(k, v);
      }
    }

    // RAW: "ancestry Hit Points from its type, plus a number of Hit Points
    // equal to 6 plus its Constitution modifier for each level you have"
    const hp = inteiro(st["hp"]) + (6 + (attr.get("con") ?? 0)) * nivel;

    const prof = new Map<string, string>();
    for (const k of Personagem.PROF_BASE) prof.set(k, "trained");
    for (const p of listaDe(st["pericia_inicial"])) prof.set(String(p).toLowerCase(), "trained");
    for (const [k, v] of pericias_av) {
      // "if it was already trained in one of those skills from its type,
      // increase its proficiency rank in that skill to expert"
      if (v === "trained" && prof.get(k) === "trained") prof.set(k, "expert");
      else prof.set(k, v);
    }

    const bonus = (chave: string, atributo: string): number =>
      nivel + RANK_BONUS[(prof.get(chave) ?? "untrained") as Rank] + (attr.get(atributo) ?? 0);

    const ataques: Dict[] = [];
    for (const bruto of listaDe(st["ataques"])) {
      const atk = dictDe(bruto);
      const dado = verdadeiro(atk["dano"]) ? String(atk["dano"]) : "";
      const face = dado.includes("d") ? dado.split("d")[dado.split("d").length - 1] : null;
      const traits = listaDe(atk["traits"]);
      const agil = traits.includes("agile");
      // finesse usa DEX quando compensa; o resto é STR, como no personagem
      const usa = traits.includes("finesse")
        && (attr.get("dex") ?? 0) > (attr.get("str") ?? 0) ? "dex" : "str";
      const dano = verdadeiro(face) ? `${dados}d${String(face)}` : "?";
      const mod = (attr.get("str") ?? 0) + dano_extra;
      ataques.push({
        nome: obter(atk, "nome"),
        ataque: bonus("unarmed", usa),
        dano: mod ? `${dano}${comSinal(mod)}` : dano,
        tipo: obter(atk, "tipo"),
        traits,
        agil,
      });
    }

    return {
      especie: nome(especie),
      maturidade: grau,
      especializado,
      tamanho: obter(st, "tamanho"),
      velocidade: obter(st, "velocidade"),
      sentidos: obter(st, "sentidos"),
      atributos: objetoDe(attr),
      hp,
      hp_detalhe: `${pyStr(obter(st, "hp"))} de ancestria + `
                  + `(6 ${comSinal(attr.get("con") ?? 0)}) x ${nivel}`,
      ac: 10 + (attr.get("dex") ?? 0) + nivel
          + RANK_BONUS[(prof.get("unarmored") ?? "untrained") as Rank],
      proficiencias: objetoDe(prof),
      saves: {
        fortitude: bonus("fortitude", "con"),
        reflex: bonus("reflex", "dex"),
        will: bonus("will", "wis"),
      },
      percepcao: bonus("perception", "wis"),
      ataques,
      support: obter(st, "support_benefit"),
      manobra_avancada: grau === "nimble" || grau === "savage"
        ? obter(st, "advanced_maneuver") : null,
    };
  }

  /**
   * De qual classe veio o ator. `classe` explícito ganha; senão tenta o
   * `concedido_por`; senão assume a classe de maior nível e AVISA -- chutar em
   * silêncio daria o cap errado sem ninguém perceber.
   */
  private _classe_do_ator(ator: Dict,
                          concessao: ConcessaoDeAtor | null = null,
  ): [string | null, string | null] {
    if (verdadeiro(ator["classe"])) return [String(ator["classe"]), null];
    // a concessão sabe em que NÍVEL o feat foi pego, e o nível diz a classe. É
    // o único caminho que acerta num `wb:feat/animal-companion`, cujo id não
    // carrega classe nenhuma.
    if (concessao !== null && concessao.classe !== null) return [concessao.classe, null];
    const origem = ator["concedido_por"];
    if (verdadeiro(origem)) {
      for (const cid of this.ordem_de_classe) {
        const n = nomeOu(this.base.opcional(cid), "");
        if (verdadeiro(n) && String(origem).includes(n.toLowerCase().replaceAll(" ", "-"))) {
          return [cid, null];
        }
      }
    }
    if (this.ordem_de_classe.length === 0) {
      return [null, "sem classe para ancorar o nivel do ator"];
    }
    let maior = this.ordem_de_classe[0];
    for (const cid of this.ordem_de_classe) {
      if (this.nivel_de(cid) > this.nivel_de(maior)) maior = cid;
    }
    return [maior, `classe de origem nao declarada; usei `
                   + `${pyStr(nome(this.base.opcional(maior)))} (a de maior nivel). `
                   + `Declare \`classe\` no ator para travar o cap da regra 17b`];
  }

  /** Regra 3: bônus = nível_de_PERSONAGEM + rank; o RANK vem do nível da classe. */
  private _dc_de_conjuracao(classe: Registro, nivel_classe: number,
                            sc: Dict): Conjuracao["dc"] {
    let prog = dictDe(sc["proficiency"]);

    // A progressão pode depender da SUBCLASSE. O Clérigo é o caso publicado:
    // Cloistered chega a legendary no 19, Warpriest para em master. Ler a
    // progressão "da classe" aqui daria o número errado para metade dos
    // Clérigos -- e é por isso que `class_level` sozinho não basta.
    const aninhadas = new Map<string, Dict>();
    for (const [k, v] of Object.entries(prog)) if (ehDict(v)) aninhadas.set(k, v);
    if (aninhadas.size > 0) {
      const escolhida = this._subclasse_de(String(classe["id"]));
      let chave: string | null = null;
      if (verdadeiro(escolhida)) {
        const alvo = normChave(dictDe(this.base.opcional(escolhida)));
        chave = [...aninhadas.keys()].find((k) => normSlug(k) === alvo) ?? null;
      }
      if (chave === null) {
        chave = ordenarTextos(aninhadas.keys())[0];
        this.avisos.push(
          `${pyStr(nome(classe))}: progressao de conjuracao depende da subclasse `
          + `(${ordenarTextos(aninhadas.keys()).join(", ")}) e nenhuma foi escolhida `
          + `-- usando \`${chave}\``);
      }
      prog = aninhadas.get(chave) as Dict;
    }

    let rank: Rank = "untrained";
    for (const n of RANKS) {
      const exigido = prog[n];
      if (ehInt(exigido) && nivel_classe >= exigido) rank = melhorRank(rank, n);
    }
    const chaves = listaDe(classe["key_ability"]).map(String);
    const mods = chaves.map((k) => this.modificadores[k] ?? 0);
    const mod = mods.length > 0 ? Math.max(...mods) : 0;
    const bonus = this.nivel + RANK_BONUS[rank] + mod;
    return {
      rank, dc: 10 + bonus, ataque: bonus,
      nota: `nivel de personagem ${this.nivel} + rank ${rank} `
            + `(pelo nivel de classe ${nivel_classe}) + mod ${mod}`,
    };
  }

  // -- regra 22: focus ----------------------------------------------------

  /** Regra 22: pool ÚNICO do personagem, teto 3, independente das classes. */
  private _focus(): void {
    let pool = 0;
    for (const cid of this.ordem_de_classe) {
      const sc = this.base.get(cid)["spellcasting"];
      if (ehDict(sc)) pool += inteiro(dictDe(sc["focus_pool"])["base"]);
    }
    this.focus_pool = Math.min(3, pool);
  }

  // -- AC e ataque: a ficha tem que trazer os números ---------------------

  private _equipados(kind: string): Array<{ registro: Registro; entrada: Dict }> {
    const saida: Array<{ registro: Registro; entrada: Dict }> = [];
    for (const bruto of listaDe((this.doc as unknown as Dict)["inventario"])) {
      const item = dictDe(bruto);
      if (!verdadeiro(item["equipado"]) && !verdadeiro(item["investido"])) continue;
      const reg = this.base.opcional(ehStr(item["item"]) ? item["item"] : "");
      if (reg !== null && reg.kind === kind) saida.push({ registro: reg, entrada: item });
    }
    return saida;
  }

  /**
   * AC = 10 + DEX (limitado pelo cap da armadura) + proficiência + item.
   *
   * Regra 3 vale aqui como em tudo: o bônus de proficiência é
   * `nivel_de_personagem + rank`, e o rank sai da categoria da armadura que
   * está sendo usada -- que pode ter vindo de qualquer classe (regra 4).
   */
  private _defesa(): void {
    const dex = this.modificadores["dex"] ?? 0;
    const armaduras = this._equipados("armor");
    const escudos = this._equipados("shield");

    let categoria: string;
    let dex_usada: number;
    let item_bonus: number;
    let potencia: number;
    let nome_arm: string | null;
    let penalidade: unknown;
    let forca: unknown;

    if (armaduras.length > 0) {
      const arm = armaduras[0].registro;
      categoria = verdadeiro(arm["armor_category"]) ? String(arm["armor_category"]) : "unarmored";
      const cap = arm["dex_cap"];
      dex_usada = ehInt(cap) ? Math.min(dex, cap) : dex;
      item_bonus = inteiro(arm["ac_bonus"]);
      // mesma regra da arma: runa do registro OU da entrada do inventário
      potencia = Math.max(inteiro(armaduras[0].entrada["potencia"]),
                          inteiro(dictDe(arm["runes"])["potency"]));
      nome_arm = nome(arm);
      penalidade = obter(arm, "check_penalty");
      forca = obter(arm, "strength");
    } else {
      categoria = "unarmored";
      dex_usada = dex;
      item_bonus = 0;
      potencia = 0;
      nome_arm = "sem armadura";
      penalidade = null;
      forca = null;
    }

    const rank = this.proficiencias.get(categoria) ?? "untrained";
    const prof = rank !== "untrained" ? this.nivel + RANK_BONUS[rank] : 0;

    // o `item_bonus` da armadura E um bonus de item, e os 6 grants
    // incondicionais de `ac` da base tambem (Bands of Force, Assassin's
    // Bracers). Somar um sobre o outro daria +2 a quem veste Couro e Bands of
    // Force, onde o RAW da +1 -- mesmo tipo nao empilha. Por isso a armadura
    // entra como CONTENDOR. A runa de potencia soma ao bonus da armadura ANTES
    // da disputa: pelo RAW ela aumenta o bonus de item, nao e um segundo.
    const contendores: BonusAplicado[] = [];
    if (item_bonus || potencia) {
      contendores.push({ tipo: "item", valor: item_bonus + potencia, origem: nome_arm ?? "" });
    }
    contendores.push(...(this._bonus_incondicionais().get("ac") ?? []));
    const bonus_de_item = this._melhor_por_tipo(contendores);
    const total = 10 + dex_usada + prof + bonus_de_item;

    // a penalidade de armadura só vale se a FOR não alcança o mínimo
    const aplica_penalidade = ehInt(forca) && (this.atributos["str"] ?? 10) < forca;

    this.ac = {
      total,
      armadura: nome_arm,
      categoria,
      rank,
      detalhe: `10 + DEX ${comSinal(dex_usada)} + prof ${prof} `
               + `(${rank}, nivel ${this.nivel}) + item ${bonus_de_item}`,
      // de onde veio cada contendor, para a ficha poder explicar por que dois
      // itens de +1 nao viraram +2
      bonus: contendores.map((c) => ({ tipo: c.tipo, valor: c.valor, origem: c.origem })),
      dex_perdida: Math.max(0, dex - dex_usada),
      check_penalty: aplica_penalidade ? (penalidade as number) : 0,
      escudo: escudos.length > 0
        ? { nome: nome(escudos[0].registro), ac: inteiro(escudos[0].registro["ac_bonus"]) }
        : null,
    };
  }

  /**
   * Ataque = nível + rank da categoria + atributo + item; dano = dados +
   * atributo.
   *
   * `finesse` deixa usar DEX no ataque; o dano continua em FOR, salvo exceção
   * que depende de feature (Thief usa DEX, e isso vem de rule element com
   * predicado -- por isso não está aqui).
   */
  private _ataques(): void {
    for (const equipado of this._equipados("weapon")) {
      const arma = equipado.registro;
      const entrada = equipado.entrada;
      const traits = new Set(listaDe(arma["traits"]).map((t) => String(t).toLowerCase()));
      const categoria = verdadeiro(arma["weapon_category"])
        ? String(arma["weapon_category"]) : "simple";
      // pelo `weapon:<slug>`, e não pela categoria crua: é por aqui que o remap
      // de `weapon_proficiency` chega ao BÔNUS DE ATAQUE. Sem isto o conserto
      // do item 75 ficaria só no predicado, e o número na ficha continuaria
      // errado. Spec: `specs/2026-07-30-proficiencia-de-arma-nomeada.md`
      const slugDaArma = pyStr(arma["id"]).split("/").pop() ?? "";
      const rank = (this._rank_de_arma(`weapon:${slugDaArma}`, null)
        ?? this.proficiencias.get(categoria) ?? "untrained") as Rank;
      const prof = rank !== "untrained" ? this.nivel + RANK_BONUS[rank] : 0;

      const forca = this.modificadores["str"] ?? 0;
      const destreza = this.modificadores["dex"] ?? 0;
      let usa_dex = traits.has("finesse") && destreza > forca;
      let atributo = usa_dex ? destreza : forca;
      // arma a distância usa DEX no ataque e não soma atributo no dano
      const distancia = verdadeiro(arma["range"]) && !traits.has("thrown");
      if (distancia) {
        atributo = destreza;
        usa_dex = true;
      }

      // RUNAS: vêm de dois lugares e os dois contam -- as embutidas no item
      // mágico da base (974 armas têm `runes`) e as que o jogador gravou na
      // entrada do inventário. Até 2026-07-29 só a segunda era lida, e
      // `striking` era ignorado sempre: `+1 striking longsword` saía 1d8.
      const runas = dictDe(arma["runes"]);
      const potencia = Math.max(inteiro(entrada["potencia"]),
                                inteiro(runas["potency"]));
      const striking = Math.max(inteiro(entrada["striking"]),
                                inteiro(runas["striking"]));
      const propriedade = ordenarTextos([...new Set([
        ...listaDe(runas["property"]).map((p) => pyStr(p)),
        ...listaDe(entrada["property"]).map((p) => pyStr(p)),
      ])]);
      const dano = dictDe(arma["damage"]);
      const mod_dano = distancia ? 0 : forca;
      // cada grau de striking soma UM dado do mesmo tamanho
      const dados = inteiro(Object.hasOwn(dano, "dados") ? dano["dados"] : 1) + striking;
      const base_do_dano = `${dados}`
                           + `${pyStr(Object.hasOwn(dano, "dado") ? dano["dado"] : "")}`;

      this.ataques.push({
        arma: nome(arma),
        categoria,
        rank,
        ataque: rank !== "untrained"
          ? this.nivel + RANK_BONUS[rank] + atributo + potencia
          : atributo + potencia,
        atributo_do_ataque: usa_dex ? "dex" : "str",
        dano: this.danoDecomposto(arma, base_do_dano, mod_dano, rank, distancia),
        tipo_de_dano: (verdadeiro(dano["tipo"]) ? dano["tipo"] : dano["type"] ?? null) as string | null,
        potencia,
        striking,
        runas_de_propriedade: propriedade,
        traits: ordenarTextos(traits),
        detalhe: `nivel ${this.nivel} + prof ${prof} (${rank}) + `
                 + `${usa_dex ? "DEX" : "FOR"} ${comSinal(atributo)}`,
      });
    }
  }

  // -- parcelas de dano ----------------------------------------------------
  //
  // Até 2026-07-30 `ataques[].dano` era string já concatenada (`"2d8+4"`): o
  // ATAQUE tinha `detalhe`, o dano não tinha nada. E estava incompleta, não só
  // opaca -- faltavam duas parcelas, as duas deterministas.
  // Spec: `specs/2026-07-30-dano-de-furia.md`

  /** Features da progressão + sub-escolhas, sem repetir e em ordem.
   *
   * As sub-escolhas entram porque o instinto do Bárbaro NÃO é feature: ele vem
   * do eixo `instinct`, e sem isto o dano de fúria nunca apareceria. */
  private idsDaFicha(): string[] {
    const ids = this.features.map((f) => f.id);
    for (const classe of this.ordem_de_classe) {
      ids.push(...this._subescolhas_de(classe));
    }
    const vistos = new Set<string>();
    const fora: string[] = [];
    for (const rid of ids) {
      if (rid && !vistos.has(rid)) { vistos.add(rid); fora.push(rid); }
    }
    return fora;
  }

  /** +2/+3/+4 pelo rank DA ARMA, dobrado pelo Greater.
   *
   * 26 das 27 classes concedem, e a base tinha `grants: []` em todas: todo
   * personagem do nível 7 pra cima estava com o dano errado na ficha. */
  private parcelaWeaponSpecialization(rank: string): ParcelaDeDano | null {
    let por_rank: Record<string, unknown> = {};
    let multiplicador = 1;
    let origem: string | null = null;
    for (const rid of this.idsDaFicha()) {
      const reg = this.base.opcional(rid);
      if (reg === null) continue;
      for (const g of listaDe(reg["grants"])) {
        const ws = dictDe(dictDe(g)["weapon_specialization"]);
        if (Object.keys(ws).length === 0) continue;
        if (verdadeiro(ws["por_rank"])) {
          // duas classes concedendo não somam: é a mesma tabela
          por_rank = dictDe(ws["por_rank"]);
          origem = origem ?? nome(reg);
        }
        if (verdadeiro(ws["multiplicador"])) {
          multiplicador = Math.max(multiplicador, inteiro(ws["multiplicador"]));
          origem = nome(reg);
        }
      }
    }
    const valor = inteiro(por_rank[rank]) * multiplicador;
    if (!valor) return null;
    return { tipo: "weapon_specialization", valor,
             origem: `${origem} (${rank})` };
  }

  /** `mode: upgrade` no Foundry: MAIOR vence, não soma. */
  private melhorGrau(rage_damage: Record<string, unknown>): number | null {
    let valor: number | null = null;
    for (const bruto of listaDe(rage_damage["graus"])) {
      const grau = dictDe(bruto);
      const exige = grau["requires"];
      if (verdadeiro(exige) && !this.avaliar(exige)[0]) continue;
      const v = inteiro(grau["valor"]);
      valor = valor === null ? v : Math.max(valor, v);
    }
    return valor;
  }

  /** [parcela incondicional, condicionais].
   *
   * O condicional NÃO entra no total: aparece com a condição escrita. É o
   * princípio zero -- marca, nunca esconde, nunca soma escondido. */
  private parcelasDeFuria(distancia: boolean):
      [ParcelaDeDano | null, DanoCondicional[]] {
    if (distancia) return [null, []];      // o `Rage` exclui arma a distância
    let melhor: ParcelaDeDano | null = null;
    const condicionais: DanoCondicional[] = [];
    for (const rid of this.idsDaFicha()) {
      const reg = this.base.opcional(rid);
      if (reg === null) continue;
      const rd = dictDe(reg["rage_damage"]);
      if (Object.keys(rd).length === 0) continue;
      const valor = this.melhorGrau(rd);
      if (valor === null) continue;
      if (verdadeiro(rd["condicao"])) {
        condicionais.push({ valor, origem: nome(reg),
                            condicao: pyStr(rd["condicao"]) });
      } else if (melhor === null || valor > (melhor.valor ?? 0)) {
        melhor = { tipo: "rage", valor, origem: nome(reg) };
      }
    }
    condicionais.sort((a, b) => b.valor - a.valor
                      || pyStr(a.origem).localeCompare(pyStr(b.origem)));
    return [melhor, condicionais];
  }

  private danoDecomposto(arma: Record<string, unknown>, dados: string,
                         mod_dano: number, rank: string,
                         distancia: boolean): DanoDecomposto {
    const parcelas: ParcelaDeDano[] = [
      { tipo: "dados", texto: dados, origem: nome(arma) },
    ];
    if (mod_dano) {
      parcelas.push({ tipo: "atributo", valor: mod_dano, origem: "FOR" });
    }
    const especializacao = this.parcelaWeaponSpecialization(rank);
    if (especializacao) parcelas.push(especializacao);
    const [furia, condicionais] = this.parcelasDeFuria(distancia);
    if (furia) parcelas.push(furia);
    const fixo = parcelas.reduce((s, p) => s + inteiro(p.valor), 0);
    return { parcelas, total: fixo ? `${dados}${comSinal(fixo)}` : dados,
             condicionais };
  }

  // -- regra 3: bônus derivado --------------------------------------------

  /** Regra 3: bônus total = nível_de_personagem + rank. Rank 0 = sem nível. */
  bonus(chave: string): number {
    const rank = this.proficiencias.get(chave) ?? "untrained";
    if (rank === "untrained") return 0;
    return this.nivel + RANK_BONUS[rank];
  }

  /** A sub-escolha que este personagem fez para a classe dada. */
  private _subclasse_de(classe_id: string): string | null {
    const todas = this._subescolhas_de(classe_id);
    return todas.length ? todas[0] : null;
  }

  /**
   * TODAS as sub-escolhas desta classe, na ordem da FONTE.
   *
   * A ordem é a da FONTE, e não a do documento. Uma classe tem VÁRIOS eixos
   * (o Mago tem `arcane-school`, `arcane-thesis` e `outras-opcoes`), e
   * percorrer as escolhas do jogador fazia a resposta depender de qual delas
   * vinha antes no array. Spec: `specs/2026-07-30-pendencias-do-review.md`
   *
   * Devolve LISTA por causa de `escolhe: N`: o eixo de ikon do Exemplar guarda
   * três escolhas no mesmo bloco, e uma só deixaria duas invisíveis ao
   * predicado.
   */
  private _subescolhas_de(classe_id: string): string[] {
    const classe = dictDe(this.base.opcional(classe_id));
    const escolhidas = new Set<unknown>(
      this._escolhas("subclasse").map((e) => e["pega"]));
    const saida: string[] = [];
    for (const b of listaDe(classe["subclasses"])) {
      for (const o of listaDe(dictDe(b)["opcoes"])) {
        if (escolhidas.has(o) && ehStr(o)) saida.push(o);
      }
    }
    return saida;
  }

  // -- avaliação do predicado ---------------------------------------------

  /**
   * Avalia o predicado contra este personagem. Devolve `[atende, motivos]`.
   *
   * **Nunca** é usado para negar uma escolha -- o princípio zero é explícito:
   * `requires` sugere e ordena, nunca bloqueia. Serve para o app dizer "estes
   * combinam com o que você tem" e para marcar o que está fora.
   */
  avaliar(predicado: unknown): [boolean, string[]] {
    return avaliarPredicado(this, predicado);
  }

  /** `getattr(self, f"_termo_{termo}", None)`: termo desconhecido não reprova. */
  termo(nome_do_termo: string, valor: unknown): ResultadoDeTermo | null {
    switch (nome_do_termo) {
      case "class_level": return this._termo_class_level(valor);
      case "character_level": return this._termo_character_level(valor);
      case "ability": return this._termo_ability(valor);
      case "proficiency": return this._termo_proficiency(valor);
      case "has": return this._termo_has(valor);
      case "subclass": return this._termo_subclass(valor);
      case "trait": return this._termo_trait(valor);
      // Termos de 2026-07-29 (spec `2026-07-29-termos-de-predicado.md`). O
      // Python despacha por convencao (`getattr(self, f"_termo_{termo}")`) e
      // aqui o switch e explicito -- esquecer uma linha faz o TS IGNORAR o
      // termo em silencio, que foi como 14 fichas divergiram do gabarito.
      case "sense": return this._termo_sense(valor);
      case "focus_pool": return this._termo_focus_pool(valor);
      case "has_actor": return this._termo_has_actor(valor);
      case "has_deity": return this._termo_has_deity(valor);
      case "deity": return this._termo_deity(valor);
      case "deity_font": return this._termo_deity_font(valor);
      case "deity_font_permitido": return this._termo_deity_font_permitido(valor);
      case "domain": return this._termo_domain(valor);
      case "deity_sanctification": return this._termo_deity_sanctification(valor);
      case "deity_favored_weapon_category":
        return this._termo_deity_favored_weapon_category(valor);
      case "proficiency_favored_weapon":
        return this._termo_proficiency_favored_weapon(valor);
      case "proficiency_divine_skill":
        return this._termo_proficiency_divine_skill(valor);
      case "spellcasting_tradition": return this._termo_spellcasting_tradition(valor);
      default: return null;
    }
  }

  /** `class_level` é o termo que só existe por causa da houserule. */
  private _termo_class_level(valor: unknown): ResultadoDeTermo {
    for (const [slug, exigencia] of Object.entries(dictDe(valor))) {
      const cid = `wb:class/${slug}`;
      const tenho = this.nivel_de(cid);
      const nome_da_classe = nomeOu(this.base.opcional(cid), slug);
      for (const [op, alvo] of Object.entries(dictDe(exigencia))) {
        if (!comparar(tenho, op, alvo)) {
          return [false, `exige ${nome_da_classe} nivel ${op} ${pyStr(alvo)}; `
                         + `tem ${tenho} (personagem ${this.nivel})`];
        }
      }
    }
    return [true, ""];
  }

  private _termo_character_level(valor: unknown): ResultadoDeTermo {
    for (const [op, alvo] of Object.entries(dictDe(valor))) {
      if (!comparar(this.nivel, op, alvo)) {
        return [false, `exige nivel de personagem ${op} ${pyStr(alvo)}; tem ${this.nivel}`];
      }
    }
    return [true, ""];
  }

  private _termo_ability(valor: unknown): ResultadoDeTermo {
    for (const [atributo, exigencia] of Object.entries(dictDe(valor))) {
      const tenho = this.atributos[atributo] ?? 10;
      for (const [op, alvo] of Object.entries(dictDe(exigencia))) {
        if (!comparar(tenho, op, alvo)) {
          return [false, `exige ${atributo.toUpperCase()} ${op} ${pyStr(alvo)}; tem ${tenho}`];
        }
      }
    }
    return [true, ""];
  }

  /**
   * O rank que a perícia teria se `excluir` não estivesse na ficha.
   *
   * Existe por causa do requisito circular: `acrobat-dedication` EXIGE
   * acrobatics trained e CONCEDE acrobatics. Desde que o motor passou a aplicar
   * grants de feat, o requisito passou a ser satisfeito pelo próprio feat, e a
   * ficha saía limpa onde antes sinalizava. Medido: 25 termos auto-satisfeitos
   * entre os 6.273 feats com `requires`.
   */
  private _rank_sem(chave: string, excluir: string | null): string {
    const atual = this.proficiencias.get(chave) ?? "untrained";
    if (!verdadeiro(excluir)) return atual;
    let restante: Rank = "untrained";
    for (const [rank, origem_id] of this.aplicacoes_de_proficiencia.get(chave) ?? []) {
      if (origem_id !== excluir) restante = melhorRank(restante, rank);
    }
    return restante;
  }

  /**
   * `weapon:aldori-dueling-sword` cai na CATEGORIA da arma.
   *
   * Ninguém preenche uma proficiência por arma nomeada -- a ficha guarda rank
   * por categoria (simple/martial/advanced). Sem esta ponte, um Guerreiro 6,
   * que é TREINADO em advanced desde o nível 1, aparecia untrained na Aldori
   * Dueling Sword e a `Aldori Duelist Dedication` saía como fora do requisito.
   * Achado comparando com o Pathbuilder, que libera as duas -- e ali ele está
   * certo.
   *
   * Rank NOMEADO ganha quando existe: feat que treina uma arma específica
   * escreve a chave própria, e ela é mais precisa que a categoria.
   */
  private _rank_de_arma(chave: string, excluir: string | null): string | null {
    if (!chave.startsWith("weapon:")) return null;
    // `.has()`, e não `Object.hasOwn`: `proficiencias` é um `Map`, e
    // `Object.hasOwn` sobre Map é SEMPRE false -- a guarda nunca disparava, e
    // no Python (`chave in self.proficiencias`) disparava. Divergência de
    // paridade dormente, item 95, que só tinha caminho de teste depois deste
    // item 75. Varrido o arquivo: dos 13 `Object.hasOwn`, era o único sobre Map.
    if (this.proficiencias.has(chave)) return null;
    const pedido = chave.slice("weapon:".length);

    // `weapon:*` pergunta "você é expert em ALGUMA arma?", e era letra morta:
    // `wb:weapon/*` não resolve e a chave literal voltava untrained SEMPRE,
    // deixando cinco feats inalcançáveis. Mesmo tratamento do `lore:*`.
    if (pedido === "*") {
      return melhorRankDe(CATEGORIAS_DE_ARMA.map((c) => this._rank_sem(c, excluir)));
    }

    const arma = this.base.opcional("wb:weapon/" + pedido);
    if (!arma) return null;
    const ranks: string[] = [];
    const categoria = arma["weapon_category"];
    if (ehStr(categoria)) ranks.push(this._rank_sem(categoria, excluir));
    // Feat de familiaridade não concede treino: REMAPEIA categoria. O melhor
    // entre nativa e remapeada, nunca só a remapeada -- ler o RAW ao pé da
    // letra faria um Guerreiro expert em marcial CAIR para trained ao pegar
    // `Archer Dedication`.
    // Spec: `specs/2026-07-30-proficiencia-de-arma-nomeada.md`
    for (const [igual_a, definicao] of this._remaps_de_arma()) {
      if (ehStr(igual_a) && this._arma_casa(arma, definicao)) {
        ranks.push(this._rank_sem(igual_a, excluir));
      }
    }
    return ranks.length ? melhorRankDe(ranks) : null;
  }

  /**
   * Todos os `weapon_proficiency` ativos na ficha, como `[igual_a, definicao]`.
   *
   * 91 ocorrências em 54 registros, e até agora nenhuma era lida nos dois
   * motores. Em cache porque `candidatos()` avalia milhares de feats por slot.
   */
  private _remaps_de_arma(): Array<[unknown, unknown]> {
    if (this._remaps_cache !== null) return this._remaps_cache;
    const saida: Array<[unknown, unknown]> = [];
    const fontes: Dict[] = [];
    for (const cid of this.ordem_de_classe) fontes.push(dictDe(this.base.get(cid)));
    for (const f of this.features) fontes.push(dictDe(f));
    for (const [, feat] of this._feats_efetivos()) fontes.push(feat);
    for (const reg of fontes) {
      for (const g of this._grants_de(reg)) {
        const wp = dictDe(g)["weapon_proficiency"];
        if (ehDict(wp)) saida.push([wp["igual_a"], wp["definicao"]]);
      }
    }
    this._remaps_cache = saida;
    return saida;
  }

  /**
   * A arma satisfaz este `definicao`?
   *
   * Gramática medida: 28 formas estruturais, mas só quatro seletores importam
   * -- `base`, `category`, `trait` e `group` cobrem 76 das 91 ocorrências
   * inteiras. Seletor desconhecido, ou valor dinâmico (`{item|flags...}`), NÃO
   * CASA -- e como o remap só ADICIONA rank, o princípio zero fica intacto por
   * construção: o que o motor não entende nunca vira reprovação.
   */
  private _arma_casa(arma: Dict, no: unknown): boolean {
    if (Array.isArray(no)) return no.every((x) => this._arma_casa(arma, x));
    if (ehDict(no)) {
      for (const op of ["or", "and", "not"] as const) {
        if (!(op in no)) continue;
        const alvo = no[op];
        const itens = Array.isArray(alvo) ? alvo : [alvo];
        if (op === "or") return itens.some((x) => this._arma_casa(arma, x));
        if (op === "and") return itens.every((x) => this._arma_casa(arma, x));
        return !this._arma_casa(arma, alvo);
      }
      return false;
    }
    if (!ehStr(no) || !no.startsWith("item:")) return false;
    const corte = no.indexOf(":", "item:".length);
    if (corte < 0) return false;                       // seletor sem valor
    const seletor = no.slice("item:".length, corte);
    const bruto = no.slice(corte + 1);
    if (bruto.includes("{")) return false;             // placeholder do VTT
    const valor = normSlug(bruto);
    if (seletor === "category") return normSlug(arma["weapon_category"] ?? "") === valor;
    if (seletor === "group") return normSlug(arma["group"] ?? "") === valor;
    if (seletor === "trait") {
      return listaDe(arma["traits"]).some((t) => normSlug(t) === valor);
    }
    if (seletor === "base" || seletor === "slug") {
      // `slug` tem, na nossa representação, a mesma semântica de `base`: o
      // sufixo do id. Ele caía no `return false` e o único remap que depende
      // dele nunca aplicava -- `Sister of the Golden Erinys Dedication` trata
      // `asp-coil` e `scourge` (as duas `martial`) como SIMPLES, e um Clérigo
      // com a dedicação lia untrained nas duas.
      // Spec: `specs/2026-07-31-atomo-slug.md`
      return normSlug(pyStr(arma["id"]).split("/").pop() ?? "") === valor;
    }
    return false;
  }

  /**
   * `Alcohol Lore` e `alcohol` são a mesma perícia.
   *
   * O sufixo ` Lore` sai antes do slug porque é assim que o parser escreve
   * (`extratores/feats.py`), e o apóstrofo some antes de hifenizar pelo mesmo
   * motivo -- o `slug()` de lá remove, o `normSlug()` daqui não.
   */
  private _slug_de_lore(bruto: unknown): string {
    const s = String(verdadeiro(bruto) ? bruto : "").trim().replace(/\s+lore$/i, "");
    return normSlug(s.replace(/['’]/g, ""));
  }

  /**
   * `lore:alcohol` cai na Lore da ficha chamada `Alcohol Lore`.
   *
   * Duas convenções para a mesma perícia: o predicado escreve o slug sem o
   * sufixo, a ficha guarda o nome humano com ele. Sem esta ponte, requisito de
   * Lore NOMEADA é insatisfazível por construção -- em 35 registros, nenhum
   * personagem atendia com nenhuma escolha. Achado comparando com o
   * Pathbuilder: um Barkeep, que tem Alcohol Lore em RAW, aparecia untrained
   * para o `Seasoned`.
   *
   * `lore:*` lê-se "alguma Lore" e devolve o MELHOR rank da ficha, porque o
   * requisito pode pedir mais que trained (`Scrollmaster` pede expert).
   */
  /**
   * RAW: Recall Knowledge é ação destas oito, e a lista é do livro -- não muda
   * com a fonte. Perception e Athletics NÃO entram, e é isso que faz o termo
   * discriminar.
   */
  private static PERICIAS_DE_RECALL = ["arcana", "crafting", "medicine", "nature",
                                       "occultism", "religion", "society"];

  /**
   * `skill:recall-knowledge` lê-se "alguma perícia com Recall Knowledge".
   *
   * Mesmo desenho de `lore:*` e `weapon:*`: devolve o MELHOR rank da ficha,
   * porque o requisito pode pedir mais que trained -- `Automatic Knowledge`
   * pede expert e `Masterful Obfuscation` pede master.
   * Spec: `specs/2026-07-31-pericia-de-recall-knowledge.md`
   */
  private _rank_de_recall(chave: string, excluir: string | null): string | null {
    if (chave !== "skill:recall-knowledge") return null;
    let melhor: string | null = null;
    for (const p of Personagem.PERICIAS_DE_RECALL) {
      melhor = melhorRank(melhor, this._rank_sem(p, excluir));
    }
    // qualquer Lore serve, e `lore:*` já responde a melhor delas
    return melhorRank(melhor, this._rank_de_lore("lore:*", excluir));
  }

  private _rank_de_lore(chave: string, excluir: string | null): string | null {
    if (!chave.startsWith("lore:")) return null;
    const pedido = chave.slice("lore:".length);
    let melhor: string | null = null;
    for (const k of this.proficiencias.keys()) {
      if (!k.startsWith("lore:")) continue;
      if (pedido !== "*" && this._slug_de_lore(k.slice("lore:".length)) !== pedido) continue;
      melhor = melhorRank(melhor, this._rank_sem(k, excluir));
    }
    return melhor;
  }

  private _termo_proficiency(valor: unknown): ResultadoDeTermo {
    const excluir = this._avaliando;
    for (const [chave, exigencia] of Object.entries(dictDe(valor))) {
      const tenho = this._rank_de_arma(chave, excluir)
        ?? this._rank_de_recall(chave, excluir)
        ?? this._rank_de_lore(chave, excluir)
        ?? this._rank_sem(chave, excluir);
      for (const [op, alvo] of Object.entries(dictDe(exigencia))) {
        const ia = indiceDeRank(tenho);
        const ib = indiceDeRank(alvo);
        if (!comparar(ia, op, ib)) {
          return [false, `exige ${chave} ${op} ${pyStr(alvo)}; tem ${tenho}`];
        }
      }
    }
    return [true, ""];
  }

  private _termo_has(valor: unknown): ResultadoDeTermo {
    // `pega` nem sempre é um id: `boosts_livres` guarda uma LISTA de atributos.
    // Filtrar por str antes do set, senão estoura no primeiro personagem que
    // distribuiu boosts.
    // RECORTE TEMPORAL: escolha feita DEPOIS da que está sendo avaliada não
    // pode satisfazer o pré-requisito dela. Sem isto, pegar `Dueling Dance` no
    // nível 2 e `Dueling Parry` no 12 -- ordem ilegal -- passava limpo, porque
    // no fim das contas o personagem "tem" as duas. A ficha é histórico, não
    // foto. Spec: `specs/2026-07-29-recorte-temporal-do-has.md`
    const ate = this._avaliando_em;
    const no_tempo = (e: Dict): boolean => {
      if (!ehInt(ate)) return true;              // sem contexto, olha tudo
      const em = obter(e, "em");
      // `criacao` antecede todo nível; `em` não numérico não recorta
      return !ehInt(em) || em <= ate;
    };
    const tudo = new Set<unknown>();
    for (const e of this._todas_escolhas()) {
      if (ehStr(e["pega"]) && no_tempo(e)) tudo.add(e["pega"]);
    }
    const excluir = this._avaliando;
    // `f.get("raiz")` do Python devolve None quando a chave FALTA -- e feature
    // de progressão de classe não tem `raiz`. Com `excluir` também None (todo
    // uso fora de `_checar_requisitos`: `candidatos`, `disponiveis`, atores),
    // `None != None` é falso e TODA feature de classe some do `has`. Portado
    // como está: `obter` devolve null na chave ausente, exatamente como o
    // `.get`. É o que faz `Call Wizardly Tools` sair como fora-do-requisito
    // ("exige ter Arcane Bond") num Mago que TEM Arcane Bond.
    for (const f of this.features) {
      // `excluir === null ||`, e não só a comparação: feature vinda da
      // PROGRESSÃO da classe não tem `raiz` (é null), e `_avaliando` também é
      // null fora de `_checar_requisitos` -- então `null !== null` dava false e
      // a feature era DESCARTADA. Em `candidatos()`, a pergunta central do app,
      // `_avaliando` nunca é setado: toda class-feature ficava invisível para o
      // `has`. 139 cláusulas em 135 registros.
      if (excluir === null || obter(f as unknown as Dict, "raiz") !== excluir) tudo.add(f.id);
    }
    // o que a cadeia concedeu conta como "tenho": no jogo não há diferença
    // entre o Streetwise que você pegou e o que a dedicação te deu. Mas o que o
    // PRÓPRIO feat concedeu não pode satisfazer o requisito dele.
    for (const c of this.concedidos) {
      if (excluir === null || c.raiz !== excluir) tudo.add(c.id);
    }
    for (const c of this.ordem_de_classe) tudo.add(c);
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg !== null) tudo.add(reg.id);
    }
    // comparar pelo id CANÔNICO dos dois lados: `requires` de 24 feats cita o
    // nome pré-remaster (`stunning-fist` pelo `stunning-blows`), e sem resolver
    // o alias o requisito nunca era satisfeito
    const canonico = this.base.resolver(valor);
    const resolvidos = new Set<unknown>();
    for (const t of tudo) resolvidos.add(this.base.resolver(t));
    if (resolvidos.has(canonico)) return [true, ""];
    // o GÊMEO também satisfaz. `Advanced Alchemy` existe como class-feature E
    // como feat, e desde 31/07 a classe concede o class-feature (o pack do UUID
    // do Foundry manda). Sem esta ponte, `efficient-alchemy`, que cita o FEAT,
    // deixou de ser atendido -- a quebra que o item 100 previa.
    // Spec: `specs/2026-07-31-gemeo-do-grant-item.md`
    for (const g of this.base.gemeos().get(String(canonico)) ?? []) {
      if (resolvidos.has(g)) return [true, ""];
    }
    return [false, `exige ter ${nomeOu(this.base.opcional(canonico), pyStr(valor))}`];
  }

  /** A camada do meio: nem classe, nem personagem. */
  private _termo_subclass(valor: unknown): ResultadoDeTermo {
    for (const [slug, alvo] of Object.entries(dictDe(valor))) {
      const escolhida = this._subclasse_de(`wb:class/${slug}`);
      // a sub-escolha pode existir com DOIS ids: `wb:instinct/animal` (AoN,
      // "Animal") e `wb:class-feature/animal-instinct` (Foundry, "Animal
      // Instinct"). Os 25 feats de instinto citam o segundo e a tela oferece o
      // primeiro. Spec: `specs/2026-07-30-instinto-com-dois-ids.md`
      // o gêmeo só entra na comparação se EXISTIR: sem esta guarda, um
      // personagem que ainda não escolheu subclasse (`escolhida` nulo) casava
      // com o `equivale_a` ausente e passava a atender TODO requisito.
      const gemeo = dictDe(this.base.opcional(alvo))["equivale_a"];
      // com `escolhe: N` a classe tem VÁRIAS sub-escolhas no mesmo eixo (os
      // três ikons do Exemplar). Comparar só com a primeira reprovaria
      // requisito que cita a segunda ou a terceira.
      const todas = new Set<unknown>(this._subescolhas_de(`wb:class/${slug}`));
      if (verdadeiro(escolhida)) todas.add(escolhida);
      const casa = todas.has(alvo) || (verdadeiro(gemeo) && todas.has(gemeo));
      if (!casa) {
        const nome_alvo = nomeOu(this.base.opcional(alvo), pyStr(alvo));
        const atual = verdadeiro(escolhida)
          ? nomeOu(this.base.opcional(escolhida), pyStr(escolhida)) : "nenhuma";
        return [false, `exige a sub-escolha ${nome_alvo}; tem ${atual}`];
      }
    }
    return [true, ""];
  }

  /**
   * Todo `grants.sense` que a ficha carrega, por tipo.
   *
   * 81 registros da base concedem sentido e **ninguém lia** -- mesmo padrão do
   * companheiro: o dado existia, o consumidor não. Isso deixava `low-light
   * vision` sem como ser respondido no pré-requisito, e a ficha sem dizer o que
   * o personagem enxerga.
   */
  private _sentidos(): Map<string, Dict> {
    if (this._cache_sentidos !== null) return this._cache_sentidos;
    const achados = new Map<string, Dict>();
    const origens: Array<[string, Dict]> = [];
    for (const [i] of this._feats_efetivos()) {
      origens.push([i, dictDe(this.base.opcional(i))]);
    }
    for (const f of this.features) {
      if (ehStr(f["id"])) origens.push([f["id"], dictDe(this.base.opcional(f["id"]))]);
    }
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg && ehStr(reg["id"])) origens.push([reg["id"], reg as Dict]);
    }
    for (const [origem_id, reg] of origens) {
      // `senses` no TOPO do registro, só em ancestria (37): `{low_light: true}`.
      // Sem isto, um Elfo (que declara só assim) não atendia `low-light vision`.
      for (const [chave, ligado] of Object.entries(dictDe(reg["senses"]))) {
        const slug = Personagem.slugDeSentido(chave);
        if (ligado && slug && !achados.has(slug)) {
          achados.set(slug, {
            tipo: chave, acuidade: null, alcance: null,
            origem: nomeOu(reg, origem_id),
          });
        }
      }
      for (const g of this._grants_de(reg)) {
        if (!ehDict(g) || !("sense" in g)) continue;
        // `sense` vem como dict na maioria e como STRING crua em parte dos
        // registros -- as duas formas existem na base
        const bruto = g["sense"];
        const sense = ehDict(bruto) ? bruto : { tipo: bruto };
        const tipo = Personagem.slugDeSentido(sense["tipo"]);
        if (!tipo || achados.has(tipo)) continue;
        achados.set(tipo, {
          tipo: sense["tipo"] ?? null,
          acuidade: sense["acuidade"] ?? null,
          alcance: sense["alcance"] ?? null,
          origem: nomeOu(reg, origem_id),
        });
      }
    }
    this._cache_sentidos = achados;
    return achados;
  }

  // a fonte escreve `low_light` e o pré-requisito diz `low-light vision`: sem o
  // alias, a mesma coisa vira duas chaves e o termo nunca casa
  static readonly ALIAS_DE_SENTIDO: Record<string, string> = {
    "low-light": "low-light-vision",
    "lowlight": "low-light-vision",
    "low-light-vision": "low-light-vision",
  };

  static slugDeSentido(bruto: unknown): string {
    const s = normSlug(ehStr(bruto) ? bruto : String(bruto ?? ""));
    return Personagem.ALIAS_DE_SENTIDO[s] ?? s;
  }

  /** `{"sense": "darkvision"}` -- o personagem enxerga assim? */
  private _termo_sense(valor: unknown): ResultadoDeTermo {
    const alvo = Personagem.slugDeSentido(valor);
    if (this._sentidos().has(alvo)) return [true, ""];
    return [false, `exige o sentido ${pyStr(valor)}`];
  }

  /**
   * `{"focus_pool": {">=": 1}}` -- o personagem tem pontos de foco?
   *
   * O motor já calculava o pool (regra 22: único, teto 3); faltava expor como
   * termo, e por isso `focus pool` e `ability to cast focus spells` caíam
   * inteiros em `requires_residuo`.
   */
  private _termo_focus_pool(valor: unknown): ResultadoDeTermo {
    for (const [op, alvo] of Object.entries(dictDe(valor))) {
      if (!comparar(this.focus_pool, op, inteiro(alvo))) {
        return [false, `exige focus pool ${op} ${pyStr(alvo)}; tem ${this.focus_pool}`];
      }
    }
    return [true, ""];
  }

  /**
   * `{"spellcasting_tradition": "arcane"}` -- conjura dessa tradição?
   *
   * 99 cláusulas em 27 arquétipos, e até 2026-07-29 nenhum dos dois motores
   * tinha o método. Termo sem handler não reprova (princípio zero), então o
   * `any` de `cathartic-mage-dedication` passava a vácuo e um Guerreiro 6
   * recebia seis dedicações de conjuração. Achado comparando com o Pathbuilder,
   * que barra as seis -- e ali ele está certo.
   *
   * Lê `this.conjuracao`, que já inclui a de CLASSE e a de ARQUETIPO.
   *
   * Spec: `specs/2026-07-29-termo-spellcasting-tradition.md`
   */
  private _termo_spellcasting_tradition(valor: unknown): ResultadoDeTermo {
    const alvo = normSlug(valor);
    if (!this.conjuracao.length) {
      return [false, `exige conjurar ${pyStr(valor)}; o personagem nao conjura`];
    }
    let indefinida = false;
    for (const c of this.conjuracao) {
      const bruta = dictDe(c)["tradicao"];
      if (!verdadeiro(bruta)) {
        // `null` é "varia com a subclasse e ela não foi escolhida", e NÃO "não
        // tem tradição" -- desde que `_conjuracao` passou a resolver (item 78),
        // a frase em prosa virou nulo. Tratar como ausência faria o Feiticeiro
        // sem bloodline ser REPROVADO, que é o oposto do princípio zero.
        indefinida = true;
        continue;
      }
      if (normSlug(bruta) === alvo) return [true, ""];
      if (!TRADICOES.includes(normSlug(bruta))) indefinida = true;
    }
    if (indefinida) {
      // princípio zero: a tradição está em prosa (item 78) -- o motor não sabe
      // qual é e não reprova sobre o que não sabe. A ficha JÁ mostra a string,
      // então a marca existe e não vira aviso aqui: `candidatos()` avalia
      // milhares de feats por slot e o log afogaria.
      return [true, ""];
    }
    const tem = ordenarTextos([...new Set(this.conjuracao
      .map((c) => dictDe(c)["tradicao"])
      .filter((t) => verdadeiro(t))
      .map((t) => pyStr(t)))]).join(", ") || "nenhuma";
    return [false, `exige conjurar ${pyStr(valor)}; tem ${tem}`];
  }

  /**
   * `{"has_actor": "companheiro"}` -- alguma coisa na ficha concede um?
   *
   * A pergunta é sobre ter DIREITO ao bicho, não sobre já ter escolhido a
   * espécie: o pré-requisito de `Mature Animal Companion` fala do primeiro.
   */
  private _termo_has_actor(valor: unknown): ResultadoDeTermo {
    const tipo = String(valor ?? "").toLowerCase();
    if (this.concessoes_de_ator.some((c) => c.tipo === tipo)) return [true, ""];
    return [false, `exige ter ${tipo}`];
  }

  // -- divindade ----------------------------------------------------------
  // Espelha `_termo_has_deity`/`_termo_deity`/`_termo_deity_font`/`_termo_domain`
  // do Python. Spec: specs/2026-07-30-divindade-na-ficha.md

  /** O registro da divindade escolhida, ou `null`. */
  divindade(): Registro | null {
    for (const bloco of this.slots_de_subclasse) {
      if (bloco.eixo === "deity" && bloco.escolhido) {
        return this.base.opcional(bloco.escolhido);
      }
    }
    return null;
  }

  /** O que a ficha mostra da divindade: nome resolvido de dominio e arma. */
  private _divindade_da_ficha(): VisaoDeDivindade | null {
    const d = this.divindade();
    if (d === null) return null;
    const nomes = (ids: unknown): { id: string; nome: string }[] =>
      (ehLista(ids) ? ids : []).map((i) => ({
        id: String(i),
        nome: nomeOu(this.base.opcional(String(i)), String(i)),
      }));
    const dominios = dictDe(d["domains"]);
    const minusculas = (v: unknown) =>
      (ehLista(v) ? v : []).map((x) => String(x).toLowerCase());
    return {
      id: String(d["id"]),
      nome: nomeOu(d, ""),
      fonte_divina: minusculas(d["divine_font"]),
      atributo_divino: minusculas(d["divine_attribute"]),
      dominios: nomes(dominios["primary"]),
      dominios_alternativos: nomes(dominios["alternate"]),
      arma_favorita: nomes(d["favored_weapon"]),
      santificacao: (d["sanctification"] ?? null) as string | null,
    };
  }

  private _termo_has_deity(valor: unknown): ResultadoDeTermo {
    const quer = Boolean(valor);
    const tem = this.divindade() !== null;
    if (tem === quer) return [true, ""];
    return [false, quer ? "exige seguir uma divindade"
                        : "exige NAO seguir divindade"];
  }

  private _termo_deity(valor: unknown): ResultadoDeTermo {
    const crus = ehLista(valor) ? valor : [valor];
    const alvos = new Set(crus.map((a) => this.base.resolver(String(a)) as string));
    const d = this.divindade();
    if (d && alvos.has(this.base.resolver(String(d["id"])) as string)) return [true, ""];
    const nomes = [...alvos]
      .map((a) => nomeOu(this.base.opcional(String(a)), String(a)))
      .sort().join(", ");
    return [false, `exige adorar ${nomes}; `
                   + `tem ${d ? nomeOu(d, "") : "nenhuma divindade"}`];
  }

  /** A fonte divina que o jogador pegou, se pegou. */
  private _fonte_escolhida(): string | null {
    for (const bloco of this.slots_de_subclasse) {
      if (bloco.eixo === "divine-font" && bloco.escolhido) {
        return bloco.escolhido.split("/").pop()!.toLowerCase();
      }
    }
    return null;
  }

  /**
   * `{"deity_font_permitido": "heal"}` -- a DIVINDADE permite esta fonte?
   *
   * É o `requires` das duas opções do eixo, e espelha o predicado do Foundry
   * (`deity:primary:font:heal`). Separado de `deity_font` para não ser
   * circular: a opção `heal` não pode exigir que a fonte já seja `heal`.
   */
  private _termo_deity_font_permitido(valor: unknown): ResultadoDeTermo {
    const alvo = String(valor ?? "").toLowerCase();
    const d = this.divindade();
    if (d === null) return [false, `exige divindade que conceda fonte ${alvo}`];
    const cru = d["divine_font"];
    const fontes = (ehLista(cru) ? cru : []).map((f) => String(f).toLowerCase());
    if (fontes.includes(alvo) || fontes.length === 0) return [true, ""];
    return [false, `${nomeOu(d, "")} concede ${fontes.join(", ")}, nao ${alvo}`];
  }

  /**
   * `{"deity_font": "heal"}` -- a fonte do PERSONAGEM é esta?
   *
   * Com o eixo `divine-font` a pergunta tem resposta exata quando o jogador
   * escolheu. Sem escolha, vale o comportamento antigo: responde pela PERMISSÃO
   * da divindade e não reprova quando ela permite as duas -- princípio zero.
   */
  private _termo_deity_font(valor: unknown): ResultadoDeTermo {
    const alvo = String(valor ?? "").toLowerCase();
    const d = this.divindade();
    if (d === null) {
      return [false, `exige fonte divina ${alvo}; nao segue divindade`];
    }
    const escolhida = this._fonte_escolhida();
    if (escolhida !== null) {
      if (escolhida === alvo) return [true, ""];
      return [false, `exige fonte divina ${alvo}; a escolhida foi ${escolhida}`];
    }
    const cru = d["divine_font"];
    const fontes = (ehLista(cru) ? cru : []).map((f) => String(f).toLowerCase());
    if (fontes.includes(alvo)) return [true, ""];
    if (fontes.length === 0) return [true, ""];
    return [false, `exige fonte divina ${alvo}; ${nomeOu(d, "")} concede `
                   + `${fontes.join(", ")}`];
  }

  /**
   * `{"deity_sanctification": "holy"}` -- cabe na divindade escolhida?
   *
   * A base guarda `sanctification` como lista achatada, e inferir dela ("uma
   * opção só = obrigatória") erraria em 408 divindades: a prosa do AoN diz
   * `can choose holy` em 265 delas. O modal vem de `sanctification_escolha`.
   *
   * `none` cabe quando a divindade NÃO OBRIGA nenhuma -- é literalmente o
   * predicado do Foundry (`nor must:holy, must:unholy`).
   */
  private _termo_deity_sanctification(valor: unknown): ResultadoDeTermo {
    const alvo = String(valor ?? "").toLowerCase();
    const d = this.divindade();
    if (d === null) {
      return [false, `exige santificacao ${alvo}; nao segue divindade`];
    }
    const cru = d["sanctification"];
    const permite = (ehLista(cru) ? cru : []).map((s) => String(s).toLowerCase());
    const obriga = String(d["sanctification_escolha"] ?? "") === "must";
    const nomeDeus = nomeOu(d, "");
    if (alvo === "none") {
      if (obriga && permite.length) {
        return [false, `${nomeDeus} obriga santificacao (${permite.join(", ")})`];
      }
      return [true, ""];
    }
    if (permite.includes(alvo)) return [true, ""];
    return [false, `exige santificacao ${alvo}; ${nomeDeus} `
                   + (permite.length ? `permite ${permite.join(", ")}`
                                     : "nao tem santificacao")];
  }

  private _termo_domain(valor: unknown): ResultadoDeTermo {
    const crus = ehLista(valor) ? valor : [valor];
    const alvos = new Set(crus.map((a) => this.base.resolver(String(a)) as string));
    const d = this.divindade();
    if (d === null) {
      return [false, "exige dominio de divindade; nao segue divindade"];
    }
    const dominios = dictDe(d["domains"]);
    const meus = new Set<string>();
    for (const chave of ["primary", "alternate"]) {
      const lista = dominios[chave];
      for (const x of (ehLista(lista) ? lista : [])) {
        meus.add(this.base.resolver(String(x)) as string);
      }
    }
    for (const a of alvos) if (meus.has(a)) return [true, ""];
    const nomes = [...alvos]
      .map((a) => nomeOu(this.base.opcional(String(a)), String(a)))
      .sort().join(", ");
    return [false, `exige dominio ${nomes}; ${nomeOu(d, "")} nao o concede`];
  }

  // -- arma favorita e perícia divina --------------------------------------
  // Spec: `specs/2026-07-30-pericia-divina-e-arma-favorita.md`

  /** Os registros de arma que a divindade escolhida favorece. */
  private armasFavoritas(): Registro[] {
    const d = this.divindade();
    if (d === null) return [];
    return listaDe(d["favored_weapon"])
      .map((a) => this.base.opcional(String(a)))
      .filter((r): r is Registro => r !== null);
  }

  /** `{"deity_favored_weapon_category": "simple"}` -- Deadly Simplicity.
   *
   * Pergunta pela ARMA da divindade, não pela proficiência do personagem: são
   * dois termos porque são duas perguntas, e `deadly-simplicity` faz as duas
   * em cláusulas separadas. */
  private _termo_deity_favored_weapon_category(valor: unknown): ResultadoDeTermo {
    const alvo = String(valor ?? "").toLowerCase();
    const d = this.divindade();
    if (d === null) {
      return [false, `exige arma favorita ${alvo}; nao segue divindade`];
    }
    const armas = this.armasFavoritas();
    // `unarmed` não é `weapon_category` -- é trait, e é assim que o RAW
    // descreve a arma favorita de quem luta desarmado
    for (const arma of armas) {
      const traits = new Set(listaDe(arma["traits"]).map((t) => String(t).toLowerCase()));
      if (String(arma["weapon_category"] ?? "").toLowerCase() === alvo
          || traits.has(alvo)) return [true, ""];
    }
    const tem = armas.map((a) => `${nomeOu(a, "")} (${a["weapon_category"]})`)
      .join(", ") || "nenhuma";
    return [false, `exige arma favorita ${alvo}; ${nomeOu(d, "")} favorece ${tem}`];
  }

  /** Compara rank contra `{">=": "expert"}`, o formato dos outros termos. */
  private rankPorExigencia(tenho: string, exigencia: unknown,
                           rotulo: string): ResultadoDeTermo {
    for (const [op, alvo] of Object.entries(dictDe(exigencia))) {
      const ia = indiceDeRank(tenho);
      const ib = indiceDeRank(String(alvo));
      if (!comparar(ia, op, ib)) {
        return [false, `exige ${rotulo} ${op} ${alvo}; tem ${tenho}`];
      }
    }
    return [true, ""];
  }

  /** O personagem tem rank X NA arma favorita da divindade? */
  private _termo_proficiency_favored_weapon(valor: unknown): ResultadoDeTermo {
    const d = this.divindade();
    if (d === null) {
      return [false, "exige proficiencia na arma favorita; nao segue divindade"];
    }
    const armas = this.armasFavoritas();
    if (armas.length === 0) {
      return [false, `${nomeOu(d, "")} nao tem arma favorita na base`];
    }
    const excluir = this._avaliando;
    let melhor = "untrained";
    let nome_da_arma: string | null = null;
    for (const arma of armas) {
      const slug = String(arma["id"]).split("/").pop() ?? "";
      const tenho = this._rank_de_arma(`weapon:${slug}`, excluir)
        ?? (this.proficiencias.get(
              String(arma["weapon_category"] ?? "simple")) ?? "untrained");
      if (indiceDeRank(tenho) >= indiceDeRank(melhor)) {
        melhor = tenho;
        nome_da_arma = nomeOu(arma, "");
      }
    }
    return this.rankPorExigencia(melhor, valor, `proficiencia em ${nome_da_arma}`);
  }

  /** O personagem tem rank X na perícia divina da divindade?
   *
   * `divine_skill` é a décima lacuna de leitura: estava na prosa do AoN de 475
   * divindades e a base tinha zero. As 13 sem o campo são filosofias, e para
   * elas a resposta é não -- com o motivo escrito. */
  private _termo_proficiency_divine_skill(valor: unknown): ResultadoDeTermo {
    const d = this.divindade();
    if (d === null) return [false, "exige a pericia divina; nao segue divindade"];
    const pericia = String(d["divine_skill"] ?? "");
    if (!pericia) return [false, `${nomeOu(d, "")} nao tem pericia divina`];
    const tenho = this._rank_sem(pericia, this._avaliando);
    return this.rankPorExigencia(tenho, valor, `${pericia} (pericia divina)`);
  }

  private _termo_trait(valor: unknown): ResultadoDeTermo {
    const alvos = ehLista(valor) ? valor : [valor];
    const meus = new Set<string>();
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg !== null) {
        for (const t of listaDe(reg["traits"])) meus.add(String(t).toLowerCase());
      }
    }
    for (const cid of this.ordem_de_classe) {
      const n = this.base.get(cid)["name"];
      meus.add(verdadeiro(n) ? String(n).toLowerCase() : "");
    }
    const faltando = alvos.filter((a) => !meus.has(String(a).toLowerCase()));
    return [faltando.length === 0,
            faltando.length > 0 ? `exige o trait ${pyRepr(faltando)}` : ""];
  }

  // -- o que o app pergunta: slots abertos e candidatos por slot -----------

  /**
   * Tudo que está por preencher, no estado atual.
   *
   * A terceira pergunta do construtor. O motor já sabia responder "o que eu
   * tenho" (`visao`) e "o que está errado" (`fora_do_requisito`, `avisos`);
   * faltava "o que falta escolher", que é o que guia a tela.
   */
  slots_abertos(): SlotAberto[] {
    const abertos: SlotAberto[] = [];
    const gasto_em = new Map<unknown, unknown[]>();
    for (const e of this._todas_escolhas()) {
      empurrar(gasto_em, obter(e, "slot"), obter(e, "em"));
    }

    const removerUm = (lista: unknown[], v: unknown): boolean => {
      const i = lista.indexOf(v);
      if (i < 0) return false;
      lista.splice(i, 1);
      return true;
    };

    for (const [slot, cadencia] of Personagem.SLOT_PARA_CADENCIA) {
      const usados = [...(gasto_em.get(slot) ?? [])];
      for (const nivel of this.slots.get(cadencia) ?? []) {
        if (removerUm(usados, nivel)) continue;
        abertos.push({
          slot, em: nivel, kind: "feat", escolhe: 1,
          rotulo: `${slot.replaceAll("_", " ")} (nivel ${nivel})`,
        });
      }
    }

    const usados = [...(gasto_em.get("skill_increase") ?? [])];
    for (const nivel of this.aumentos_de_pericia) {
      if (removerUm(usados, nivel)) continue;
      abertos.push({
        slot: "skill_increase", em: nivel, kind: "skill", escolhe: 1,
        rotulo: `aumento de pericia (nivel ${nivel})`,
      });
    }

    // o slot que um feat ou heranca CONCEDEU. Identidade pela `flag` do
    // ChoiceSet e nao pelo nivel: dois concessores podem cair no mesmo nivel.
    const usadosConc = new Set<unknown>();
    for (const e of this._todas_escolhas()) {
      if (obter(e, "slot") === "feat_concedido") usadosConc.add(obter(e, "flag"));
    }
    for (const bloco of this.slots_concedidos) {
      if (usadosConc.has(bloco.flag)) continue;
      abertos.push({
        // o `slot` continua `feat_concedido` mesmo carregando magia:
        // renomear obrigaria a migrar documento salvo, fixture e ficha de
        // exemplo, e o `kind` já diz o que o slot pede. Dívida de nome.
        slot: "feat_concedido", em: bloco.em, kind: bloco.tipo || "feat",
        escolhe: 1, flag: bloco.flag,
        rotulo: `${bloco.tipo || "feat"} concedido por ${bloco.origem}`,
      });
    }

    for (const bloco of this.slots_de_subclasse) {
      // `escolhe: N` -- o mesmo formato que `boosts_livres` já usava: um slot
      // só, dizendo QUANTAS faltam.
      const faltamSub = bloco.escolhe - bloco.escolhidos.length;
      if (faltamSub > 0) {
        abertos.push({
          slot: "subclasse", em: bloco.nivel, kind: bloco.eixo,
          escolhe: faltamSub, opcoes: bloco.opcoes,
          rotulo: `${bloco.classe} / ${pyStr(bloco.eixo)}`,
        });
      }
    }

    const faltam = this.boosts_direito - this.boosts_declarados;
    if (faltam > 0) {
      abertos.push({
        slot: "boosts_livres", em: "criacao", kind: "ability",
        escolhe: faltam, fontes: this.boosts_pendentes,
        rotulo: `boosts de atributo (${faltam} a escolher)`,
      });
    }

    for (const e of this.escolhas_de_grant) {
      if (e.escolhido === null) {
        abertos.push({
          slot: "escolha_de_grant", em: "criacao", kind: "grant", escolhe: 1,
          opcoes: e.opcoes, flag: e.flag, origem: e.origem,
          rotulo: `${e.nome} / ${pyStr(e.flag)}`,
        });
      }
    }

    // sem esta entrada a tela nunca oferece o picker de perícia, e o orçamento
    // continua sendo um número que ninguém gasta
    const faltam_pericias = this.pericias_livres - this.pericias_declaradas;
    if (faltam_pericias > 0) {
      abertos.push({
        slot: "pericias_livres", em: "criacao", kind: "skill",
        escolhe: faltam_pericias, fontes: this.pericias_livres_detalhe,
        rotulo: `pericias treinadas (${faltam_pericias} a escolher)`,
      });
    }

    // concessão de ator sem ator: o feat foi pego e a espécie não foi
    // escolhida. `preenchida` é marcado em `_atores`, que já rodou.
    for (const c of this.concessoes_de_ator) {
      if (c.preenchida) continue;
      abertos.push({
        // `em` do slot e `number | "criacao" | null`: a concessao guarda o
        // nivel como `unknown` (vem do documento), entao estreita aqui
        slot: c.tipo, em: ehInt(c.em) ? c.em : "criacao",
        kind: c.escolhe, escolhe: 1, origem: c.origem, opcoes_ids: c.opcoes,
        rotulo: `${c.tipo} -- ${c.origem_nome}`,
      });
    }

    for (const slot of ["ancestralidade", "heranca", "background"] as const) {
      const atributo = { ancestralidade: this.ancestria, heranca: this.heranca,
                         background: this.background }[slot];
      if (atributo === null) {
        abertos.push({
          slot, em: "criacao",
          kind: { ancestralidade: "ancestry", heranca: "heritage",
                  background: "background" }[slot],
          escolhe: 1, rotulo: slot,
        });
      }
    }

    return ordenarPor(abertos, (s) => [ehInt(s.em) ? s.em : 0, s.slot]);
  }

  /**
   * Elegibilidade de SLOT -- que é coisa diferente de requisito.
   *
   * O slot FILTRA por tipo; `requires` só ORDENA (princípio zero). Um feat sem
   * trait `archetype` não é candidato ao slot gratuito -- isso não é bloquear
   * escolha, é a definição do slot. Já um feat de arquétipo cujo requisito o
   * personagem não atende APARECE, marcado.
   */
  /** `item:X:Y` -> onde X vive no nosso registro. Medido nos 101 ChoiceSet com
   *  `itemType: "feat"`: trait 291, level 94, category 56, rarity 8. */
  private static CAMPO_DO_ATOMO: Record<string, string> = {
    trait: "traits", level: "level", category: "feat_category", rarity: "rarity",
    // `tag` entrou em 2026-07-31: os filtros da base usam `item:tag` 54 vezes e
    // o motor o IGNORAVA -- e átomo ignorado conta como SATISFEITO. Certo para
    // estreitar slot de feat, destrutivo para definir eixo.
    // Spec: `specs/2026-07-31-tag-e-eixo-por-query.md`
    tag: "tags",
    // `slug` entrou com o slot concedido genérico -- ver `_atomo_de_filtro`
    slug: "slug",
  };

  /**
   * O mesmo `requires` sem a clausula de nivel de personagem.
   *
   * A prosa do `Ancient Elf` e explicita: "You gain the multiclass dedication
   * feat for that class, **even though you don't meet its level prerequisite**.
   * You must still meet its **other** prerequisites." O slot concedido dispensa
   * o nivel e mantem todo o resto.
   */
  private _sem_gate_de_nivel(requires: unknown): unknown {
    if (!ehDict(requires)) return requires;
    if ("character_level" in requires) return null;
    const saida: Dict = {};
    for (const [chave, valor] of Object.entries(requires)) {
      if ((chave === "all" || chave === "any" || chave === "none") && Array.isArray(valor)) {
        const limpo = valor.map((v) => this._sem_gate_de_nivel(v)).filter((c) => c !== null);
        if (limpo.length > 0) saida[chave] = limpo;
      } else {
        saida[chave] = valor;
      }
    }
    return Object.keys(saida).length > 0 ? saida : null;
  }

  /** Um atomo do filtro contra um registro. `null` = nao sei avaliar -- e
   *  `null` nao e `false`: 153 atomos carregam referencia dinamica, e tratar o
   *  que nao se avalia como reprovacao esvaziaria o slot em silencio. */
  private _atomo_de_filtro(reg: Registro, atomo: string): boolean | null {
    if (atomo.includes("{")) return null;
    const partes = atomo.split(":");
    if (partes.length < 3 || partes[0] !== "item") return null;
    const campo = Personagem.CAMPO_DO_ATOMO[partes[1]];
    if (campo === undefined) return null;
    let alvo = partes.slice(2).join(":");
    if (campo === "slug") {
      // `slug` não é campo: é o sufixo do id, ou um alias. 60 dos 69 átomos
      // `item:slug` vivem nos filtros de `tipo: spell`, e átomo ignorado conta
      // como SATISFEITO -- sem isto o slot de `Dragon Spit` ofereceria as
      // 1.638 magias da base em vez de 4. `normSlug` resolve de quebra o
      // defeito de fonte `item:slug:dispel magic`, com espaço no meio.
      alvo = normSlug(alvo);
      if (normSlug(pyStr(reg["id"]).split("/").pop() ?? "") === alvo) return true;
      return listaDe((reg as Dict)["aliases"]).some((a) => normSlug(pyStr(a)) === alvo);
    }
    const valor = (reg as Dict)[campo];
    if (campo === "traits" || campo === "tags") {
      return listaDe(valor).map((t) => pyStr(t)).includes(alvo);
    }
    if (campo === "level") return ehInt(valor) && String(valor) === alvo;
    return pyStr(valor ?? "") === alvo;
  }

  /**
   * O filtro RECORTA o slot, como `_aceita_no_slot` -- nao ordena.
   *
   * Gramatica medida na fonte: lista no topo e AND; `or` 28, `and` 16, `not`
   * 37, `nor` 2, `xor` 8, `lte` 59. Atomo desconhecido NAO reprova: conta em
   * `filtro_ignorado` e vale como satisfeito.
   */
  /**
   * O nó não tem NENHUM átomo que o motor saiba avaliar.
   *
   * Só serve para `not`/`nor`, onde a coerção do desconhecido para satisfeito
   * se inverte e vira reprovação geral. Em `and`/`or` ela alarga, que é o lado
   * certo do princípio zero, e nada aqui muda.
   */
  private _filtro_indecidivel(no: unknown): boolean {
    if (ehStr(no)) {
      return no.includes("{") || this._atomo_de_filtro({} as Registro, no) === null;
    }
    if (Array.isArray(no)) return no.every((x) => this._filtro_indecidivel(x));
    if (ehDict(no)) return Object.values(no).every((v) => this._filtro_indecidivel(v));
    return false;
  }

  private _casa_filtro(reg: Registro, filtro: unknown): boolean {
    if (filtro === null || filtro === undefined || filtro === true) return true;
    if (ehStr(filtro)) {
      const r = this._atomo_de_filtro(reg, filtro);
      if (r === null) {
        this.filtro_ignorado[filtro] = (this.filtro_ignorado[filtro] ?? 0) + 1;
        return true;
      }
      return r;
    }
    if (Array.isArray(filtro)) return filtro.every((f) => this._casa_filtro(reg, f));
    if (!ehDict(filtro)) return true;
    for (const [op, arg] of Object.entries(filtro)) {
      const itens = Array.isArray(arg) ? arg : [arg];
      if (op === "or") {
        if (!itens.some((i) => this._casa_filtro(reg, i))) return false;
      } else if (op === "and") {
        if (!itens.every((i) => this._casa_filtro(reg, i))) return false;
      } else if (op === "not") {
        // o default "átomo ignorado conta como SATISFEITO" é seguro sob
        // `and`/`or`, onde ALARGA -- e se inverte sob `not`, onde passa a
        // REPROVAR tudo. `Adopted Ancestry` filtra
        // `{"not": "item:slug:{actor|...}"}`, e com a coerção para true o
        // `not` rejeitava as 50 ancestralidades e o slot nascia VAZIO.
        if (this._filtro_indecidivel(itens)) continue;
        if (itens.every((i) => this._casa_filtro(reg, i))) return false;
      } else if (op === "nor") {
        if (this._filtro_indecidivel(itens)) continue;   // mesma inversão
        if (itens.some((i) => this._casa_filtro(reg, i))) return false;
      } else if (op === "xor") {
        if (itens.filter((i) => this._casa_filtro(reg, i)).length !== 1) return false;
      } else if (op === "lte" || op === "lt" || op === "gte" || op === "gt") {
        if (itens.length !== 2 || !pyStr(itens[0]).endsWith(":level")) {
          this.filtro_ignorado[op] = (this.filtro_ignorado[op] ?? 0) + 1;
          continue;
        }
        const nivel = (reg as Dict)["level"];
        // o lado direito e inteiro em 32 dos 34 e `self:level` em um --
        // `Rogue Dedication` concede "um feat de pericia de nivel ate o seu".
        // Tratar a referencia como nao-inteiro reprovava TODOS os feats de
        // pericia e esvaziava o slot em silencio.
        const teto = itens[1] === "self:level" ? this.nivel : itens[1];
        if (!ehInt(teto)) {
          const k = pyStr(itens[1]);
          this.filtro_ignorado[k] = (this.filtro_ignorado[k] ?? 0) + 1;
          continue;
        }
        if (!ehInt(nivel)) return false;
        const ok = op === "lte" ? nivel <= teto : op === "lt" ? nivel < teto
                 : op === "gte" ? nivel >= teto : nivel > teto;
        if (!ok) return false;
      } else {
        this.filtro_ignorado[op] = (this.filtro_ignorado[op] ?? 0) + 1;
      }
    }
    return true;
  }

  /** Em que nivel o feat entrou. `criacao` quando veio pela cadeia. */
  private _nivel_do_feat(wbId: string): number | "criacao" {
    for (const e of listaDe(this.doc["escolhas"])) {
      const d = dictDe(e);
      if (d["pega"] === wbId || d["valor"] === wbId) {
        return (d["em"] ?? "criacao") as number | "criacao";
      }
    }
    return "criacao";
  }

  private _aceita_no_slot(slot: string, r: Registro): boolean {
    const traits = new Set(listaDe(r["traits"]).map((t) => String(t).toLowerCase()));
    if (slot === "free_archetype") return traits.has("archetype");
    if (slot === "skill_feat") return traits.has("skill");
    if (slot === "general_feat") return traits.has("general");
    if (slot === "ancestry_feat") {
      const nomes = new Set<string>();
      nomes.add(verdadeiro((this.ancestria ?? {})["name"])
        ? String((this.ancestria as Registro)["name"]).toLowerCase() : "");
      nomes.add(verdadeiro((this.heranca ?? {})["name"])
        ? String((this.heranca as Registro)["name"]).toLowerCase() : "");
      nomes.delete("");
      for (const n of nomes) if (traits.has(n)) return true;
      return false;
    }
    if (slot === "class_feat") {
      // feat de classe do personagem. Um feat pode servir a várias classes, e
      // basta pertencer a UMA das que ele tem.
      for (const c of this.ordem_de_classe) {
        const n = this.base.get(c)["name"];
        const chave = verdadeiro(n) ? String(n).toLowerCase() : "";
        if (traits.has(chave)) return true;
      }
      // RAW: feat de ARQUÉTIPO pode ser gasto num slot de feat de classe -- é
      // literalmente assim que se entra num arquétipo no PF2e oficial. Nenhuma
      // das 226 dedicações carrega trait de classe, então exigir a trait da
      // classe as tornava inalcançáveis por este slot, e a única porta para
      // dedicação virava o slot de Free Archetype. Num projeto cuja regra da
      // casa SUBSTITUI a dedicação, o caminho RAW tem de continuar existindo
      // para poder ser comparado com ela.
      //
      // A regra 23 (exclusão mútua entre nível de classe e dedicação da mesma
      // classe) continua valendo: `_veto_dedicacao_da_propria_classe` marca a
      // dedicação do próprio Guerreiro como fora-do-requisito, sem escondê-la.
      return traits.has("archetype");
    }
    return true;
  }

  /**
   * O que cabe NESTE slot, ordenado -- nunca filtrado por requisito.
   *
   * `disponiveis(kind=...)` devolve os 6.273 feats da base; uma tela de escolha
   * não pode receber isso. Aqui o conjunto de entrada é recortado pela
   * elegibilidade do slot, e o `requires` continua só ordenando.
   */
  candidatos(slot: string, em: number | string | null = null,
             limite: number | null = null, flag: string | null = null): Candidato[] {
    if (slot === "boosts_livres") {
      return ATRIBUTOS.map((a) => ({
        id: a, nome: a.toUpperCase(), level: null,
        atende: true, motivos: [], ja_pego: false,
      }));
    }

    if (slot === "companheiro" || slot === "familiar" || slot === "eidolon") {
      // As `opcoes` do concessor ORDENAM, não filtram: Drake Rider diz "riding
      // drake, riding dragonet, or another animal companion", e mesmo o Rough
      // Rider, que fixa o lobo, não some com o resto -- princípio zero aplicado
      // à espécie.
      const preferidas = new Set<string>();
      const kinds = new Set<string>();
      for (const c of this.concessoes_de_ator) {
        if (c.tipo !== slot) continue;
        kinds.add(c.escolhe);
        if (em === null || c.em === em) for (const o of c.opcoes) preferidas.add(o);
      }
      if (kinds.size === 0) kinds.add("animal-companion");
      // `stats` separa ESPÉCIE de ESPECIALIZAÇÃO: dos 113 registros do kind, 17
      // são Ambusher, Nimble, Savage e companhia -- graus que não têm stat
      // block e não cabem neste slot. Elegibilidade de slot, não requisito.
      //
      // Só vale no companheiro: os 39 `familiar-specific` não têm `stats` --
      // a fonte não publica número para eles --, e exigir o campo esvaziaria a
      // lista. Spec `specs/2026-07-30-familiar-e-eidolon-concedidos.md`.
      const especies = [...this.base.por_id.values()]
        .filter((r) => kinds.has(String(r.kind))
                && (slot !== "companheiro" || verdadeiro(r["stats"])));
      const escolha: Candidato[] = especies.map((r) => {
        const [atende, motivos] = this.avaliar(r["requires"]);
        return {
          id: r.id, nome: nome(r), level: ehInt(r["level"]) ? r["level"] : null,
          atende, motivos, ja_pego: false, sugerida: preferidas.has(r.id),
        };
      });
      const ord = ordenarPor(escolha, (x) => [!x.sugerida, !x.atende, x.nome ?? ""]);
      return limite ? ord.slice(0, limite) : ord;
    }

    let registros: Array<Registro | null>;
    if (slot === "subclasse") {
      // `opcoes` e a CONTAGEM; os ids estao em `opcoes_ids`. Ate 2026-07-28 as
      // duas implementacoes liam `opcoes` aqui e levantavam TypeError ao
      // iterar um int -- so nao explodia porque nenhuma ficha de exemplo
      // exercitava este slot, e foi o porte que trouxe o caso a tona.
      const ids: string[] = [];
      for (const b of this.slots_de_subclasse) {
        if (em === null || b.nivel === em) ids.push(...b.opcoes_ids);
      }
      registros = ids.map((i) => this.base.opcional(i));
    } else if (slot === "skill_increase") {
      registros = [...this.base.por_id.values()].filter((r) => r.kind === "skill");
    } else if (slot === "nivel_de_classe") {
      registros = [...this.base.por_id.values()].filter((r) => r.kind === "class");
    } else if (slot === "feat_concedido") {
      // o filtro do ChoiceSet RECORTA, como qualquer elegibilidade de slot. Um
      // slot de `Ancient Elf` que aceitasse feat qualquer seria pior que nao
      // existir: entregaria escolha ilegal com cara de legal.
      let blocos = this.slots_concedidos.filter((b) => em === null || b.em === em);
      if (flag !== null) blocos = blocos.filter((b) => b.flag === flag);
      // O `tipo` estreita QUANDO existe kind com aquele nome; o filtro
      // estreita depois. Sem o kind, `Adopted Ancestry` -- cujo filtro é só
      // referência dinâmica de ator -- ofereceria os 19.606 registros da base;
      // sem o filtro, `Adopted Ancestry` não estreita. Cada um cobre o buraco
      // do outro.
      //
      // `action` do Foundry NÃO é o nosso `kind: action`, e isso importa desde
      // 31/07: no Foundry a tática do Commander É um `type: action`, e nós a
      // modelamos como `kind: tactic` (extrator próprio, fonte AoN). Traduzir
      // `tipo: action` só para o kind `action` ESVAZIAVA os 4 blocos de tática
      // -- 21 opções viravam 0.
      // Spec: specs/2026-07-31-kind-action.md
      const kindsDoBloco = blocos.map((b) => b.tipo).filter((k): k is string => !!k);
      const kinds = new Set(kindsDoBloco.filter((k) => this.base.kinds().has(k)));
      if (kindsDoBloco.includes("action")) {
        for (const k of ["action", "tactic"]) {
          if (this.base.kinds().has(k)) kinds.add(k);
        }
      }
      registros = blocos.length === 0 ? [] :
        [...this.base.por_id.values()].filter((r) =>
          (kinds.size === 0 || kinds.has(r.kind ?? ""))
          && blocos.some((b) => this._casa_filtro(r, b.filtro)));
    } else if (slot === "heranca") {
      // Heranca pertence a uma ancestralidade -- nao existe Anao Elfico. O
      // vinculo esta em `ancestry` (309 das 334 herancas o declaram).
      //
      // As 25 que NAO declaram sao as versateis do PF2e (Aiuvarin, Nephilim,
      // Dhampir, Changeling, Suli...), abertas a qualquer ancestralidade -- e
      // por isso a ausencia do campo e o que as identifica, nao um descuido.
      //
      // Mesmo criterio de `_aceita_no_slot`: isto e filtro por TIPO, nao
      // requisito. Herança de outra ancestralidade nao e "escolha ruim", e
      // escolha inexistente, e o principio zero vale para requisito.
      const minha = this.ancestria === null ? null : this.ancestria.id;
      registros = [...this.base.por_id.values()].filter((r) => {
        if (r.kind !== "heritage") return false;
        // sem ancestralidade escolhida ainda, mostrar tudo: lista vazia num
        // slot recem-aberto parece defeito, e o jogador ainda vai voltar aqui
        if (minha === null) return true;
        const dona = r["ancestry"];
        return !ehStr(dona) || this.base.resolver(dona) === this.base.resolver(minha);
      });
    } else {
      registros = [...this.base.por_id.values()]
        .filter((r) => r.kind === "feat" && this._aceita_no_slot(slot, r));
    }

    const ja = this._ids_de_feat_escolhidos();
    const saida: Candidato[] = [];
    for (const r of registros) {
      if (r === null) continue;
      const exigencia = slot === "feat_concedido"
        ? this._sem_gate_de_nivel(r["requires"]) : r["requires"];
      let [atende, motivos] = this.avaliar(exigencia);
      const veto = this._veto_dedicacao_da_propria_classe(r);
      if (veto !== null) {
        atende = false;
        motivos = [...motivos, veto];
      }
      // `em` e int nos slots de cadencia e a string `criacao` no que nasce na
      // criacao. Slot concedido nao tem teto proprio: o filtro da fonte ja diz
      // quais niveis aceita, e o `Ancient Elf` dispensa o nivel por escrito.
      const teto = slot === "feat_concedido" ? null
                 : (em === "criacao" ? 1 : em);
      if (ehInt(teto) && ehInt(r["level"]) && r["level"] > teto) {
        atende = false;
        motivos = [...motivos,
                   `feat de nivel ${r["level"]} num slot de nivel ${em}`];
      }
      saida.push({
        id: r.id, nome: nome(r), level: ehInt(r["level"]) ? r["level"] : null,
        atende, motivos, ja_pego: ja.has(r.id),
      });
    }
    const ordenado = ordenarPor(saida, (x) => [
      !x.atende, x.ja_pego, x.level ?? 0, x.nome ?? "",
    ]);
    return limite ? ordenado.slice(0, limite) : ordenado;
  }

  /**
   * O que combina com o personagem -- a pergunta central do construtor.
   *
   * `requires` ORDENA a lista; não a filtra. O que está fora aparece marcado,
   * nunca escondido.
   */
  disponiveis(kind = "feat", limite: number | null = null): Candidato[] {
    const saida: Candidato[] = [];
    for (const r of this.base.por_id.values()) {
      if (r.kind !== kind) continue;
      let [atende, motivos] = this.avaliar(r["requires"]);
      const extra = this._veto_dedicacao_da_propria_classe(r);
      if (extra !== null) {
        atende = false;
        motivos = [...motivos, extra];
      }
      saida.push({
        id: r.id, nome: nome(r), level: ehInt(r["level"]) ? r["level"] : null,
        atende, motivos, ja_pego: false,
      });
    }
    const ordenado = ordenarPor(saida, (x) => [!x.atende, x.level ?? 0, x.nome ?? ""]);
    return limite ? ordenado.slice(0, limite) : ordenado;
  }

  /**
   * nome normalizado -> id da classe, para os 27 arquétipos de multiclasse.
   * O cache vive na BASE, não no personagem -- ver o comentário em `base.ts`.
   */
  private _classes_multiclasse(): Map<string, string> {
    return this.base.multiclasse();
  }

  /**
   * Regra 23: dedicação de multiclasse da própria classe.
   *
   * RAW (Advanced Player's Guide, "Multiclass Archetypes"): *"You can't select
   * a multiclass archetype's dedication feat if you are a member of the class
   * of the same name."* Nada na base modelava isso -- um Mago 20 puro recebia
   * `atende: True` para Wizard Dedication.
   *
   * DECISÃO DO IGOR (2026-07-27): a exclusão vale sempre que o personagem tem
   * QUALQUER nível da classe, e é MÚTUA -- ver `_veto_classe_de_dedicacao_ja_pega`.
   *
   * O que a exclusão tira é a ESCOLHA DA TRADIÇÃO, não os slots -- então a
   * regra 21 não é violada. E resolve uma incoerência real: com as duas rotas
   * na mesma classe, a mesma magia sairia em DOIS ranks na mesma ficha, o do
   * slot de classe elevado pela regra 17 e o do slot de arquétipo, que pela
   * regra 18 roda RAW puro.
   *
   * Princípio zero continua valendo: isto marca `fora do requisito`, com o
   * motivo escrito. Nunca esconde nem impede.
   */
  private _veto_dedicacao_da_propria_classe(feat: Registro): string | null {
    const n = normSlug(verdadeiro(feat["name"]) ? feat["name"] : "");
    if (!n.endsWith("-dedication")) return null;
    const cid = this._classes_multiclasse().get(n.slice(0, -"-dedication".length));
    if (cid === undefined) return null;
    const nc = this.nivel_de(cid);
    if (nc === 0) return null;
    return `regra 23: o personagem ja tem ${nc} nivel(is) de `
           + `${pyStr(nome(this.base.get(cid)))}; as duas rotas se excluem`;
  }

  // -- princípio zero: sinaliza, nunca bloqueia ---------------------------

  /**
   * `requires` sugere, NUNCA bloqueia (princípio zero da spec).
   *
   * Regra 12: o requisito de nível de um class feat é checado contra o nível
   * DAQUELA CLASSE. Regra 13: feat de arquétipo, contra o nível de personagem.
   */
  private _checar_requisitos(): void {
    for (const e of this._todas_escolhas()) {
      const wb_id = e["pega"];
      if (!ehStr(wb_id) || !wb_id.startsWith("wb:feat/")) continue;
      const feat = this.base.opcional(wb_id);
      if (feat === null) {
        this.fora_do_requisito.push({ feat: wb_id, motivo: "id ausente da base" });
        continue;
      }
      // O predicado já carrega o gate de nível derivado, então a checagem
      // manual de nível que existia aqui virou caso particular de avaliar o
      // predicado inteiro -- e agora `proficiency`, `has`, `ability` e
      // `subclass` também são verificados.
      // o requisito de um feat é avaliado contra o estado SEM o efeito dele
      // mesmo -- ver `_rank_sem`
      this._avaliando = wb_id;
      // o nível DESTA escolha: sem ele o `has` olha o documento inteiro e a
      // ordem ilegal passa limpa -- ver `_termo_has`
      const em_da_escolha = obter(e, "em");
      this._avaliando_em = ehInt(em_da_escolha) ? em_da_escolha : null;
      let [atende, motivos] = this.avaliar(feat["requires"]);
      this._avaliando = null;
      this._avaliando_em = null;
      for (const veto of [this._veto_dedicacao_da_propria_classe(feat),
                          this._exige_a_dedicacao_do_arquetipo(feat, motivos)]) {
        if (veto !== null) {
          atende = false;
          motivos = [...motivos, veto];
        }
      }
      if (!atende) {
        this.fora_do_requisito.push({
          feat: nomeOu(feat, wb_id),
          motivo: motivos.join("; ") || "predicado nao atendido",
        });
      }
    }
    this._veto_classe_de_dedicacao_ja_pega();
    this._nova_dedicacao_exige_dois_feats();
  }

  // -- as duas regras do trait `dedication` (RAW) -------------------------

  /**
   * Escolhidos MAIS concedidos. `gray-corsair-training` concede
   * `pirate-dedication`: sem contar o concedido, um feat Pirate na mesma ficha
   * era acusado de não ter a dedicação (falso positivo) e uma segunda dedicação
   * passava batido (falso negativo).
   */
  private _ids_de_feat_escolhidos(): Set<string> {
    const ids = new Set<string>();
    for (const e of this._todas_escolhas()) {
      if (ehStr(e["pega"]) && e["pega"].startsWith("wb:feat/")) ids.add(e["pega"]);
    }
    for (const c of this.concedidos) if (c.id.startsWith("wb:feat/")) ids.add(c.id);
    return ids;
  }

  /**
   * RAW do trait `archetype`: um feat de arquétipo exige a Dedication daquele
   * arquétipo.
   *
   * A base não escreve isso no `requires` -- 181 feats de arquétipo trazem só
   * `character_level >= N` --, e por isso Barbarian Resiliency entrava numa
   * ficha sem Barbarian Dedication em silêncio. O vínculo não precisa de lista:
   * `feat["archetype"]` aponta o arquétipo e a dedicação dele é achável por
   * trait.
   */
  private _exige_a_dedicacao_do_arquetipo(feat: Registro, motivos: string[]): string | null {
    const traits = listaDe(feat["traits"]);
    if (!traits.includes("archetype") || traits.includes("dedication")) return null;
    const arq = feat["archetype"];
    if (!verdadeiro(arq)) return null;
    const ded = this.base.dedicacao_do_arquetipo(arq);
    if (ded === null || this._ids_de_feat_escolhidos().has(ded)) return null;
    const n = nomeOu(this.base.get(ded), ded);
    // se o `requires` já reprovou por causa da MESMA dedicação, não repetir
    if (motivos.some((m) => m.includes(n))) return null;
    const reg = this.base.opcional(arq);
    return `feat do arquetipo ${reg !== null ? nomeOu(reg, String(arq)) : pyStr(arq)}`
           + ` exige ${n} (RAW do trait archetype), que a ficha nao tem`;
  }

  /**
   * RAW do trait `dedication`, conferido no texto da própria base (76 dedicações
   * repetem a cláusula): "You can't select another dedication feat until you've
   * gained two other feats from the <X> archetype".
   *
   * A contagem é NO TEMPO: vale o que o personagem tinha até o nível em que a
   * nova dedicação entrou, não o que ele tem no fim da ficha.
   */
  private _nova_dedicacao_exige_dois_feats(): void {
    let picks: Dict[] = this._todas_escolhas()
      .filter((e) => ehStr(e["pega"]) && e["pega"].startsWith("wb:feat/"));
    // `criacao` vem antes de qualquer nível numerado
    picks = ordenarPor(picks, (e) => [ehInt(e["em"]) ? e["em"] : 0]);
    // feat de arquétipo CONCEDIDO conta na cota tanto quanto o escolhido --
    // entra no nível da escolha que o originou, que é quando ele apareceu
    const nivel_da_raiz = new Map<unknown, unknown>();
    for (const e of picks) nivel_da_raiz.set(e["pega"], obter(e, "em"));
    for (const c of this.concedidos) {
      if (c.id.startsWith("wb:feat/")) {
        picks.push({ pega: c.id, em: nivel_da_raiz.get(c.raiz) ?? null });
      }
    }
    picks = ordenarPor(picks, (e) => [ehInt(e["em"]) ? e["em"] : 0]);

    const contagem = new Map<string, number>();   // arquétipo -> feats não-dedicação
    const dedicados: string[] = [];               // arquétipos já dedicados, em ordem
    for (const e of picks) {
      const feat = this.base.opcional(e["pega"]);
      if (feat === null) continue;
      const traits = listaDe(feat["traits"]);
      const arq = feat["archetype"];
      if (traits.includes("dedication") && verdadeiro(arq)) {
        const faltando = dedicados.filter((a) => (contagem.get(a) ?? 0) < 2);
        if (faltando.length > 0) {
          const nomes = faltando
            .map((a) => nomeOu(this.base.opcional(a), a)).join(", ");
          this.fora_do_requisito.push({
            feat: nomeOu(feat, String(e["pega"])),
            motivo: `nova dedicacao no nivel ${pyStr(obter(e, "em"))} sem os 2 feats `
                    + `exigidos de: ${nomes} (RAW do trait dedication)`,
          });
        }
        dedicados.push(String(arq));
      } else if (verdadeiro(arq)) {
        somar(contagem, String(arq), 1);
      }
    }
  }

  /**
   * Regra 23, o outro sentido: nível de classe X com dedicação de X.
   *
   * A exclusão é MÚTUA. O primeiro sentido (pegar a dedicação tendo a classe) é
   * barrado em `_veto_dedicacao_da_propria_classe`; este barra a ordem inversa,
   * que produz exatamente a mesma ficha e passaria batido se só um lado fosse
   * checado.
   */
  private _veto_classe_de_dedicacao_ja_pega(): void {
    const pegos = new Set<string>();
    for (const e of this._todas_escolhas()) {
      if (ehStr(e["pega"]) && e["pega"].startsWith("wb:feat/")) {
        pegos.add(normSlug(nomeOu(this.base.opcional(e["pega"]), "")));
      }
    }
    for (const [n, cid] of this._classes_multiclasse()) {
      const nc = this.nivel_de(cid);
      if (nc && pegos.has(`${n}-dedication`)) {
        const nome_da_classe = pyStr(nome(this.base.get(cid)));
        this.fora_do_requisito.push({
          feat: `${nome_da_classe} (nivel de classe)`,
          motivo: `regra 23: o personagem tem ${nc} nivel(is) de ${nome_da_classe} `
                  + `E a dedicacao da mesma classe. As duas rotas se excluem`,
        });
      }
    }
  }

  /** A classe de um feat sai do trait, não de lista escrita à mão. */
  classe_do_feat(feat: Registro): string | null {
    const traits = new Set(listaDe(feat["traits"]).map((t) => String(t).toLowerCase()));
    for (const cid of this.ordem_de_classe) {
      const n = this.base.get(cid)["name"];
      if (traits.has(verdadeiro(n) ? String(n).toLowerCase() : "")) return cid;
    }
    return null;
  }

  // -- cadeia de grant_feat/grant_item: aplica o estático, sinaliza o resto -

  /**
   * Percorre `grant_feat`/`grant_item` de tudo que o personagem tem (feats
   * escolhidos + features de classe/subclasse), com guarda de profundidade e
   * visitados.
   *
   * O que a cadeia entrega com ALVO ESTÁTICO é aplicado: no PF2e isso não é
   * escolha nenhuma, é efeito automático (Barbarian Dedication dá Rage, ponto
   * final). O princípio zero fala de `requires` -- sugerir em vez de bloquear a
   * ESCOLHA do jogador --, não de esconder o efeito de uma escolha já feita.
   * Alvo DINÂMICO (`{item|flags...}`) é que depende de escolha ainda não feita:
   * esse continua só sinalizado, e o app precisa distinguir "pendente" de
   * "ausente".
   *
   * Antes desta passada, uma dedicação entrava na ficha como linha e não
   * entregava nada -- medido: 52 HP contra 56 (`battle-harbinger`), `society`
   * untrained (`shieldmarshal`), Rage sumido (`barbarian`).
   */
  private _grants_em_cadeia(): void {
    // o que o personagem já tem por escolha própria não pode ser concedido de
    // novo: senão Toughness pego à mão + Toughness da dedicação somaria HP duas
    // vezes.
    this._ja_tenho = new Set();
    for (const f of this.features) if (verdadeiro(f.id)) this._ja_tenho.add(f.id as string);
    for (const [wb_id] of this._feats_escolhidos()) this._ja_tenho.add(wb_id);

    const origens: Array<[string, unknown[]]> = [];
    for (const [wb_id, feat] of this._feats_escolhidos()) {
      origens.push([wb_id, listaDe(feat["grants"])]);
    }
    // snapshot: a recursão percorre os grants do próprio alvo concedido, então
    // features novas não precisam ser revisitadas por este laço
    for (const f of [...this.features]) {
      if (verdadeiro(f.id)) origens.push([f.id as string, f.grants]);
    }
    // ancestria, herança e background TAMBÉM concedem -- são 496 registros com
    // `grant_feat` que ficavam inertes porque a cadeia só olhava feat e feature
    // (`shielded-fortune` -> Toughness, `ambitious-human` -> Fleet)
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg !== null && verdadeiro(reg.id)) origens.push([reg.id, listaDe(reg["grants"])]);
    }
    for (const [origem_id, grants] of origens) {
      this._resolver_cadeia_de_grants(origem_id, grants, new Set([origem_id]));
    }
  }

  /**
   * Quem ORIGINOU este item na ficha. Para o que o jogador escolheu, é ele
   * mesmo; para o que veio de cadeia, é a escolha lá no começo dela.
   */
  private _raiz_de(wb_id: string): string {
    return this._raizes.get(wb_id) ?? wb_id;
  }

  /**
   * Põe na ficha o que a cadeia concedeu. Class-feature vira linha de feature
   * (e por isso entra em `_proficiencias`, em `_termo_has` e na visão); feat
   * vira feat efetivo, que é o que `_hp` e `_proficiencias` percorrem.
   */
  private _aplicar_concessao(origem_id: string, alvo: string, alvo_reg: Registro): void {
    const origem_nome = nomeOu(this.base.opcional(origem_id), origem_id);
    const raiz = this._raiz_de(origem_id);
    this._raizes.set(alvo, raiz);
    const registro: RegistroConcedido = {
      id: alvo,
      nome: nomeOu(alvo_reg, alvo),
      classe: null,
      origem: origem_nome,
      nivel_de_classe: null,
      grants: listaDe(alvo_reg["grants"]),
      na_base: true,
      concedido_por: origem_id,
      raiz,
    };
    this.concedidos.push(registro);
    if (alvo.startsWith("wb:class-feature/")) this.features.push(registro);
  }

  /**
   * Feats escolhidos MAIS os concedidos pela cadeia, sem repetir.
   *
   * É a lista que vale para efeito: o jogo não distingue o Toughness que você
   * pegou do Toughness que a dedicação te deu.
   */
  private *_feats_efetivos(): Generator<[string, Registro, string | null]> {
    const vistos = new Set<string>();
    for (const [wb_id, feat] of this._feats_escolhidos()) {
      if (!vistos.has(wb_id)) {
        vistos.add(wb_id);
        yield [wb_id, feat, null];
      }
    }
    for (const c of this.concedidos) {
      if (c.id.startsWith("wb:feat/") && !vistos.has(c.id)) {
        vistos.add(c.id);
        yield [c.id, this.base.get(c.id), c.origem];
      }
    }
  }

  /**
   * Um passo da cadeia. `visitados` é compartilhado entre as chamadas
   * recursivas de uma mesma origem -- é o que poda auto-referência (A concede A
   * mesma) sem gerar aviso: o alvo já está em `visitados` desde o primeiro
   * passo, então é tratado como "já tenho", não como perda.
   */
  private _resolver_cadeia_de_grants(origem_id: string, grants: unknown[],
                                     visitados: Set<string>, profundidade = 0): void {
    if (profundidade > MAX_PROFUNDIDADE_GRANTS) {
      this.avisos.push(
        `${origem_id}: cadeia de grants cortada em profundidade `
        + `${MAX_PROFUNDIDADE_GRANTS} (possivel ciclo ou dado malformado)`);
      return;
    }
    for (const g of listaDe(grants)) {
      if (!ehDict(g)) continue;
      if (Object.hasOwn(g, "grant_feat")) {
        const bruto = g["grant_feat"];
        const alvos = ehLista(bruto) ? bruto : [bruto];
        for (const alvo of alvos) {
          if (!ehStr(alvo) || !alvo.startsWith("wb:")) {
            // 476 alvos da base são nome cru ou dict serializado em vez de id
            // -- TODOS de background (medido 2026-07-27). Não é "ausente da
            // base", é referência não resolvida pelo pipeline, e o aviso
            // precisa dizer isso.
            this.avisos.push(
              `${origem_id}: grant_feat com alvo nao resolvido pelo pipeline `
              + `(${pyStr(alvo).slice(0, 60)}) -- nao aplicado`);
            continue;
          }
          if (alvo.includes("{")) {
            this.avisos.push(
              `${origem_id}: grant_feat depende de escolha do jogador (${alvo}) `
              + `-- nao resolvivel automaticamente`);
            continue;
          }
          if (visitados.has(alvo)) continue;   // já concedido nesta cadeia
          const alvo_reg = this.base.opcional(alvo);
          if (alvo_reg === null) {
            this.avisos.push(
              `${origem_id}: grant_feat aponta pra id ausente da base: ${alvo}`);
            continue;
          }
          visitados.add(alvo);
          if (!this._ja_tenho.has(alvo)) {
            this._ja_tenho.add(alvo);
            this._aplicar_concessao(origem_id, alvo, alvo_reg);
          }
          this._resolver_cadeia_de_grants(
            alvo, listaDe(alvo_reg["grants"]), visitados, profundidade + 1);
        }
      }
      if (Object.hasOwn(g, "grant_item")) {
        const gi = g["grant_item"];
        const uuid = ehDict(gi) ? gi["uuid"] : gi;
        // `wb` é o id que o pipeline resolveu a partir do NOME no fim do uuid
        // (spec `2026-07-29-grant-item-por-nome.md`). Até 2026-07-29 o motor não
        // aplicava grant_item NENHUM -- só avisava do uuid dinâmico --, então
        // 619 concessões ficavam inertes.
        const alvo = ehDict(gi) ? gi["wb"] : null;
        if (ehStr(alvo) && alvo.startsWith("wb:")) {
          if (visitados.has(alvo)) continue;
          const alvo_reg = this.base.opcional(alvo);
          if (alvo_reg === null) {
            this.avisos.push(
              `${origem_id}: grant_item aponta pra id ausente da base: ${alvo}`);
            continue;
          }
          visitados.add(alvo);
          if (!this._ja_tenho.has(alvo)) {
            this._ja_tenho.add(alvo);
            this._aplicar_concessao(origem_id, alvo, alvo_reg);
          }
          this._resolver_cadeia_de_grants(
            alvo, this._grants_de(alvo_reg), visitados, profundidade + 1);
          continue;
        }
        if (ehStr(uuid) && uuid.includes("{")) {
          // uuid dinâmico: só a escolha do jogador fecha isto. NÃO é "alvo não
          // encontrado" -- é "pendente", e o app tem que distinguir os dois.
          this.avisos.push(
            `${origem_id}: grant_item depende de escolha do jogador (uuid `
            + `dinamico \`${uuid}\`) -- pendente, nao e alvo ausente`);
        }
      }
    }
  }

  // -- saída --------------------------------------------------------------


  // -- bônus incondicional e o total de perícia/salva ------------------------

  /**
   * Soma respeitando a regra de tipo do PF2e.
   *
   * Bônus do MESMO tipo não empilham -- vale o maior. Tipos diferentes somam.
   * Bônus sem tipo (`untyped`) empilha com tudo, inclusive com outro untyped.
   *
   * Sem isto, um personagem com três itens de +1 de circunstância sairia com +3
   * onde o RAW dá +1 -- e a ficha parada inflaria sozinha.
   *
   * Spec: `specs/2026-07-30-bonus-de-pericia-e-salva.md`
   */
  private _melhor_por_tipo(bonus: BonusAplicado[]): number {
    const melhor = new Map<string, number>();
    let solto = 0;
    for (const b of bonus) {
      const tipo = ehStr(b.tipo) ? b.tipo.toLowerCase() : "";
      if (!tipo || tipo === "untyped") { solto += b.valor; continue; }
      melhor.set(tipo, Math.max(melhor.get(tipo) ?? 0, b.valor));
    }
    let soma = solto;
    for (const v of melhor.values()) soma += v;
    return soma;
  }

  /**
   * `flat_modifier` sem `condicional`, agrupado por selector.
   *
   * São 462 de 1.709 -- os outros 1.247 são condicionais ("+2 em Atletismo só
   * para Empurrar") e dependem de contexto de ação que a ficha não tem.
   */
  private _bonus_incondicionais(): Map<string, BonusAplicado[]> {
    if (this._bonusMemo !== null) return this._bonusMemo;
    const fora: Record<string, number> = {};
    const porSelector = new Map<string, BonusAplicado[]>();
    const fontes: Array<[string, Dict]> = [];
    for (const cid of this.ordem_de_classe) {
      const c = dictDe(this.base.get(cid));
      fontes.push([nomeOu(c, cid), c]);
    }
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg) fontes.push([pyStr(nome(reg)), dictDe(reg)]);
    }
    for (const f of this.features) fontes.push([pyStr(f["nome"]), dictDe(f)]);
    for (const [i, feat] of this._feats_efetivos()) fontes.push([nomeOu(feat, i), feat]);
    // o inventario equipado, que faltava: 293 grants incondicionais e
    // aplicaveis em equipment/armor/shield/weapon, em selectors que o motor ja
    // soma. Ver `specs/2026-07-30-bonus-de-item-equipado.md`.
    for (const entrada of listaDe(this.doc["inventario"])) {
      const e = dictDe(entrada);
      if (!verdadeiro(e["equipado"])) continue;
      const reg = this.base.opcional(pyStr(e["item"]));
      if (reg) fontes.push([pyStr(nome(reg)), dictDe(reg)]);
    }
    for (const [rotulo, reg] of fontes) {
      for (const g of this._grants_de(reg)) {
        const fm = dictDe(g)["flat_modifier"];
        if (!ehDict(fm) || verdadeiro(fm["condicional"])) continue;
        const valor = fm["value"];
        if (!ehInt(valor)) { fora["valor nao inteiro"] = (fora["valor nao inteiro"] ?? 0) + 1; continue; }
        const bruto = fm["selector"];
        const alvos = Array.isArray(bruto) ? bruto : [bruto];
        for (const alvo of alvos) {
          const chave = pyStr(alvo);
          if (chave.includes("{")) { fora["selector dinamico"] = (fora["selector dinamico"] ?? 0) + 1; continue; }
          empurrar(porSelector, chave, { tipo: fm["type"], valor, origem: rotulo });
        }
      }
    }
    this.bonus_ignorados = fora;
    this._bonusMemo = porSelector;
    return porSelector;
  }

  /**
   * O total que a TELA calculava (`PainelDireito.tsx:94`).
   *
   * Número que nasce no componente React não tem oráculo, não tem paridade e
   * não tem onde receber `flat_modifier`. AC e ataque já moravam aqui; a
   * perícia e a salva ficaram para trás.
   */
  private _pericias_e_salvas(): void {
    const bonus = this._bonus_incondicionais();
    const consumidos = new Set<string>();

    const total = (chave: string, atributo: string, extras: string[]): LinhaDePericia => {
      const rank = (this.proficiencias.get(chave) ?? "untrained") as Rank;
      const mod = this.modificadores[atributo] ?? 0;
      const aplicados: BonusAplicado[] = [];
      for (const sel of extras) {
        aplicados.push(...(bonus.get(sel) ?? []));
        consumidos.add(sel);
      }
      const extra = this._melhor_por_tipo(aplicados);
      // RAW: destreinado NÃO soma o nível, só o atributo
      const base = rank !== "untrained" ? this.nivel + RANK_BONUS[rank] : 0;
      const linha: LinhaDePericia = {
        chave, nome: chave, rank, atributo,
        mod_atributo: mod, bonus_total: extra, total: base + mod + extra,
        detalhe: `${rank !== "untrained" ? `nivel ${this.nivel} + prof ` : ""}`
          + `${rank !== "untrained" ? RANK_BONUS[rank] : 0} (${rank})`
          + ` + ${atributo.toUpperCase()} ${comSinal(mod)}`
          + (extra ? ` + bonus ${comSinal(extra)}` : ""),
      };
      if (aplicados.length) linha.bonus = aplicados;
      return linha;
    };

    this.pericias = [];
    for (const reg of this.base.por_id.values()) {
      if (reg.kind !== "skill" || reg["lore"] === true || reg.id === "wb:skill/lore") continue;
      const chave = reg.id.split("/").pop() ?? "";
      const attr = pyStr(listaDe(reg["attribute"])[0] ?? "int");
      const linha = total(chave, attr, [chave]);
      linha.nome = reg.name ?? chave;
      this.pericias.push(linha);
    }
    for (const chave of this.proficiencias.keys()) {
      if (!chave.startsWith("lore:")) continue;
      const linha = total(chave, "int", [chave]);
      // a chave às vezes já carrega o sufixo "Lore" (vem assim da fonte), e
      // prefixar cegamente produzia `Lore: Alcohol Lore` na ficha. A regra
      // estava em `PainelDireito.tsx` e veio junto com a conta.
      const bruto = chave.slice("lore:".length).replace(/\s*\blore\b\s*$/i, "").trim();
      linha.nome = "Lore: " + bruto.replace(/\b\w/g, (c) => c.toUpperCase());
      this.pericias.push(linha);
    }
    this.pericias.sort((a, b) => ordenarTextos([a.nome, b.nome])[0] === a.nome ? -1 : 1);

    const ATRIBUTO_DA_SALVA: Record<string, string> = {
      fortitude: "con", reflex: "dex", will: "wis", perception: "wis",
    };
    this.salvas = {};
    for (const [chave, attr] of Object.entries(ATRIBUTO_DA_SALVA)) {
      const extras = chave === "perception" ? [chave] : [chave, "saving-throw"];
      this.salvas[chave] = total(chave, attr, extras);
      consumidos.add(chave);
    }
    consumidos.add("saving-throw");

    // o que sobrou não é "ignorado" indistintamente: `hp` e `ac` têm passo
    // próprio, e o resto (`initiative`, `perception-dc`, `skill-check`
    // genérico) o motor não modela. Contar é o que impede a perda silenciosa.
    const OUTRO_PASSO = new Set(["hp", "ac"]);
    for (const [sel, lista] of bonus) {
      if (consumidos.has(sel) || OUTRO_PASSO.has(sel)) continue;
      this.bonus_ignorados[`selector nao modelado: ${sel}`] = lista.length;
    }
  }


  // -- resistência, fraqueza e imunidade ------------------------------------

  /**
   * Duas fontes do MESMO tipo não somam -- vale a maior (regra do livro).
   * Mesma forma do `_melhor_por_tipo` dos bônus, mas devolvendo as LINHAS,
   * porque a ficha mostra a origem.
   */
  private _melhor_resistencia(lista: LinhaDeResistencia[]): LinhaDeResistencia[] {
    const melhor = new Map<string, LinhaDeResistencia>();
    for (const linha of lista) {
      const t = String(linha.tipo);
      const atual = melhor.get(t);
      if (!atual || (linha.valor ?? 0) > (atual.valor ?? 0)) melhor.set(t, linha);
    }
    return ordenarPor([...melhor.values()], (x) => [String(x.tipo)]);
  }

  /**
   * 233 `resistance`, 14 `immunity` e 11 `weakness` que a ficha ignorava.
   * Spec: `specs/2026-07-30-resistencia-e-formula.md`
   */
  private _resistencias(): void {
    const crus: Record<string, LinhaDeResistencia[]> = {
      resistance: [], weakness: [], immunity: [],
    };
    const conta = (chave: string) => {
      this.bonus_ignorados[chave] = (this.bonus_ignorados[chave] ?? 0) + 1;
    };
    const fontes: Array<[string, Dict]> = [];
    for (const cid of this.ordem_de_classe) {
      const c = dictDe(this.base.get(cid));
      fontes.push([nomeOu(c, cid), c]);
    }
    for (const reg of [this.ancestria, this.heranca, this.background]) {
      if (reg) fontes.push([pyStr(nome(reg)), dictDe(reg)]);
    }
    for (const f of this.features) fontes.push([pyStr(f["nome"]), dictDe(f)]);
    for (const [i, feat] of this._feats_efetivos()) fontes.push([nomeOu(feat, i), feat]);
    for (const entrada of listaDe(this.doc["inventario"])) {
      const e = dictDe(entrada);
      if (!verdadeiro(e["equipado"])) continue;
      const reg = this.base.opcional(pyStr(e["item"]));
      if (reg) fontes.push([pyStr(nome(reg)), dictDe(reg)]);
    }
    for (const [rotulo, reg] of fontes) {
      for (const g of this._grants_de(reg)) {
        const d = dictDe(g);
        for (const chave of ["resistance", "weakness", "immunity"]) {
          const bruto = d[chave];
          if (bruto === undefined || bruto === null) continue;
          // `tipo` é LISTA em 19 dos 258 (`Blast Resistance` protege de fire E
          // sonic). Uma resistência a N tipos são N linhas; converter direto
          // para texto escrevia `"['fire', 'sonic']"` na ficha.
          const alvo = chave === "immunity" ? bruto : dictDe(bruto)["tipo"];
          const tipos = Array.isArray(alvo) ? alvo.map((x) => pyStr(x)) : [pyStr(alvo)];
          for (const tipo of tipos) {
            if (tipo.includes("{")) { conta(`${chave} de tipo dinamico`); continue; }
            if (tipo === "custom") { conta(`${chave} custom`); continue; }
            if (chave === "immunity") {
              crus[chave].push({ tipo, origem: rotulo });
              continue;
            }
            const valor = this._resolver_valor(dictDe(bruto)["valor"]);
            if (valor === null) { conta(`${chave} com formula fora da gramatica`); continue; }
            crus[chave].push({ tipo, valor, origem: rotulo });
          }
        }
      }
    }
    this.resistencias = this._melhor_resistencia(crus["resistance"]);
    this.fraquezas = this._melhor_resistencia(crus["weakness"]);
    // imunidade não tem valor: basta uma por tipo
    const vistas = new Set<string>();
    this.imunidades = [];
    for (const linha of crus["immunity"]) {
      if (vistas.has(linha.tipo)) continue;
      vistas.add(linha.tipo);
      this.imunidades.push(linha);
    }
    this.imunidades = ordenarPor(this.imunidades, (x) => [x.tipo]);
  }


  // -- velocidade ------------------------------------------------------------

  /**
   * `speed` sem sufixo é o que o Foundry usa quando só há um modo -- 11
   * ocorrências, todas de deslocamento terrestre.
   */
  private static readonly SELECTOR_DE_MODO: Record<string, string> = {
    "land-speed": "land", speed: "land", "fly-speed": "fly",
    "swim-speed": "swim", "climb-speed": "climb", "burrow-speed": "burrow",
  };

  /**
   * base da ancestria -> modo concedido -> bônus -> penalidade de armadura.
   *
   * Modo concedido NÃO soma: dois feats que dão `fly 25` e `fly 30` dão 30.
   * `all-speeds` aplica só nos modos que EXISTEM -- criar modo a partir de
   * bônus daria voo a quem não voa.
   *
   * Spec: `specs/2026-07-30-velocidade.md`
   */
  private _compor_velocidade(
    base: Record<string, number>, concedidos: Array<[string, number]>,
    bonus: Map<string, BonusAplicado[]>, penalidade: number,
  ): Record<string, number> {
    const vel: Record<string, number> = { ...base };
    for (const [modo, valor] of concedidos) {
      vel[modo] = Math.max(vel[modo] ?? 0, valor);
    }
    for (const [selector, lista] of bonus) {
      const modo = Personagem.SELECTOR_DE_MODO[selector];
      const alvos = selector === "all-speeds" ? Object.keys(vel) : (modo ? [modo] : []);
      for (const alvo of alvos) {
        if (alvo in vel) vel[alvo] += this._melhor_por_tipo(lista);
      }
    }
    if (penalidade) {
      for (const modo of Object.keys(vel)) vel[modo] = Math.max(0, vel[modo] + penalidade);
    }
    return vel;
  }

  /** A ficha do COMPANHEIRO já mostrava velocidade; a do personagem, não. */
  private _velocidade(): void {
    const base: Record<string, number> = {};
    const detalhe: Array<Dict> = [];
    if (this.ancestria) {
      for (const g of this._grants_de(dictDe(this.ancestria))) {
        const sp = dictDe(g)["speed"];
        if (ehDict(sp) && !("tipo" in sp)) {
          for (const [modo, valor] of Object.entries(sp)) base[modo] = inteiro(valor);
          detalhe.push({ origem: nome(this.ancestria), efeito: { ...base } });
        }
      }
    }
    let inicial = base;
    if (!Object.keys(base).length) {
      inicial = { land: 25 };
      this.avisos.push("sem ancestria escolhida: velocidade base assumida em 25 pes");
    }

    const concedidos: Array<[string, number]> = [];
    const fontes: Array<[string, Dict]> = [];
    for (const f of this.features) fontes.push([pyStr(f["nome"]), dictDe(f)]);
    for (const [i, feat] of this._feats_efetivos()) fontes.push([nomeOu(feat, i), feat]);
    for (const [rotulo, reg] of fontes) {
      for (const g of this._grants_de(reg)) {
        const sp = dictDe(g)["speed"];
        if (ehDict(sp) && "tipo" in sp) {
          const valor = this._resolver_valor(sp["valor"]);
          if (valor === null) continue;
          concedidos.push([pyStr(sp["tipo"]), valor]);
          detalhe.push({ origem: rotulo, efeito: { [pyStr(sp["tipo"])]: valor } });
        }
      }
    }

    const todos = this._bonus_incondicionais();
    const bonus = new Map<string, BonusAplicado[]>();
    for (const [sel, lista] of todos) {
      if (sel in Personagem.SELECTOR_DE_MODO || sel === "all-speeds") {
        bonus.set(sel, lista);
        for (const b of lista) detalhe.push({ origem: b.origem, efeito: { [sel]: b.valor } });
      }
    }

    // RAW: a penalidade cai 5 (mínimo 0) quando a FOR atende o requisito da
    // armadura. Ignorar a segunda metade poria um Guerreiro de FOR alta 5 pés
    // mais lento do que ele é.
    let penalidade = 0;
    for (const entrada of listaDe(this.doc["inventario"])) {
      const e = dictDe(entrada);
      if (!verdadeiro(e["equipado"])) continue;
      const arm = dictDe(this.base.opcional(pyStr(e["item"])));
      if (arm["kind"] !== "armor" || !verdadeiro(arm["speed_penalty"])) continue;
      let bruta = inteiro(arm["speed_penalty"]);
      const exigida = arm["strength"];
      if (ehInt(exigida) && (this.modificadores["str"] ?? 0) >= exigida) {
        bruta = Math.min(0, bruta + 5);
      }
      penalidade += bruta;
      if (bruta) detalhe.push({ origem: nome(arm), efeito: { penalidade: bruta } });
    }

    this.velocidade = this._compor_velocidade(inicial, concedidos, bonus, penalidade);
    this.velocidade_detalhe = detalhe;
  }

  /** A visão calculada. Cache, nunca fonte de verdade. */
  visao(): Visao {
    const classes: Record<string, number> = {};
    for (const [c, n] of this.niveis_por_classe) classes[nomeOu(this.base.get(c), c)] = n;
    const proficiencias: Record<string, Rank> = objetoDe(this.proficiencias);
    const slots: Record<string, number[]> = objetoDe(this.slots);
    return {
      nivel: this.nivel,
      classes,
      ancestralidade: nome(this.ancestria),
      heranca: nome(this.heranca),
      background: nome(this.background),
      atributos: this.atributos,
      modificadores: this.modificadores,
      hp: this.hp,
      proficiencias,
      pericias: this.pericias,
      salvas: this.salvas,
      pericias_livres: this.pericias_livres,
      aumentos_de_pericia: {
        niveis: this.aumentos_de_pericia, gastos: this.aumentos_detalhe,
      },
      boosts: {
        direito: this.boosts_direito, declarados: this.boosts_declarados,
        fontes: this.boosts_pendentes,
      },
      // a terceira pergunta do construtor: o que falta escolher
      slots_abertos: this.slots_abertos(),
      slots,
      conjuracao: this.conjuracao,
      sentidos: [...this._sentidos().values()] as Visao["sentidos"],
      atores: this.atores as unknown as Ator[],
      concessoes_de_ator: this.concessoes_de_ator,
      escolhas_de_feat: this.escolhas_de_feat,
      focus_pool: this.focus_pool,
      // sem isto a escolha de divindade nao muda nada VISIVEL, que e metade
      // do defeito do item 98
      divindade: this._divindade_da_ficha(),
      ac: this.ac,
      velocidade: this.velocidade,
      velocidade_detalhe: this.velocidade_detalhe,
      resistencias: this.resistencias,
      fraquezas: this.fraquezas,
      imunidades: this.imunidades,
      ataques: this.ataques,
      features: this.features,
      // o que a cadeia de grants entregou sem o jogador escolher. Fica em lista
      // própria (e não misturado em `escolhas`) porque a origem importa: a
      // ficha precisa poder dizer "Streetwise veio da dedicação", e o documento
      // continua com só o que foi escolhido.
      concedidos: this.concedidos.map((c): Concedido => ({
        id: c.id, nome: c.nome, por: c.origem, por_id: c.concedido_por,
      })),
      subclasses: this.slots_de_subclasse,
      fora_do_requisito: this.fora_do_requisito,
      avisos: this.avisos,
    };
  }
}
