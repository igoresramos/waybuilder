/**
 * A linha de escolha do build, e o modal que ela abre.
 *
 * Formato copiado do Pathbuilder, que o Igor usa: icone a esquerda, rotulo
 * cinza pequeno em cima, valor embaixo, e vazio como **"Nao escolhido" em
 * vermelho** -- e o que faz um build de 20 niveis ser legivel de relance,
 * porque o olho acha o buraco sem ler nada.
 *
 * O modal tem tres partes, e a do meio e a que faltava na primeira versao:
 *   abas de categoria  ->  lista  ->  TEXTO COMPLETO do item selecionado
 * Ninguem escolhe um feat pelo nome. O jogador le o que ele faz, os traits, o
 * requisito e a fonte, e so entao aceita. A prosa vem sob demanda de
 * `base/text/`, que por isso nunca viaja na carga inicial.
 *
 * PRINCIPIO ZERO: o que nao atende o requisito aparece na MESMA lista, em
 * cinza, depois dos que atendem -- e continua selecionavel. Nao ha "mostrar
 * mais": esconder o feat de nivel 6 impede justamente o planejamento, que e
 * metade do que se faz num construtor. O slot filtra por TIPO; o requisito so
 * ordena e explica.
 */
import { useEffect, useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Candidato } from "../motor/tipos";
import { prosa } from "../carregarBase";
import { iconeDeSlot } from "./Icones";
import { Traits } from "./Traits";
import { ListaVirtual } from "./ListaVirtual";
import { limparMarcacao } from "../marcacao";
import { Prosa } from "./Prosa";
import { Funil, FUNIL_VAZIO, aplicarFunil, type EstadoDoFunil } from "./Funil";

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
  /** tipo do slot -- so decide qual icone aparece na linha */
  tipo?: string;
}

/**
 * As abas do topo do modal -- as mesmas quatro do Pathbuilder, e pela mesma
 * razao: quem abre um slot de feat de classe quer ver os feats da classe, mas
 * quem esta pensando em multiclasse quer ver as dedicacoes, e sao listas de
 * tamanho muito diferente (125 contra 226 contra 1.902) para conviverem numa so.
 *
 * `De classe` cai fora quando o slot ja e de outra natureza (pericia, geral):
 * ali nao existe "o feat da minha classe", e a aba sairia sempre vazia.
 */
const temTrait = (r: Record<string, unknown>, t: string) =>
  ((r.traits as string[]) ?? []).includes(t);

export const FILTROS_DE_FEAT: Filtro[] = [
  {
    id: "classe", rotulo: "De classe",
    casa: (r) => !temTrait(r, "archetype"),
  },
  {
    id: "dedicacao", rotulo: "Dedicacoes",
    casa: (r) => temTrait(r, "dedication"),
  },
  {
    id: "arquetipo", rotulo: "De arquetipo",
    casa: (r) => temTrait(r, "archetype") && !temTrait(r, "dedication"),
  },
  { id: "todos", rotulo: "Todos", casa: () => true },
];

export const FILTROS_DE_RARIDADE: Filtro[] = [
  { id: "todos", rotulo: "Todas", casa: () => true },
  { id: "common", rotulo: "Comum", casa: (r) => (r.rarity ?? "common") === "common" },
  { id: "uncommon", rotulo: "Incomum", casa: (r) => r.rarity === "uncommon" },
  { id: "rare", rotulo: "Raro+", casa: (r) => r.rarity === "rare" || r.rarity === "unique" },
];

export function Slot({
  rotulo, candidatos, base, escolhido, aoEscolher, aoLimpar, filtros, tipo,
}: Props) {
  const [aberto, setAberto] = useState(false);
  const nome = escolhido
    ? candidatos.find((c) => c.id === escolhido)?.nome
      ?? base.opcional(escolhido)?.name ?? escolhido
    : null;

  return (
    <div className="slot">
      <button className="slot-linha" onClick={() => setAberto(true)}>
        <span className="slot-icone">{iconeDeSlot(tipo ?? rotulo.toLowerCase())}</span>
        <span className="slot-texto">
          <span className="slot-rotulo">{rotulo}</span>
          <span className={`slot-valor ${nome ? "" : "vazio"}`}>
            {nome ?? "Nao escolhido"}
          </span>
        </span>
      </button>
      {escolhido && aoLimpar && (
        <button className="slot-x" onClick={aoLimpar}
                title={`limpar ${rotulo}`} aria-label={`limpar ${rotulo}`}>x</button>
      )}
      {aberto && (
        <Modal
          titulo={rotulo}
          candidatos={candidatos}
          base={base}
          filtros={filtros}
          escolhido={escolhido ?? null}
          aoFechar={() => setAberto(false)}
          aoLimpar={aoLimpar}
          aoAceitar={(id) => { aoEscolher(id); setAberto(false); }}
        />
      )}
    </div>
  );
}

