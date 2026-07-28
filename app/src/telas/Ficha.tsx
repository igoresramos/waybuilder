/**
 * A ficha -- a visao calculada.
 *
 * Regra da tela: **todo numero mostra de onde veio**. O motor ja carrega a
 * origem de cada rank (`origem_proficiencia`) e de cada ponto de HP
 * (`hp_detalhe`); um construtor que mostra so o total obriga o jogador a
 * confiar, e confiar em software de regra e o que faz ninguem achar o erro.
 *
 * A outra regra: aviso e AVISO. `fora_do_requisito` sugere e ordena -- pintar
 * de vermelho de bloqueio seria mentir sobre a regra do projeto.
 */
import type { Visao } from "../motor/tipos";

interface Props {
  v: Visao;
  origemProficiencia?: Record<string, string[]>;
  hpDetalhe?: Array<{ origem: string; hp: number; nota?: string }>;
}

const NOME_ATRIBUTO: Record<string, string> = {
  str: "FOR", dex: "DES", con: "CON", int: "INT", wis: "SAB", cha: "CAR",
};

export function Ficha({ v, origemProficiencia = {}, hpDetalhe = [] }: Props) {
  const classes = Object.entries(v.classes)
    .map(([nome, n]) => `${nome} ${n}`)
    .join(" / ");

  return (
    <div className="ficha">
      <section className="cabecalho">
        <div className="titulo">
          <h2>{classes || "sem classe"}</h2>
          <p className="sub">
            nivel {v.nivel}
            {v.ancestralidade && ` - ${v.ancestralidade}`}
            {v.heranca && ` (${v.heranca})`}
            {v.background && ` - ${v.background}`}
          </p>
        </div>
        <div className="vitais">
          <div className="vital" title={hpDetalhe.map((d) => `${d.origem}: ${d.hp}`).join("\n")}>
            <strong>{v.hp}</strong>
            <span>HP</span>
          </div>
          <div className="vital">
            <strong>{v.ac}</strong>
            <span>CA</span>
          </div>
        </div>
      </section>

      <section className="atributos">
        {Object.entries(v.atributos).map(([a, valor]) => (
          <div key={a} className="atributo">
            <span className="rotulo">{NOME_ATRIBUTO[a] ?? a.toUpperCase()}</span>
            <strong>{valor}</strong>
            <span className="mod">
              {v.modificadores[a] >= 0 ? "+" : ""}
              {v.modificadores[a]}
            </span>
          </div>
        ))}
      </section>

      {v.slots_abertos.length > 0 && (
        <section className="pendencias">
          <h3>Falta escolher ({v.slots_abertos.length})</h3>
          <ul>
            {v.slots_abertos.map((s, i) => (
              <li key={`${s.slot}-${s.em}-${i}`}>
                <span className="quando">{s.em}</span>
                {s.rotulo}
                {s.escolhe > 1 && <span className="qtd"> x{s.escolhe}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="pericias">
        <h3>Proficiencias</h3>
        <ul>
          {Object.entries(v.proficiencias)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([chave, rank]) => (
              <li key={chave}>
                <span className="chave">{chave.replace("lore:", "Lore: ")}</span>
                <span className={`rank r-${rank}`}>{rank}</span>
                {/* de onde veio -- e o que permite conferir em vez de confiar */}
                <span className="origem">
                  {(origemProficiencia[chave] ?? []).join(", ")}
                </span>
              </li>
            ))}
        </ul>
      </section>

      {v.features.length > 0 && (
        <section className="features">
          <h3>Identidade de classe</h3>
          <ul>
            {v.features.map((f, i) => (
              <li key={`${f.id}-${i}`}>
                {f.nivel_de_classe != null && (
                  <span className="quando">nv{f.nivel_de_classe}</span>
                )}
                {f.nome}
                {f.classe && <span className="de"> {f.classe}</span>}
                {!f.na_base && <span className="alerta">ausente da base</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {v.concedidos.length > 0 && (
        <section className="concedidos">
          <h3>Concedido (nao escolhido)</h3>
          <ul>
            {v.concedidos
              .filter((c) => c.nome !== c.por)
              .map((c) => (
                <li key={c.id}>
                  {c.nome} <span className="de">via {c.por}</span>
                </li>
              ))}
          </ul>
        </section>
      )}

      {v.conjuracao.length > 0 && (
        <section className="conjuracao">
          <h3>Conjuracao</h3>
          {v.conjuracao.map((c, i) => (
            <div key={i} className="tradicao">
              <h4>
                {c.classe} {c.nivel_de_classe} - {c.tradicao} ({c.tipo})
              </h4>
              <p>
                DC {c.dc.dc}, ataque {c.dc.ataque >= 0 ? "+" : ""}
                {c.dc.ataque} - rank efetivo {c.rank_efetivo}
                {c.elevacao > 0 && ` (+${c.elevacao} pela regra 17)`}
              </p>
              <p className="slots">
                {Object.entries(c.slots)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([rank, n]) => `rank ${rank}: ${n}`)
                  .join("  -  ") || "sem slots"}
              </p>
            </div>
          ))}
        </section>
      )}

      {v.fora_do_requisito.length > 0 && (
        <section className="sinais">
          <h3>Fora do requisito</h3>
          <p className="nota">
            o predicado <strong>sugere e ordena</strong> -- nada aqui impede a
            ficha de existir
          </p>
          <ul>
            {v.fora_do_requisito.map((f, i) => (
              <li key={i}>
                <strong>{f.feat}</strong>: {f.motivo}
              </li>
            ))}
          </ul>
        </section>
      )}

      {v.avisos.length > 0 && (
        <section className="sinais">
          <h3>Avisos</h3>
          <ul>
            {v.avisos.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
