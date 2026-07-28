/**
 * Waybuilder -- construtor de personagem de Pathfinder 2e com a regra caseira
 * de multiclasse.
 *
 * Fatia vertical 1: montar do zero ate o nivel 4, com Free Archetype ligado.
 *
 * O fluxo da tela e o fluxo do documento: a UI edita `escolhas[]` e o motor
 * re-deriva TUDO a cada mudanca. Nao ha estado calculado guardado -- se
 * houvesse, mudanca de regra invalidaria ficha salva, que e exatamente o que a
 * arquitetura evita.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { Base } from "./motor/base";
import { Personagem } from "./motor/personagem";
import type { Documento, Registro } from "./motor/tipos";
import { carregarNucleo } from "./carregarBase";
import { Picker } from "./componentes/Picker";
import { Ficha } from "./telas/Ficha";
import * as doc from "./doc";
import "./estilo.css";

type Aba = "criacao" | "progressao" | "ficha";

const SLOTS_DO_NIVEL = [
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
  const [aba, setAba] = useState<Aba>("criacao");
  const arquivo = useRef<HTMLInputElement>(null);

  useEffect(() => {
    carregarNucleo()
      .then((r) => setBase(r.base))
      .catch((e) => setErro(String(e)));
  }, []);

  // salva a cada mudanca: sem botao de salvar, sem perder trabalho por fechar
  // a aba. O documento e pequeno e localStorage e sincrono.
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
        <p className="nota">
          rode <code>./sincronizar-base.sh</code> em <code>app/</code>
        </p>
      </div>
    );
  }
  if (!base || !p || !v) {
    return <div className="carregando">carregando a base...</div>;
  }

  const nivel = doc.nivelDoPersonagem(d);
  const opcoesDe = (kind: string): Registro[] =>
    [...base.por_id.values()].filter((r) => r.kind === kind);
  const escolhaEm = (slot: string, em: number | "criacao") =>
    (d.escolhas.find((e) => e.slot === slot && e.em === em)?.pega as string) ??
    null;
  const cru = (rs: Registro[]) =>
    rs.map((r) => ({
      id: r.id, nome: r.name, level: r.level ?? null,
      atende: true, motivos: [] as string[], ja_pego: false,
    }));

  return (
    <div className="app">
      <header className="topo">
        <div className="marca">
          <h1>Waybuilder</h1>
          <input
            className="nome"
            value={d.identidade?.nome ?? ""}
            onChange={(e) =>
              setD({ ...d, identidade: { ...d.identidade, nome: e.target.value } })
            }
            placeholder="nome do personagem"
          />
        </div>
        <nav>
          {(["criacao", "progressao", "ficha"] as Aba[]).map((a) => (
            <button
              key={a}
              className={aba === a ? "ativa" : ""}
              onClick={() => setAba(a)}
            >
              {a}
            </button>
          ))}
        </nav>
        <div className="acoes">
          <button onClick={() => doc.exportar(d)}>exportar</button>
          <button onClick={() => arquivo.current?.click()}>importar</button>
          <input
            ref={arquivo}
            type="file"
            accept="application/json"
            hidden
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

      <div className="resumo">
        <span>nivel {nivel}</span>
        <span>{v.hp} HP</span>
        <span>CA {v.ac}</span>
        <span className={v.slots_abertos.length ? "pend" : "ok"}>
          {v.slots_abertos.length} pendencia(s)
        </span>
      </div>

      <main>
        {aba === "criacao" && (
          <section className="painel">
            {(
              [
                ["ancestralidade", "ancestry", "Ancestralidade"],
                ["heranca", "heritage", "Heranca"],
                ["background", "background", "Background"],
              ] as const
            ).map(([slot, kind, rotulo]) => (
              <Picker
                key={slot}
                titulo={rotulo}
                escolhido={escolhaEm(slot, "criacao")}
                candidatos={cru(opcoesDe(kind))}
                aoEscolher={(x) => setD(doc.escolher(d, slot, "criacao", x))}
                aoLimpar={() => setD(doc.limpar(d, slot, "criacao"))}
              />
            ))}

            <div className="picker">
              <header>
                <h4>Boosts de atributo</h4>
              </header>
              <p className="nota">
                {v.boosts.declarados} de {v.boosts.direito} escolhidos
              </p>
              <ul className="fontes">
                {v.boosts.fontes.map((f, i) => (
                  <li key={i}>
                    {f.origem}: {f.quantidade}{" "}
                    {f.opcoes ? `(entre ${f.opcoes.join("/")})` : "(livre)"}
                  </li>
                ))}
              </ul>
              <BoostPicker d={d} setD={setD} />
            </div>
          </section>
        )}

        {aba === "progressao" && (
          <section className="painel">
            {nivel === 0 && (
              <p className="nota">
                nenhum nivel ainda -- suba para o nivel 1 para comecar
              </p>
            )}
            <div className="niveis">
              {Array.from({ length: nivel }, (_, i) => i + 1).map((n) => (
                <div key={n} className="nivel">
                  <h3>nivel {n}</h3>

                  <Picker
                    titulo="Classe deste nivel (a houserule)"
                    escolhido={escolhaEm("nivel_de_classe", n)}
                    candidatos={cru(opcoesDe("class"))}
                    aoEscolher={(x) => setD(doc.definirClasseDoNivel(d, n, x))}
                  />

                  {SLOTS_DO_NIVEL.filter((s) =>
                    (v.slots[s.cadencia] ?? []).includes(n),
                  ).map((s) => (
                    <Picker
                      key={s.slot}
                      titulo={s.rotulo}
                      escolhido={escolhaEm(s.slot, n)}
                      candidatos={p.candidatos(s.slot, n)}
                      aoEscolher={(x) => setD(doc.escolher(d, s.slot, n, x))}
                      aoLimpar={() => setD(doc.limpar(d, s.slot, n))}
                    />
                  ))}

                  {v.aumentos_de_pericia.niveis.includes(n) && (
                    <Picker
                      titulo="Aumento de pericia"
                      escolhido={escolhaEm("skill_increase", n)}
                      candidatos={p.candidatos("skill_increase", n)}
                      aoEscolher={(x) =>
                        setD(doc.escolher(d, "skill_increase", n, x))
                      }
                      aoLimpar={() => setD(doc.limpar(d, "skill_increase", n))}
                    />
                  )}

                  {v.subclasses
                    .filter((b) => b.nivel === n && !b.escolhido)
                    .map((b, i) => (
                      <Picker
                        key={`sub-${i}`}
                        titulo={`${b.classe} / ${b.eixo}`}
                        escolhido={escolhaEm("subclasse", n)}
                        candidatos={p.candidatos("subclasse", n)}
                        aoEscolher={(x) => setD(doc.escolher(d, "subclasse", n, x))}
                        aoLimpar={() => setD(doc.limpar(d, "subclasse", n))}
                      />
                    ))}
                </div>
              ))}
            </div>

            <div className="controles">
              <button
                onClick={() => {
                  const anterior =
                    escolhaEm("nivel_de_classe", nivel) ?? opcoesDe("class")[0]?.id;
                  if (anterior) {
                    setD(doc.definirClasseDoNivel(d, nivel + 1, anterior));
                  }
                }}
              >
                + subir para o nivel {nivel + 1}
              </button>
              {nivel > 0 && (
                <button onClick={() => setD(doc.removerUltimoNivel(d))}>
                  - remover o nivel {nivel}
                </button>
              )}
            </div>
          </section>
        )}

        {aba === "ficha" && (
          <Ficha
            v={v}
            origemProficiencia={p.origem_proficiencia}
            hpDetalhe={p.hp_detalhe}
          />
        )}
      </main>
    </div>
  );
}

/**
 * Boost e o unico slot que aceita VARIAS entradas no mesmo nivel -- por isso
 * nao passa pelo `escolher` comum, que substitui por (slot, nivel).
 */
function BoostPicker({
  d, setD,
}: {
  d: Documento;
  setD: (x: Documento) => void;
}) {
  const [sel, setSel] = useState<string[]>([]);
  return (
    <div className="boosts">
      <div className="linha">
        {ATRIBUTOS.map((a) => (
          <button
            key={a}
            className={sel.includes(a) ? "sel" : ""}
            onClick={() =>
              setSel(sel.includes(a) ? sel.filter((x) => x !== a) : [...sel, a])
            }
          >
            {a.toUpperCase()}
          </button>
        ))}
      </div>
      <button
        disabled={!sel.length}
        onClick={() => {
          const quantos = d.escolhas.filter(
            (e) => e.slot === "boosts_livres",
          ).length;
          setD(doc.definirBoosts(d, "criacao", quantos, sel));
          setSel([]);
        }}
      >
        adicionar {sel.length || ""} boost(s)
      </button>
      <ul className="fontes">
        {d.escolhas
          .filter((e) => e.slot === "boosts_livres")
          .map((e, i) => (
            <li key={i}>{(e.pega as string[]).join(", ").toUpperCase()}</li>
          ))}
      </ul>
    </div>
  );
}
