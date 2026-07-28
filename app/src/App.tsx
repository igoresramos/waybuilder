/**
 * Waybuilder -- construtor de personagem de Pathfinder 2e com a regra caseira
 * de multiclasse.
 *
 * DUAS COLUNAS, como o Pathbuilder: o build a esquerda, a ficha viva a
 * direita. A primeira versao tinha abas separadas e o jogador escolhia um feat
 * sem ver o numero mudar -- num construtor, o retorno imediato e o ponto todo.
 *
 * A esquerda mostra TODOS os niveis ate o alvo, nao so os ja preenchidos: um
 * build de Pathfinder e planejamento, e o jogador quer ver onde os slots caem
 * la na frente antes de decidir o de agora.
 *
 * O documento continua sendo a unica fonte de verdade: a tela edita
 * `escolhas[]` e o motor re-deriva tudo a cada mudanca.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { Base } from "./motor/base";
import { Personagem } from "./motor/personagem";
import type { Candidato, Documento, Registro } from "./motor/tipos";
import { carregarNucleo } from "./carregarBase";
import { Slot, FILTROS_DE_FEAT, FILTROS_DE_RARIDADE } from "./componentes/Slot";
import { PainelDireito } from "./componentes/PainelDireito";
import { IconeCog } from "./componentes/Icones";
import * as doc from "./doc";
import "./estilo.css";

const TRILHOS = [
  { slot: "class_feat", cadencia: "class", rotulo: "Feat de classe" },
  { slot: "skill_feat", cadencia: "skill", rotulo: "Feat de pericia" },
  { slot: "general_feat", cadencia: "general", rotulo: "Feat geral" },
  { slot: "ancestry_feat", cadencia: "ancestry", rotulo: "Feat de ancestria" },
  { slot: "free_archetype", cadencia: "free_archetype", rotulo: "Free Archetype" },
] as const;

const ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"];

export default function App() {
  const [base, setBase] = useState<Base | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [d, setD] = useState<Documento>(() => doc.novoDocumento());
  const [id] = useState(() => doc.novoId());
  const [alvo, setAlvo] = useState(4);
  const arquivo = useRef<HTMLInputElement>(null);

  useEffect(() => {
    carregarNucleo().then((r) => setBase(r.base)).catch((e) => setErro(String(e)));
  }, []);
  useEffect(() => {
    if (d.escolhas.length) doc.salvar(id, d);
  }, [d, id]);

  const p = useMemo(
    () => (base ? new Personagem(structuredClone(d), base) : null),
    [base, d],
  );
  const v = p?.visao();

  if (erro) {
    return (
      <div className="carregando erro">
        <h1>nao carregou a base</h1>
        <p>{erro}</p>
        <p className="nota">rode <code>./sincronizar-base.sh</code> em <code>app/</code></p>
      </div>
    );
  }
  if (!base || !p || !v) return <div className="carregando">carregando a base...</div>;

  const nivel = doc.nivelDoPersonagem(d);
  const opcoesDe = (kind: string): Registro[] =>
    [...base.por_id.values()].filter((r) => r.kind === kind);
  const cru = (rs: Registro[]): Candidato[] =>
    rs.map((r) => ({
      id: r.id, nome: r.name ?? null, level: r.level ?? null,
      atende: true, motivos: [], ja_pego: false,
    })).sort((a, b) => (a.nome ?? "").localeCompare(b.nome ?? ""));
  const escolhaEm = (slot: string, em: number | "criacao") =>
    (d.escolhas.find((e) => e.slot === slot && e.em === em)?.pega as string) ?? null;

  const classePrincipal = escolhaEm("nivel_de_classe", 1);

  return (
    <div className="app">
      <header className="topo">
        <input
          className="nome"
          value={d.identidade?.nome ?? ""}
          onChange={(e) =>
            setD({ ...d, identidade: { ...d.identidade, nome: e.target.value } })}
          placeholder="nome do personagem"
        />
        <span className="resumo-classe">
          {Object.entries(v.classes).map(([n, q]) => `${n} ${q}`).join(" / ") ||
            "sem classe"}
        </span>
        <div className="alvo">
          <label>montar ate o nivel</label>
          <input
            type="number" min={1} max={20} value={alvo}
            onChange={(e) => setAlvo(Math.max(1, Math.min(20, +e.target.value || 1)))}
          />
        </div>
        <div className="acoes">
          <button onClick={() => doc.exportar(d)}>exportar</button>
          <button onClick={() => arquivo.current?.click()}>importar</button>
          <input
            ref={arquivo} type="file" accept="application/json" hidden
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              const { doc: lido, erro: falha } = doc.importar(await f.text());
              if (falha) alert(falha);
              else if (lido) setD(lido);
              e.target.value = "";
            }}
          />
        </div>
      </header>

      <div className="colunas">
        <main className="coluna-build">
          <section className="bloco identidade">
            <Slot base={base} rotulo="Ancestralidade" tipo="ancestralidade"
                  candidatos={cru(opcoesDe("ancestry"))} filtros={FILTROS_DE_RARIDADE}
                  escolhido={escolhaEm("ancestralidade", "criacao")}
                  aoEscolher={(x) => setD(doc.escolher(d, "ancestralidade", "criacao", x))}
                  aoLimpar={() => setD(doc.limpar(d, "ancestralidade", "criacao"))} />
            {/* candidatos, nao `cru`: heranca pertence a uma ancestralidade, e
                quem sabe disso e o motor */}
            <Slot base={base} rotulo="Heranca" tipo="heranca"
                  candidatos={p.candidatos("heranca")} filtros={FILTROS_DE_RARIDADE}
                  escolhido={escolhaEm("heranca", "criacao")}
                  aoEscolher={(x) => setD(doc.escolher(d, "heranca", "criacao", x))}
                  aoLimpar={() => setD(doc.limpar(d, "heranca", "criacao"))} />
            <Slot base={base} rotulo="Background" tipo="background"
                  candidatos={cru(opcoesDe("background"))} filtros={FILTROS_DE_RARIDADE}
                  escolhido={escolhaEm("background", "criacao")}
                  aoEscolher={(x) => setD(doc.escolher(d, "background", "criacao", x))}
                  aoLimpar={() => setD(doc.limpar(d, "background", "criacao"))} />

            <Boosts d={d} setD={setD}
                    declarados={v.boosts.declarados} direito={v.boosts.direito} />
          </section>

          {Array.from({ length: Math.max(alvo, nivel) }, (_, i) => i + 1).map((n) => (
            <section key={n} className={`bloco nivel ${n > nivel ? "futuro" : ""}`}>
              <h3>
                Nivel {n}
                {n > nivel && <span className="marca-futuro">nao alcancado</span>}
              </h3>

              <Slot base={base}
                rotulo="Classe deste nivel" tipo="class"
                candidatos={cru(opcoesDe("class"))}
                escolhido={escolhaEm("nivel_de_classe", n)}
                aoEscolher={(x) => setD(doc.definirClasseDoNivel(d, n, x))}
              />

              {n <= nivel && TRILHOS.filter((t) =>
                (v.slots[t.cadencia] ?? []).includes(n),
              ).map((t) => (
                <Slot base={base} key={t.slot} rotulo={t.rotulo} tipo={t.slot}
                      filtros={FILTROS_DE_FEAT}
                      candidatos={p.candidatos(t.slot, n)}
                      escolhido={escolhaEm(t.slot, n)}
                      aoEscolher={(x) => setD(doc.escolher(d, t.slot, n, x))}
                      aoLimpar={() => setD(doc.limpar(d, t.slot, n))} />
              ))}

              {n <= nivel && v.aumentos_de_pericia.niveis.includes(n) && (
                <Slot base={base} rotulo="Aumento de pericia" tipo="skill_increase"
                      candidatos={p.candidatos("skill_increase", n)}
                      escolhido={escolhaEm("skill_increase", n)}
                      aoEscolher={(x) => setD(doc.escolher(d, "skill_increase", n, x))}
                      aoLimpar={() => setD(doc.limpar(d, "skill_increase", n))} />
              )}

              {n <= nivel && v.subclasses.filter((b) => b.nivel === n).map((b, i) => (
                <Slot base={base} key={`sub${i}`} rotulo={`${b.classe} / ${b.eixo}`}
                      candidatos={p.candidatos("subclasse", n)}
                      escolhido={escolhaEm("subclasse", n)}
                      aoEscolher={(x) => setD(doc.escolher(d, "subclasse", n, x))}
                      aoLimpar={() => setD(doc.limpar(d, "subclasse", n))} />
              ))}

              {/* o que este nivel CONCEDEU -- nao e escolha, e consequencia */}
              {n <= nivel && (() => {
                const dadas = v.features.filter((f) => f.nivel_de_classe === n);
                return dadas.length ? (
                  <ul className="concedido-no-nivel">
                    {dadas.map((f, i) => <li key={i}>{f.nome}</li>)}
                  </ul>
                ) : null;
              })()}

              {n === nivel + 1 && (
                <button className="subir"
                        onClick={() => {
                          const anterior = escolhaEm("nivel_de_classe", nivel)
                            ?? classePrincipal ?? opcoesDe("class")[0]?.id;
                          if (anterior) setD(doc.definirClasseDoNivel(d, n, anterior));
                        }}>
                  + subir para o nivel {n}
                </button>
              )}
            </section>
          ))}

          {nivel > 0 && (
            <button className="remover" onClick={() => setD(doc.removerUltimoNivel(d))}>
              remover o nivel {nivel}
            </button>
          )}
        </main>

        <PainelDireito p={p} v={v} base={base} d={d} setD={setD} />
      </div>
    </div>
  );
}

