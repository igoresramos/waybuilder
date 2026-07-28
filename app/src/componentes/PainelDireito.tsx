/**
 * A ficha viva -- fica SEMPRE visivel enquanto se monta, na coluna da direita.
 *
 * Foi o feedback que reorganizou o app: a primeira versao tinha abas separadas
 * (criacao / progressao / ficha), e o jogador escolhia um feat e tinha de
 * trocar de aba para ver o que mudou. Num construtor, o retorno imediato e o
 * ponto todo.
 *
 * Formato copiado do Pathbuilder, que o Igor usa: atributo vira MODIFICADOR
 * (`DEX +3`, nao `16`), e pericia mostra o TOTAL rolavel (`+8`), com o rank
 * como etiqueta ao lado. Numa mesa ninguem rola "expert" -- rola +8.
 */
import { useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Personagem } from "../motor/personagem";
import type { Rank, Visao } from "../motor/tipos";

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

type Aba = "pericias" | "ataques" | "feats" | "concedido" | "sinais";

export function PainelDireito({
  p, v, base,
}: {
  p: Personagem;
  v: Visao;
  base: Base;
}) {
  const [aba, setAba] = useState<Aba>("pericias");

  /** Toda pericia da base, treinada ou nao -- destreinada tambem se rola. */
  const pericias = useMemo(() => {
    const linhas = [...base.por_id.values()]
      .filter((r) => r.kind === "skill" && r.id !== "wb:skill/lore")
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
        chave, nome: `Lore: ${chave.slice(5)}`, rank: rank as Rank, attr: "int",
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
              <strong>{(v.modificadores[a] ?? 0) >= 0 ? "+" : ""}
                {v.modificadores[a] ?? 0}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="bloco defesas">
        <div className="ca" title={v.ac.detalhe}>
          <span className="rotulo">CA</span>
          <strong>{v.ac.total}</strong>
        </div>
        <div className="defesas-direita">
          <div className="barra-hp">
            <div className="preenchida" style={{ width: "100%" }} />
            <span>HP {v.hp}/{v.hp}</span>
          </div>
          <div className="saves">
            {SALVAGUARDAS.map(([chave, nome]) => {
              const s = salva(chave);
              return (
                <div key={chave} className="save">
                  <span className={`prof p-${s.rank}`}>{SIGLA[s.rank]}</span>
                  <strong>{s.total >= 0 ? "+" : ""}{s.total}</strong>
                  <span className="nome">{nome}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="bloco percepcao">
        <div className="save">
          <span className={`prof p-${perc.rank}`}>{SIGLA[perc.rank]}</span>
          <strong>{perc.total >= 0 ? "+" : ""}{perc.total}</strong>
          <span className="nome">Percepcao</span>
        </div>
        <div className="save">
          <strong>{v.focus_pool}</strong>
          <span className="nome">Pontos de foco</span>
        </div>
      </section>

      <section className="bloco abas">
        <nav className="menu-abas">
          {([
            ["pericias", "Pericias"],
            ["ataques", `Ataques (${v.ataques.length})`],
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

        {aba === "pericias" && (
          <ul className="lista-pericias">
            {pericias.map((s) => (
              <li key={s.chave}>
                <span className={`prof p-${s.rank}`}>{SIGLA[s.rank]}</span>
                <strong>{s.total >= 0 ? "+" : ""}{s.total}</strong>
                <span className="nome">{s.nome}</span>
                {/* de onde veio o rank -- e o que deixa conferir em vez de confiar */}
                <span className="origem">
                  {(p.origem_proficiencia.get(s.chave) ?? []).join(", ")}
                </span>
              </li>
            ))}
          </ul>
        )}

        {aba === "ataques" && (
          <ul className="lista-simples">
            {v.ataques.map((a, i) => (
              <li key={i}>
                <strong>{a.ataque >= 0 ? "+" : ""}{a.ataque}</strong>
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
    </aside>
  );
}
