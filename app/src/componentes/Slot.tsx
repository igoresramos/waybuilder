/**
 * A linha de escolha do build, e o modal que ela abre.
 *
 * Formato copiado do Pathbuilder, que o Igor usa: rotulo cinza pequeno em
 * cima, valor embaixo, e vazio como **"Nao escolhido" em vermelho** -- e o que
 * faz um build de 20 niveis ser legivel de relance, porque o olho acha o
 * buraco sem ler nada.
 *
 * O modal tem tres partes, e a do meio e a que faltava na primeira versao:
 *   filtros por categoria  ->  lista  ->  TEXTO COMPLETO do item selecionado
 * Ninguem escolhe um feat pelo nome. O jogador le o que ele faz, os traits, o
 * requisito e a fonte, e so entao aceita. A prosa vem sob demanda de
 * `base/text/`, que por isso nunca viaja na carga inicial.
 *
 * PRINCIPIO ZERO: o que nao atende o requisito aparece na lista, marcado, com
 * o motivo -- e continua selecionavel. O slot filtra por TIPO; o requisito so
 * ordena e explica.
 */
import { useEffect, useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Candidato } from "../motor/tipos";
import { prosa } from "../carregarBase";

export interface Filtro {
  id: string;
  rotulo: string;
  casa: (r: Record<string, unknown>) => boolean;
}

interface Props {
  rotulo: string;
  candidatos: Candidato[];
  base: Base;
  escolhido?: string | null;
  aoEscolher: (id: string) => void;
  aoLimpar?: () => void;
  filtros?: Filtro[];
}

/** Os filtros do topo do modal, por tipo de slot -- como no Pathbuilder. */
export const FILTROS_DE_FEAT: Filtro[] = [
  { id: "todos", rotulo: "Todos", casa: () => true },
  {
    id: "dedicacao", rotulo: "Dedicacoes",
    casa: (r) => ((r.traits as string[]) ?? []).includes("dedication"),
  },
  {
    id: "arquetipo", rotulo: "De arquetipo",
    casa: (r) => ((r.traits as string[]) ?? []).includes("archetype")
      && !((r.traits as string[]) ?? []).includes("dedication"),
  },
];

export const FILTROS_DE_RARIDADE: Filtro[] = [
  { id: "todos", rotulo: "Todas", casa: () => true },
  { id: "common", rotulo: "Comum", casa: (r) => (r.rarity ?? "common") === "common" },
  { id: "uncommon", rotulo: "Incomum", casa: (r) => r.rarity === "uncommon" },
  { id: "rare", rotulo: "Raro+", casa: (r) => r.rarity === "rare" || r.rarity === "unique" },
];

export function Slot({
  rotulo, candidatos, base, escolhido, aoEscolher, aoLimpar, filtros,
}: Props) {
  const [aberto, setAberto] = useState(false);
  const nome = escolhido
    ? candidatos.find((c) => c.id === escolhido)?.nome
      ?? base.opcional(escolhido)?.name ?? escolhido
    : null;

  return (
    <div className="slot">
      <button className="slot-linha" onClick={() => setAberto(true)}>
        <span className="slot-rotulo">{rotulo}</span>
        <span className={`slot-valor ${nome ? "" : "vazio"}`}>
          {nome ?? "Nao escolhido"}
        </span>
      </button>
      {escolhido && aoLimpar && (
        <button className="slot-x" onClick={aoLimpar} title="limpar">x</button>
      )}
      {aberto && (
        <Modal
          titulo={rotulo}
          candidatos={candidatos}
          base={base}
          filtros={filtros}
          escolhido={escolhido ?? null}
          aoFechar={() => setAberto(false)}
          aoAceitar={(id) => { aoEscolher(id); setAberto(false); }}
        />
      )}
    </div>
  );
}