/**
 * Boost de atributo: um botao-cog com o QUE FALTA sobreposto, como no
 * Pathbuilder. E a peca que resolve o problema de "escolha agregada" -- boost
 * nao e um slot com um valor, sao N escolhas que so importam somadas, e um
 * numero grande na engrenagem diz de relance quantas faltam sem ocupar linha.
 */
function Boosts({
  d, setD, declarados, direito,
}: {
  d: Documento; setD: (x: Documento) => void; declarados: number; direito: number;
}) {
  const [aberto, setAberto] = useState(false);
  const faltam = Math.max(0, direito - declarados);
  return (
    <>
      <div className="cogs">
        <button className={`cog ${faltam === 0 ? "pronto" : ""}`}
                onClick={() => setAberto(!aberto)}>
          <span className="cog-face">
            <IconeCog />
            <strong>{faltam === 0 ? declarados : faltam}</strong>
          </span>
          <span className="cog-rotulo">Boosts</span>
        </button>
      </div>
      {aberto && <BoostPicker d={d} setD={setD} />}
    </>
  );
}

/** Boost e o unico slot que aceita VARIAS entradas no mesmo nivel. */
function BoostPicker({ d, setD }: { d: Documento; setD: (x: Documento) => void }) {
  const [sel, setSel] = useState<string[]>([]);
  return (
    <div className="boost-picker">
      <div className="linha">
        {ATRIBUTOS.map((a) => (
          <button key={a} className={sel.includes(a) ? "sel" : ""}
                  onClick={() => setSel(sel.includes(a)
                    ? sel.filter((x) => x !== a) : [...sel, a])}>
            {a.toUpperCase()}
          </button>
        ))}
      </div>
      <button className="add" disabled={!sel.length}
              onClick={() => {
                const q = d.escolhas.filter((e) => e.slot === "boosts_livres").length;
                setD(doc.definirBoosts(d, "criacao", q, sel));
                setSel([]);
              }}>
        adicionar {sel.length || ""}
      </button>
      <ul className="declarados">
        {d.escolhas.filter((e) => e.slot === "boosts_livres").map((e, i) => (
          <li key={i}>
            {(e.pega as string[]).join(" ").toUpperCase()}
            <button className="slot-x" aria-label="remover boost"
                    onClick={() => setD({
                      ...d,
                      escolhas: d.escolhas.filter((x) => x !== e),
                    })}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