function Modal({
  titulo, candidatos, base, filtros, escolhido, aoFechar, aoAceitar, aoLimpar,
}: {
  titulo: string;
  candidatos: Candidato[];
  base: Base;
  filtros?: Filtro[];
  escolhido: string | null;
  aoFechar: () => void;
  aoAceitar: (id: string) => void;
  aoLimpar?: () => void;
}) {
  const [busca, setBusca] = useState("");
  const [filtro, setFiltro] = useState(filtros?.[0]?.id ?? "todos");
  const [sel, setSel] = useState<string | null>(escolhido);
  const [texto, setTexto] = useState<string | null>(null);
  const [funil, setFunil] = useState<EstadoDoFunil>(FUNIL_VAZIO);

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

  /** Uma lista so: os que atendem primeiro, os que nao atendem em seguida. */
  const lista = useMemo(() => {
    const q = busca.trim().toLowerCase();
    const f = filtros?.find((x) => x.id === filtro);
    const casa = candidatos.filter((c) => {
      if (q && !(c.nome ?? "").toLowerCase().includes(q) && !c.id.includes(q)) {
        return false;
      }
      if (!f) return true;
      const reg = base.opcional(c.id);
      return reg ? f.casa(reg as Record<string, unknown>) : true;
    });
    const filtrada = aplicarFunil(casa, funil, base);
    return [...filtrada.filter((c) => c.atende), ...filtrada.filter((c) => !c.atende)];
  }, [candidatos, busca, filtro, filtros, base, funil]);

  const reg = sel ? base.opcional(sel) : null;
  const marcado = candidatos.find((c) => c.id === sel);

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
          <Funil candidatos={candidatos} base={base}
                 estado={funil} aoMudar={setFunil} />
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
          <ListaVirtual
            className="modal-lista" itens={lista} altura={640}
            vazio={<li className="vazio">nada passa nos filtros de agora</li>}
          >
            {(c) => (
              <li key={c.id} className={sel === c.id ? "sel" : ""}>
                <button onClick={() => setSel(c.id)}
                        className={c.atende ? "" : "marcado"}
                        aria-pressed={sel === c.id}>
                  <span className="nome">{c.nome ?? c.id}</span>
                  {c.ja_pego && <span className="ja">tem</span>}
                  {c.level != null && <span className="nv">{c.level}</span>}
                </button>
              </li>
            )}
          </ListaVirtual>

          <div className="modal-detalhe">
            {!reg && <p className="vazio">selecione para ler</p>}
            {reg && (
              <>
                <div className="cabeca">
                  <h4>{reg.name}</h4>
                  {reg.level != null && <span className="nv">{reg.level}</span>}
                </div>
                <Traits base={base} reg={reg} />
                {/* O PRE-REQUISITO em prosa, como o Pathbuilder imprime:
                    "Prerequisites trained in Diplomacy". Vem da base em
                    `requires_texto`; quando falta, o gate ainda existe em
                    `requires` (o trait de ancestralidade de Natural Ambition,
                    por exemplo) e aparece no aviso logo abaixo. */}
                {typeof reg.requires_texto === "string" && (
                  <p className="prereq">
                    <b>Pre-requisitos</b> {limparMarcacao(reg.requires_texto)}
                  </p>
                )}
                {marcado && !marcado.atende && (
                  <p className="fora-aviso">
                    fora do requisito: {marcado.motivos.join("; ")}
                    <br />
                    <em>o requisito sugere e ordena -- da para escolher assim mesmo</em>
                  </p>
                )}
                {texto
                  ? <Prosa texto={texto} nome={reg.name} />
                  : <p className="vazio">sem texto para este registro</p>}
              </>
            )}
          </div>
        </div>

        <footer>
          <button className="aceitar" disabled={!sel}
                  onClick={() => sel && aoAceitar(sel)}>
            Aceitar
          </button>
          <button onClick={aoFechar}>Cancelar</button>
          {aoLimpar && escolhido && (
            <button onClick={() => { aoLimpar(); aoFechar(); }}>Limpar</button>
          )}
        </footer>
      </div>
    </div>
  );
}