function Modal({
  titulo, candidatos, base, filtros, escolhido, aoFechar, aoAceitar,
}: {
  titulo: string;
  candidatos: Candidato[];
  base: Base;
  filtros?: Filtro[];
  escolhido: string | null;
  aoFechar: () => void;
  aoAceitar: (id: string) => void;
}) {
  const [busca, setBusca] = useState("");
  const [filtro, setFiltro] = useState(filtros?.[0]?.id ?? "todos");
  const [sel, setSel] = useState<string | null>(escolhido);
  const [texto, setTexto] = useState<string | null>(null);
  const [verFora, setVerFora] = useState(false);

  // Esc fecha: o modal cobre a tela e sair dele nao pode exigir mira
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === "Escape") aoFechar(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [aoFechar]);

  useEffect(() => {
    setTexto(null);
    if (!sel) return;
    let vivo = true;
    prosa(base.opcional(sel)?.text as string | undefined)
      .then((t) => { if (vivo) setTexto(t); });
    return () => { vivo = false; };
  }, [sel, base]);

  const { atendem, fora } = useMemo(() => {
    const q = busca.trim().toLowerCase();
    const f = filtros?.find((x) => x.id === filtro);
    const lista = candidatos.filter((c) => {
      if (q && !(c.nome ?? "").toLowerCase().includes(q) && !c.id.includes(q)) {
        return false;
      }
      if (!f) return true;
      const reg = base.opcional(c.id);
      return reg ? f.casa(reg as Record<string, unknown>) : true;
    });
    return {
      atendem: lista.filter((c) => c.atende),
      fora: lista.filter((c) => !c.atende),
    };
  }, [candidatos, busca, filtro, filtros, base]);

  const reg = sel ? base.opcional(sel) : null;
  const marcado = candidatos.find((c) => c.id === sel);

  const linha = (c: Candidato, forinha = false) => (
    <li key={c.id} className={sel === c.id ? "sel" : ""}>
      <button onClick={() => setSel(c.id)} className={forinha ? "marcado" : ""}>
        <span className="nome">{c.nome ?? c.id}</span>
        {c.level != null && <span className="nv">{c.level}</span>}
        {c.ja_pego && <span className="ja">tem</span>}
      </button>
    </li>
  );

  return (
    <div className="modal-fundo" onClick={aoFechar}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <header>
          <h3>{titulo}</h3>
          <input
            autoFocus className="busca"
            placeholder={`buscar entre ${candidatos.length}...`}
            value={busca} onChange={(e) => setBusca(e.target.value)}
          />
        </header>

        {filtros && (
          <nav className="filtros">
            {filtros.map((f) => (
              <button key={f.id} className={filtro === f.id ? "sel" : ""}
                      onClick={() => setFiltro(f.id)}>
                {f.rotulo}
              </button>
            ))}
          </nav>
        )}

        <div className="modal-corpo">
          <ul className="modal-lista">
            {atendem.map((c) => linha(c))}
            {!atendem.length && <li className="vazio">nada encontrado</li>}

            {fora.length > 0 && (
              <li className="separador">
                <button className="link" onClick={() => setVerFora(!verFora)}>
                  {verFora ? "esconder" : "mostrar"} {fora.length} fora do requisito
                </button>
              </li>
            )}
            {verFora && fora.map((c) => linha(c, true))}
          </ul>

          <div className="modal-detalhe">
            {!reg && <p className="vazio">selecione para ler</p>}
            {reg && (
              <>
                <h4>{reg.name}</h4>
                <div className="traits">
                  {reg.rarity && reg.rarity !== "common" && (
                    <span className={`trait r-${reg.rarity}`}>{reg.rarity}</span>
                  )}
                  {(reg.traits ?? []).map((t) => (
                    <span key={t} className="trait">{t}</span>
                  ))}
                </div>
                {marcado && !marcado.atende && (
                  <p className="fora-aviso">
                    fora do requisito: {marcado.motivos.join("; ")}
                    <br />
                    <em>o requisito sugere e ordena -- da para escolher assim mesmo</em>
                  </p>
                )}
                <div className="prosa">
                  {texto ?? <span className="vazio">sem texto para este registro</span>}
                </div>
                {reg.source?.book && (
                  <p className="fonte">
                    {reg.source.book}
                    {reg.source.page ? `, pg. ${reg.source.page}` : ""}
                  </p>
                )}
              </>
            )}
          </div>
        </div>

        <footer>
          <button onClick={aoFechar}>Cancelar</button>
          <button className="aceitar" disabled={!sel}
                  onClick={() => sel && aoAceitar(sel)}>
            Aceitar
          </button>
        </footer>
      </div>
    </div>
  );
}
