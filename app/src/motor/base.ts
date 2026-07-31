/**
 * A base canônica, carregada uma vez. Porte de `Base` em `motor/motor.py`.
 *
 * Tudo aqui é derivado do catálogo e cacheado NA BASE, nunca no personagem:
 * o resultado depende só do catálogo, e a base é compartilhada por todas as
 * fichas. Com cache de instância, cada `Personagem` novo varria os 19.705
 * registros -- o profile de um teste de carga com 285 fichas mostrou ~90% do
 * tempo total de derivação nisso. Era o único ponto medido cujo custo escalava
 * com o tamanho da BASE em vez do tamanho da FICHA, que é exatamente o que não
 * pode acontecer num app client-side.
 */
import type { Registro } from "./tipos.ts";
import { ehStr, listaDe, normSlug, verdadeiro } from "./util.ts";

export class Base {
  readonly por_id: Map<string, Registro>;

  private _dedicacao_de: Map<string, string> | null = null;
  private _multiclasse: Map<string, string> | null = null;
  private _por_alias: Map<string, string> | null = null;
  private _kinds: Set<string> | null = null;
  private _gemeos: Map<string, Set<string>> | null = null;

  constructor(registros: Registro[]) {
    // `Map` e não objeto: a ordem de inserção é o que decide qual registro
    // ganha em `dedicacao_do_arquetipo` (setdefault) e a ordem da lista de
    // candidatos em caso de empate. Objeto literal reordena chave numérica.
    this.por_id = new Map();
    for (const r of registros) this.por_id.set(r.id, r);
  }

  /**
   * Índice de `equivale_a` nos DOIS sentidos, montado UMA vez.
   *
   * A primeira versão varria os 19.606 registros a cada `has`, e `has` roda
   * milhares de vezes por ficha -- o oráculo passou de segundos para mais de
   * seis minutos. O índice é o mesmo trabalho feito uma vez.
   */
  gemeos(): Map<string, Set<string>> {
    if (this._gemeos === null) {
      const idx = new Map<string, Set<string>>();
      const por = (k: string) => {
        if (!idx.has(k)) idx.set(k, new Set());
        return idx.get(k)!;
      };
      for (const r of this.por_id.values()) {
        const eq = (r as Record<string, unknown>)["equivale_a"];
        const alvos = Array.isArray(eq) ? eq : eq ? [eq] : [];
        const a = String(this.resolver(r.id));
        for (const x of alvos) {
          const b = String(this.resolver(String(x)));
          por(a).add(b);
          por(b).add(a);
        }
      }
      this._gemeos = idx;
    }
    return this._gemeos;
  }

  /**
   * Os kinds que a base REALMENTE tem.
   *
   * O slot concedido usa isto para saber se o `tipo` do ChoiceSet estreita:
   * `spell`, `heritage`, `ancestry`, `deity` e `weapon` são kinds; `action`
   * não é, e ali quem estreita é o filtro.
   */
  kinds(): Set<string> {
    if (this._kinds === null) {
      this._kinds = new Set<string>();
      for (const r of this.por_id.values()) if (r.kind) this._kinds.add(r.kind);
    }
    return this._kinds;
  }

  /**
   * Id canônico de uma referência, seguindo `aliases`.
   *
   * A base guarda o nome PRÉ-REMASTER como alias: `wb:feat/stunning-fist` é o
   * mesmo feat que `wb:feat/stunning-blows`, `wild-shape` virou
   * `untamed-form`, `divine-ally` virou `devout-blessing`. São 348 ids
   * alternativos.
   *
   * O portão 3 do pipeline sempre aceitou essas referências -- ele resolve por
   * alias antes de reclamar --, mas o motor comparava id cru e por isso 24
   * `requires` de feats de classes centrais nunca eram satisfeitos, por mais
   * que o personagem tivesse o feat. Portão e motor precisam concordar sobre o
   * que é "a mesma coisa"; enquanto discordavam, o portão verde escondia o
   * defeito em vez de denunciar.
   */
  resolver(wb_id: unknown): unknown {
    if (this._por_alias === null) {
      this._por_alias = new Map();
      for (const r of this.por_id.values()) {
        const kind = r.kind;
        for (const a of listaDe(r.aliases)) {
          if (verdadeiro(kind) && verdadeiro(a)) {
            this._por_alias.set(`wb:${String(kind)}/${normSlug(a)}`, r.id);
          }
        }
      }
    }
    // não-string atravessa intacto, como o `.get(wb_id, wb_id)` do Python
    if (!ehStr(wb_id)) return wb_id;
    if (this.por_id.has(wb_id)) return wb_id;
    return this._por_alias.get(wb_id) ?? wb_id;
  }

  /**
   * nome normalizado -> id da classe, para os arquétipos de multiclasse.
   *
   * Derivado: arquétipo cujo nome é nome de classe. Sem lista escrita à mão,
   * que já errou três vezes neste projeto.
   */
  multiclasse(): Map<string, string> {
    if (this._multiclasse === null) {
      const classes = new Map<string, string>();
      for (const r of this.por_id.values()) {
        if (r.kind === "class" && verdadeiro(r.name)) {
          classes.set(normSlug(r.name), r.id);
        }
      }
      const saida = new Map<string, string>();
      for (const r of this.por_id.values()) {
        if (r.kind === "archetype" && verdadeiro(r.name)) {
          const chave = normSlug(r.name);
          const cid = classes.get(chave);
          if (cid !== undefined) saida.set(chave, cid);
        }
      }
      this._multiclasse = saida;
    }
    return this._multiclasse;
  }

  /**
   * O feat de dedicação de um arquétipo, achado pelo DADO -- nunca por lista
   * escrita à mão. O vínculo é 1:1 na base inteira: 225 arquétipos, nenhum com
   * duas dedicações (medido 2026-07-27).
   */
  dedicacao_do_arquetipo(arquetipo_id: unknown): string | null {
    if (this._dedicacao_de === null) {
      this._dedicacao_de = new Map();
      for (const r of this.por_id.values()) {
        const traits = listaDe(r.traits);
        if (r.id.startsWith("wb:feat/") && traits.includes("dedication")
            && verdadeiro(r.archetype)) {
          const arq = String(r.archetype);
          // setdefault: o PRIMEIRO ganha
          if (!this._dedicacao_de.has(arq)) this._dedicacao_de.set(arq, r.id);
        }
      }
    }
    if (!ehStr(arquetipo_id)) return null;
    return this._dedicacao_de.get(arquetipo_id) ?? null;
  }

  get(wb_id: string): Registro {
    const r = this.por_id.get(wb_id);
    if (r === undefined) throw new Error(`id ausente da base: ${wb_id}`);
    return r;
  }

  /**
   * Como `get`, mas devolve `null` em vez de erro -- e SEGUINDO aliases.
   *
   * Sem o alias, ficha salva que cite um id que a fusão aposentou perde o item
   * em SILÊNCIO: `wb:equipment/cloak-of-elvenkind-greater` virou
   * `cloak-of-illusions-greater` e o inventário parava de achar. Isso
   * contradiz a promessa do motor: "mudança de regra re-deriva em vez de
   * invalidar ficha salva". Spec: `specs/2026-07-30-grau-legado-nao-fundido.md`
   */
  opcional(wb_id: unknown): Registro | null {
    if (!ehStr(wb_id)) return null;
    const direto = this.por_id.get(wb_id);
    if (direto !== undefined) return direto;
    return this.por_id.get(this.resolver(wb_id) as string) ?? null;
  }
}
