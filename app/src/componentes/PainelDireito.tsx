/**
 * A ficha viva -- fica SEMPRE visivel enquanto se monta, na coluna da direita.
 *
 * Foi o feedback que reorganizou o app: a primeira versao tinha abas separadas
 * (criacao / progressao / ficha), e o jogador escolhia um feat e tinha de
 * trocar de aba para ver o que mudou. Num construtor, o retorno imediato e o
 * ponto todo.
 *
 * Disposicao copiada do Pathbuilder, que o Igor usa: faixa de atributos no
 * topo, defesas logo abaixo com a CA dentro de um escudo, e o corpo em duas
 * faixas -- a coluna estreita de pericias sempre a vista, as abas ao lado.
 * Pericia nao e aba: e o numero que mais se consulta na mesa, e tirar da vista
 * custaria um clique por rolagem.
 *
 * Atributo vira MODIFICADOR (`DEX +3`, nao `16`), e pericia mostra o TOTAL
 * rolavel (`+8`), com o rank como pastilha ao lado. Numa mesa ninguem rola
 * "expert" -- rola +8.
 */
import { useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Personagem } from "../motor/personagem";
import type { Documento, Rank, Visao } from "../motor/tipos";
import { IconeEscudo } from "./Icones";
import { Equipamento } from "./Equipamento";

const RANK_BONUS: Record<Rank, number> = {
  untrained: 0, trained: 2, expert: 4, master: 6, legendary: 8,
};
const SIGLA: Record<Rank, string> = {
  untrained: "U", trained: "T", expert: "E", master: "M", legendary: "L",
};
const ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"] as const;
const SALVAGUARDAS = [
  ["fortitude", "Fortitude"], ["reflex", "Reflexos"], ["will", "Vontade"],
] as const;

type Aba = "ataques" | "equipamento" | "feats" | "concedido" | "sinais";

const sinal = (n: number) => `${n >= 0 ? "+" : ""}${n}`;

/**
 * `lore:alcohol lore` -> `Lore: Alcohol`.
 *
 * A chave da proficiencia as vezes ja carrega o sufixo "lore" (vem assim da
 * fonte), e prefixar cegamente produzia `Lore: Alcohol Lore` na ficha.
 */
function nomeDeLore(chave: string): string {
  const bruto = chave.slice(5).replace(/\s*\blore\b\s*$/i, "").trim();
  const titulo = bruto.replace(/\b\w/g, (c) => c.toUpperCase());
  return `Lore: ${titulo}`;
}

