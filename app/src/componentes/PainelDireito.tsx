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
import { useState } from "react";
import type { Base } from "../motor/base";
import type { Personagem } from "../motor/personagem";
import type { Documento, Rank, Visao } from "../motor/tipos";
import { IconeEscudo } from "./Icones";
import { Equipamento } from "./Equipamento";

const SIGLA: Record<Rank, string> = {
  untrained: "U", trained: "T", expert: "E", master: "M", legendary: "L",
};
const ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"] as const;
const SALVAGUARDAS = [
  ["fortitude", "Fortitude"], ["reflex", "Reflexos"], ["will", "Vontade"],
] as const;

type Aba = "ataques" | "equipamento" | "feats" | "magia" | "companheiro"
  | "concedido" | "sinais";

const sinal = (n: number) => `${n >= 0 ? "+" : ""}${n}`;


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
  // A conta (`nivel + RANK_BONUS[rank] + mod`) morava AQUI, em tres lugares
  // deste arquivo. Numero que nasce no componente React nao tem oraculo, nao
  // tem paridade com o Python e nao tem onde receber `flat_modifier` -- foi por
  // isso que 462 bonus incondicionais da base nunca chegaram na ficha. Agora o
  // motor calcula e a tela so LE.
  // Spec: `specs/2026-07-30-bonus-de-pericia-e-salva.md`
  const pericias = v.pericias;

  const salva = (chave: string) => v.salvas[chave];

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
            {/* A divindade escolhida. Sem esta linha a escolha nao muda nada
                VISIVEL, que era metade do defeito do item 98 -- a base tinha
                488 divindades estruturadas e nenhum consumidor.
                Spec: `specs/2026-07-30-divindade-na-ficha.md`. */}
            {v.divindade && (
              <div className="save deidade">
                <span className="nome">{v.divindade.nome}</span>
                <span className="origem">
                  {[
                    v.divindade.fonte_divina.length
                      ? `fonte ${v.divindade.fonte_divina.join("/")}`
                      : null,
                    v.divindade.arma_favorita.length
                      ? v.divindade.arma_favorita.map((a) => a.nome).join(", ")
                      : null,
                    v.divindade.dominios.length
                      ? v.divindade.dominios.map((d) => d.nome).join(", ")
                      : null,
                  ].filter(Boolean).join("  -  ")}
                </span>
              </div>
            )}
            {/* Velocidade por modo. A ficha do companheiro ja mostrava; a do
                personagem nao tinha o numero -- spec `2026-07-30-velocidade.md`. */}
            {Object.entries(v.velocidade).map(([modo, pes]) => (
              <div className="save" key={modo}>
                <strong>{pes}</strong>
                <span className="nome">
                  {modo === "land" ? "Velocidade" : `Velocidade (${modo})`}
                </span>
              </div>
            ))}
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
              // A conjuracao era calculada desde sempre e NUNCA aparecia: o
              // unico bloco que a mostrava vivia numa tela que ninguem
              // importava (removida em 2026-07-29). Some quando o personagem
              // nao conjura.
              ...(v.conjuracao.length
                ? [["magia", `Magia (${v.conjuracao.length})`] as const]
                : []),
              // a aba do bicho so existe quando ha bicho -- ela some inteira em
              // vez de ficar vazia, que e o que 90% das fichas veriam
              ...(v.atores.length
                ? [["companheiro", `Companheiro (${v.atores.length})`] as const]
                : []),
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
                  <span className="dado">{a.dano.total} {a.tipo_de_dano}</span>
                  <span className="origem">{a.detalhe}</span>
                  {/* o dano decomposto: a soma sozinha não diz de onde veio, e
                      era essa a lacuna -- Weapon Specialization e dano de fúria
                      nem entravam na conta.
                      Spec: `specs/2026-07-30-dano-de-furia.md` */}
                  <span className="parcelas-de-dano">
                    {a.dano.parcelas.map((p, j) => (
                      <span key={j} className="parcela">
                        {p.tipo === "dados" ? p.texto : sinal(p.valor ?? 0)}
                        <em>{p.origem}</em>
                      </span>
                    ))}
                  </span>
                  {/* condicional NÃO entra no total: aparece com a condição
                      escrita. Princípio zero -- marca, nunca esconde. */}
                  {a.dano.condicionais.map((c, j) => (
                    <span key={j} className="parcela condicional">
                      {sinal(c.valor)}<em>{c.origem} — só com {c.condicao}</em>
                    </span>
                  ))}
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

          {/* Os numeros ja vem prontos do motor (`_ficha_de_companheiro`), que
              deriva do stat block da especie mais o avanco young/mature/nimble/
              savage e o cap da regra 17b. A tela nao calcula nada aqui -- e a
              mesma regra do resto da ficha. */}
          {aba === "companheiro" && v.atores.map((a, i) => (
            <div key={`${a.concedido_por ?? a.nome}-${i}`} className="cartao-ator">
              <h4>
                {a.nome || a.especie || a.tipo}
                {a.especie && a.nome ? ` - ${a.especie}` : ""}
                <span className="origem">
                  nivel {a.nivel}
                  {a.classe ? ` (${a.classe} ${a.nivel_de_classe})` : ""}
                  {a.maturidade ? ` - ${a.maturidade}` : ""}
                  {a.especializado ? " especializado" : ""}
                </span>
              </h4>
              {a.aviso && <p className="nota">{a.aviso}</p>}
              {a.nota && <p className="nota">{a.nota}</p>}
              {a.hp != null && (
                <>
                  <div className="linha-atributos">
                    {ATRIBUTOS.map((x) => (
                      <div key={x} className="atributo">
                        <span className="rotulo">{x.toUpperCase()}</span>
                        <strong>{sinal(a.atributos?.[x] ?? 0)}</strong>
                      </div>
                    ))}
                  </div>
                  <ul className="lista-simples">
                    <li title={a.hp_detalhe}>
                      <strong>{a.hp}</strong>
                      <span className="nome">HP</span>
                      {/* `velocidade` vem por modo (`{land: 40, fly: 25}`) --
                          `max` e derivado e nao se mostra duas vezes */}
                      <span className="origem">
                        {[a.tamanho, ...Object.entries(a.velocidade ?? {})
                          .filter(([modo]) => modo !== "max")
                          .map(([modo, pes]) => `${modo} ${pes} ft`)]
                          .filter(Boolean).join(" - ")}
                      </span>
                    </li>
                    <li>
                      <strong>{a.ac}</strong>
                      <span className="nome">CA</span>
                      <span className="origem">
                        Percepcao {sinal(a.percepcao ?? 0)}
                      </span>
                    </li>
                    {a.sentidos && (
                      <li>
                        <span className="nome">Sentidos</span>
                        <span className="origem" title={a.sentidos}>
                          {a.sentidos.replace(/\s+/g, " ").trim()}
                        </span>
                      </li>
                    )}
                    <li>
                      <span className="nome">Salvaguardas</span>
                      <span className="origem">
                        {SALVAGUARDAS.map(([chave, nome]) =>
                          `${nome} ${sinal(a.saves?.[chave] ?? 0)}`).join("  -  ")}
                      </span>
                    </li>
                    {(a.ataques ?? []).map((atk, j) => (
                      <li key={`atk${j}`}>
                        <strong>{sinal(atk.ataque)}</strong>
                        <span className="nome">{atk.nome}</span>
                        <span className="dado">{atk.dano} {atk.tipo}</span>
                      </li>
                    ))}
                  </ul>
                  {a.support && (
                    <p className="nota"><strong>Support:</strong> {a.support}</p>
                  )}
                  {a.manobra_avancada && (
                    <p className="nota">
                      <strong>Manobra avancada:</strong> {a.manobra_avancada}
                    </p>
                  )}
                </>
              )}
            </div>
          ))}

          {aba === "magia" && v.conjuracao.map((c, i) => (
            <div key={`${c.classe}-${i}`} className="cartao-ator">
              <h4>
                {c.classe}
                <span className="origem">
                  {c.tradicao ?? "tradicao a definir"}
                  {c.tipo ? ` - ${c.tipo}` : ""}
                  {c.de_arquetipo
                    ? " - de arquetipo (nao eleva)"
                    : c.nivel_de_classe != null ? ` - nivel de classe ${c.nivel_de_classe}` : ""}
                </span>
              </h4>
              <ul className="lista-simples">
                <li>
                  <strong>{c.dc.dc}</strong>
                  <span className="nome">DC</span>
                  <span className="origem">
                    ataque {sinal(c.dc.ataque)} - {c.dc.rank}
                  </span>
                </li>
                <li>
                  <strong>{c.truques ?? 0}</strong>
                  <span className="nome">Truques</span>
                  {/* a elevacao da regra 17 e o numero mais surpreendente da
                      houserule: o slot vem da classe, a potencia do personagem */}
                  <span className="origem">
                    rank efetivo {c.rank_efetivo}
                    {c.elevacao > 0 ? ` (+${c.elevacao} pela regra 17)` : ""}
                  </span>
                </li>
                {Object.entries(c.slots)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([rank, quantos]) => (
                    <li key={rank}>
                      <strong>{quantos}</strong>
                      <span className="nome">slots de rank {rank}</span>
                    </li>
                  ))}
                {!Object.keys(c.slots).length && (
                  <li className="vazio">
                    sem slot -- so os truques (falta o feat de Spellcasting)
                  </li>
                )}
              </ul>
            </div>
          ))}

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