export function PainelDireito({
  p, v, base, d, setD,
}: {
  p: Personagem;
  v: Visao;
  base: Base;
  d: Documento;
  setD: (x: Documento) => void;
}) {
  const [aba, setAba] = useState<Aba>("ataques");

  /**
   * Toda pericia da base, treinada ou nao -- destreinada tambem se rola.
   *
   * Ficam de fora dois grupos, e por criterios DIFERENTES -- foi o que me
   * pegou na primeira tentativa:
   *
   * 1. as DEZESSEIS de reino do Kingmaker (Agriculture, Arts, Boating,
   *    Defense, Engineering, Exploration, Folklore, Industry, Intrigue, Magic,
   *    Politics, Scholarship, Statecraft, Trade, Warfare, Wilderness), que
   *    trazem `lore: true`;
   * 2. o `Lore` generico, que traz **`lore: false`** e por isso escapa do
   *    criterio acima. Ele e a CATEGORIA, nao uma pericia: o personagem tem
   *    `Lore: Alcohol`, nunca "Lore".
   *
   * Regra de reino esta fora do escopo do projeto, e essas dezesseis nao tem
   * `attribute` -- caiam no fallback de INT e apareciam somando +INT numa ficha
   * comum, ao lado das 17 de verdade. As Lore que o personagem TEM (a
   * `Lore: Alcohol` que o background Barkeep concede) entram logo abaixo, por
   * `proficiencias`, que e de onde elas realmente vem.
   */
  const pericias = useMemo(() => {
    const linhas = [...base.por_id.values()]
      .filter((r) => r.kind === "skill" && r.lore !== true && r.id !== "wb:skill/lore")
      .map((r) => {
        const chave = r.id.split("/").pop()!;
        const rank = (v.proficiencias[chave] ?? "untrained") as Rank;
        const attr = (Array.isArray(r.attribute) ? r.attribute[0] : "int") as string;
        const mod = v.modificadores[attr] ?? 0;
        // RAW: destreinada NAO soma o nivel, so o atributo
        const total = rank === "untrained" ? mod : v.nivel + RANK_BONUS[rank] + mod;
        return { chave, nome: r.name ?? chave, rank, attr, total };
      });
    // as Lore que o personagem tem entram junto, com a mesma conta
    for (const [chave, rank] of Object.entries(v.proficiencias)) {
      if (!chave.startsWith("lore:")) continue;
      const mod = v.modificadores.int ?? 0;
      linhas.push({
        chave, nome: nomeDeLore(chave), rank: rank as Rank, attr: "int",
        total: rank === "untrained" ? mod : v.nivel + RANK_BONUS[rank as Rank] + mod,
      });
    }
    return linhas.sort((a, b) => a.nome.localeCompare(b.nome));
  }, [base, v]);

  const salva = (chave: string) => {
    const rank = (v.proficiencias[chave] ?? "untrained") as Rank;
    const attr = chave === "fortitude" ? "con" : chave === "reflex" ? "dex" : "wis";
    const mod = v.modificadores[attr] ?? 0;
    return {
      rank,
      total: rank === "untrained" ? mod : v.nivel + RANK_BONUS[rank] + mod,
    };
  };

  const perc = salva("perception");

  return (
    <aside className="painel-direito">
      <section className="bloco topo-ficha">
        <div className="linha-atributos">
          {ATRIBUTOS.map((a) => (
            <div key={a} className="atributo">
              <span className="rotulo">{a.toUpperCase()}</span>
              <strong>{sinal(v.modificadores[a] ?? 0)}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="bloco defesas">
        <div className="ca" title={v.ac.detalhe}>
          <IconeEscudo />
          <span className="rotulo">CA</span>
          <strong>{v.ac.total}</strong>
        </div>
        <div className="defesas-direita">
          <div className="barras">
            {/* faixa, preenchimento e texto empilhados em grid */}
            <div className="barra">
              <span className="faixa" />
              <span className="preenchida" style={{ width: "100%" }} />
              <span className="rotulo">HP {v.hp}/{v.hp}</span>
            </div>
            <div className="barra vazia">
              <span className="faixa" />
              <span className="rotulo">Sem escudo</span>
            </div>
          </div>
          <div className="saves">
            {SALVAGUARDAS.map(([chave, nome]) => {
              const s = salva(chave);
              return (
                <div key={chave} className="save">
                  <span className={`prof p-${s.rank}`}>{SIGLA[s.rank]}</span>
                  <strong>{sinal(s.total)}</strong>
                  <span className="nome">{nome}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <div className="ficha-corpo">
        {/* a coluna estreita: o que se consulta a toda rolagem */}
        <div className="coluna-pericias">
          <div className="cartao-mini percepcao">
            <div className="save">
              <span className={`prof p-${perc.rank}`}>{SIGLA[perc.rank]}</span>
              <strong>{sinal(perc.total)}</strong>
              <span className="nome">Percepcao</span>
            </div>
            <div className="save">
              <strong>{v.focus_pool}</strong>
              <span className="nome">Pontos de foco</span>
            </div>
          </div>

          <div className="cartao-mini">
            <ul className="lista-pericias">
              {pericias.map((s) => (
                <li key={s.chave} title={(p.origem_proficiencia.get(s.chave) ?? []).join(", ")}>
                  <span className={`prof p-${s.rank}`}>{SIGLA[s.rank]}</span>
                  <strong>{sinal(s.total)}</strong>
                  <span className="nome">{s.nome}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <section className="area-abas">
          <nav className="menu-abas">
            {([
              ["ataques", `Ataques (${v.ataques.length})`],
              ["equipamento", `Equipamento (${(d.inventario ?? []).length})`],
              ["feats", "Feats"],
              ["concedido", `Concedido (${v.concedidos.length})`],
              ["sinais", `Sinais (${v.fora_do_requisito.length + v.avisos.length})`],
            ] as const).map(([id, rotulo]) => (
              <button key={id} className={aba === id ? "sel" : ""}
                      onClick={() => setAba(id)}>
                {rotulo}
              </button>
            ))}
          </nav>

          {aba === "ataques" && (
            <ul className="lista-simples">
              {v.ataques.map((a, i) => (
                <li key={i}>
                  <strong>{sinal(a.ataque)}</strong>
                  <span className="nome">{a.arma}</span>
                  <span className="dado">{a.dano} {a.tipo_de_dano}</span>
                  <span className="origem">{a.detalhe}</span>
                </li>
              ))}
              {!v.ataques.length && (
                <li className="vazio">nenhuma arma equipada no documento</li>
              )}
            </ul>
          )}

          {aba === "equipamento" && <Equipamento base={base} d={d} setD={setD} />}

          {aba === "feats" && (
            <ul className="lista-simples">
              {v.features.map((f, i) => (
                <li key={`${f.id}-${i}`}>
                  <span className="quando">
                    {f.nivel_de_classe != null ? `nv${f.nivel_de_classe}` : ""}
                  </span>
                  <span className="nome">{f.nome}</span>
                  <span className="origem">{f.classe ?? f.origem}</span>
                </li>
              ))}
              {!v.features.length && <li className="vazio">nada ainda</li>}
            </ul>
          )}

          {aba === "concedido" && (
            <ul className="lista-simples">
              {v.concedidos.filter((c) => c.nome !== c.por).map((c) => (
                <li key={c.id}>
                  <span className="nome">{c.nome}</span>
                  <span className="origem">via {c.por}</span>
                </li>
              ))}
              {!v.concedidos.length && (
                <li className="vazio">nada concedido automaticamente</li>
              )}
            </ul>
          )}

          {aba === "sinais" && (
            <>
              <p className="nota">
                o requisito <strong>sugere e ordena</strong> -- nada aqui impede a
                ficha de existir
              </p>
              <ul className="lista-simples">
                {v.fora_do_requisito.map((f, i) => (
                  <li key={`r${i}`}>
                    <span className="nome">{f.feat}</span>
                    <span className="origem">{f.motivo}</span>
                  </li>
                ))}
                {v.avisos.map((a, i) => (
                  <li key={`a${i}`}><span className="origem">{a}</span></li>
                ))}
                {!v.fora_do_requisito.length && !v.avisos.length && (
                  <li className="vazio">nada a apontar</li>
                )}
              </ul>
            </>
          )}
        </section>
      </div>
    </aside>
  );
}
