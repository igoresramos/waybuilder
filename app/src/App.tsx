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
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Base } from "./motor/base";
import { Personagem } from "./motor/personagem";
import type {
  Candidato, Documento, FonteDeBoost, PinDaBase, Registro,
} from "./motor/tipos";
import { carregarNucleo } from "./carregarBase";
import { Avatar } from "./componentes/Avatar";
import { Slot, FILTROS_DE_FEAT, FILTROS_DE_RARIDADE } from "./componentes/Slot";
import { PainelDireito } from "./componentes/PainelDireito";
import { IconeCog } from "./componentes/Icones";
import { Detalhe } from "./componentes/Detalhe";
import { Fichas } from "./componentes/Fichas";
import { Licenca } from "./componentes/Licenca";
import * as doc from "./doc";
import "./estilo.css";

/** o debounce da gravacao. Ate 2026-08-01 gravava a CADA tecla do campo de nome */
const ESPERA_PARA_GRAVAR = 500;

const AVISO_DE_COTA =
  "o armazenamento deste navegador encheu: a ultima edicao NAO foi gravada. "
  + "Ela continua aberta e pode ser exportada; para voltar a gravar, apague "
  + "alguma ficha da lista.";

/** `#/p/<id>` sem empilhar historico -- cada F5 numa aba volta na ficha dela. */
function enderecar(id: string | null): void {
  if (typeof location === "undefined" || typeof history === "undefined") return;
  const alvo = id ? `#/p/${encodeURIComponent(id)}` : "";
  if (location.hash === alvo) return;
  history.replaceState(null, "", alvo || location.pathname + location.search);
}

const TRILHOS = [
  { slot: "class_feat", cadencia: "class", rotulo: "Feat de classe" },
  { slot: "skill_feat", cadencia: "skill", rotulo: "Feat de pericia" },
  { slot: "general_feat", cadencia: "general", rotulo: "Feat geral" },
  { slot: "ancestry_feat", cadencia: "ancestry", rotulo: "Feat de ancestria" },
  { slot: "free_archetype", cadencia: "free_archetype", rotulo: "Free Archetype" },
] as const;

const ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"];

/**
 * Rotulo humano para o `tipo` do slot concedido.
 *
 * O motor entrega o `itemType` cru da fonte (`spell`, `heritage`, `action`);
 * quem le a ficha nao tem por que ver o vocabulario do Foundry.
 */
const NOME_DO_TIPO: Record<string, string> = {
  feat: "Feat", spell: "Magia", heritage: "Heranca", action: "Acao",
  weapon: "Arma", ancestry: "Ancestralidade", deity: "Divindade",
};

/**
 * Rota de dev do avatar -- `#/avatar` (spec, passo 3 da ordem).
 *
 * Fica dentro do proprio app, com o mesmo build e o mesmo versionamento
 * (decisao 10): a promocao a modal e mover um componente. Prototipo de
 * interface em projeto separado e modo de perda conhecido nesta casa.
 */
function RotaDoAvatar() {
  return (
    <main style={{ padding: "var(--u)" }}>
      <h2 style={{ marginTop: 0 }}>Avatar (rota de dev)</h2>
      <Avatar />
    </main>
  );
}

export default function App() {
  if (location.hash.startsWith("#/avatar")) return <RotaDoAvatar />;
  const [base, setBase] = useState<Base | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  // A CARGA DECIDE QUAL FICHA ABRE -- hash, ponteiro, mais recente, ou nova.
  // Ate 2026-08-01 nao existia leitura nenhuma: `App.tsx:54` cunhava um id
  // novo a cada mount e `App.tsx:63-65` so gravava, entao cada recarga nascia
  // uma ficha diferente e a do jogador nunca voltava (issue #1). O id agora vem
  // de dentro do documento carregado, e o teste `persistencia.test.ts` mantem
  // este arquivo sem nenhuma cunhagem de id.
  const [inicial] = useState(() => doc.abrir());
  const [d, setD] = useState<Documento>(inicial.doc);
  const [avisos, setAvisos] = useState<string[]>(inicial.avisos);
  const [fichas, setFichas] = useState<doc.Salvo[]>(() => doc.listar());
  const [seletor, setSeletor] = useState(false);
  const [alvo, setAlvo] = useState(4);
  // o registro que o jogador quer LER (concedido, nao escolhido)
  const [lendo, setLendo] = useState<string | null>(null);
  const arquivo = useRef<HTMLInputElement>(null);

  // o texto do ultimo documento GRAVADO: gravar de novo o identico e escrita a
  // toa numa cota que ja foi vazada uma vez
  const ultimoGravado = useRef<string | null>(null);
  const pendente = useRef<Documento | null>(null);
  const pinDaBase = useRef<PinDaBase | null>(null);
  // o aviso de cota fala UMA vez por sessao: com o debounce falhando a cada
  // 500 ms, repetir viraria ruido que esconde o proprio aviso
  const avisouCota = useRef(false);

  const avisar = useCallback((texto: string) => {
    setAvisos((a) => (a.includes(texto) ? a : [...a, texto]));
  }, []);

  useEffect(() => {
    if (!inicial.nova) enderecar(inicial.doc.id ?? null);
  }, [inicial]);

  useEffect(() => {
    carregarNucleo().then((r) => {
      setBase(r.base);
      pinDaBase.current = r.pin;
      // o aviso de base divergente e de CARGA: dispara uma vez, quando o pin
      // chega, e nao a cada edicao. O aviso de id nao resolvido e outro bicho --
      // ele e derivado da base e reaparece sozinho enquanto o id nao resolver.
      const divergiu = doc.avisoDePin(d, r.pin);
      if (divergiu) avisar(divergiu);
    }).catch((e) => setErro(String(e)));
    // de proposito sem `d`: rodar de novo a cada tecla recarregaria a base
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Grava o que estiver pendente, AGORA.
   *
   * Falha de cota nao descarta a edicao: ela continua em `d`, na tela e no
   * `exportar()`. Perder ficha para caber e o unico desfecho que a spec proibe.
   */
  const gravar = useCallback(() => {
    const alvoDoc = pendente.current;
    if (!alvoDoc) return;
    pendente.current = null;
    const carimbado = pinDaBase.current
      ? doc.carimbarBase(alvoDoc, pinDaBase.current) : alvoDoc;
    const r = doc.salvar(carimbado);
    if (!r.ok) {
      if (!avisouCota.current) {
        avisouCota.current = true;
        avisar(r.detalhe && r.erro === "resgate" ? r.detalhe : AVISO_DE_COTA);
        setSeletor(true); // para o jogador poder apagar o que quiser
      }
      return;
    }
    ultimoGravado.current = JSON.stringify(carimbado);
    if (carimbado.id) {
      doc.marcarAberta(carimbado.id);
      enderecar(carimbado.id);
    }
    setFichas(r.lista);
    // o carimbo faz parte do documento: sem isto o `base` gravado e o da tela
    // divergiriam, e o proximo `exportar()` sairia sem identidade de build
    setD(carimbado);
  }, [avisar]);

  useEffect(() => {
    if (!doc.temConteudo(d)) return; // visita ociosa nao deixa entrada
    const texto = JSON.stringify(d);
    if (texto === ultimoGravado.current) return;
    pendente.current = d;
    const t = setTimeout(gravar, ESPERA_PARA_GRAVAR);
    return () => clearTimeout(t);
  }, [d, gravar]);

  /**
   * O debounce sem flush seria REGRESSAO: o codigo de hoje grava a cada tecla, e
   * fechar a aba dentro dos 500 ms perderia a ultima edicao. `pagehide` cobre
   * fechar e navegar; `visibilitychange` cobre o descarte do iOS, onde
   * `pagehide` pode nao chegar.
   */
  useEffect(() => {
    const flush = () => { if (pendente.current) gravar(); };
    const aoEsconder = () => {
      if (document.visibilityState === "hidden") flush();
    };
    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", aoEsconder);
    return () => {
      window.removeEventListener("pagehide", flush);
      document.removeEventListener("visibilitychange", aoEsconder);
    };
  }, [gravar]);

  /** Troca a ficha aberta -- gravando o pendente ANTES, senao a edicao some. */
  const trocarPara = useCallback((novo: Documento, novosAvisos: string[]) => {
    if (pendente.current) gravar();
    ultimoGravado.current = null;
    pendente.current = null;
    setD(novo);
    const divergiu = pinDaBase.current ? doc.avisoDePin(novo, pinDaBase.current) : null;
    setAvisos(divergiu ? [...novosAvisos, divergiu] : novosAvisos);
    setSeletor(false);
    setFichas(doc.listar());
  }, [gravar]);

  const abrirFicha = useCallback((idAlvo: string) => {
    const a = doc.abrir(`#/p/${encodeURIComponent(idAlvo)}`);
    trocarPara(a.doc, a.avisos);
    enderecar(a.nova ? null : a.doc.id ?? null);
  }, [trocarPara]);

  /**
   * Comecar OUTRA ficha -- o substituto do habito antigo de recarregar a pagina.
   *
   * Nao grava no clique: ela entra na lista na primeira edicao, pela mesma regra
   * que impede a visita ociosa de deixar entrada. Recarregar antes de editar
   * volta na ficha anterior, porque um rascunho intocado nunca chegou ao disco.
   */
  const novaFicha = useCallback(() => {
    doc.esquecerUltima();
    enderecar(null);
    trocarPara(doc.novoDocumento(), []);
  }, [trocarPara]);

  const apagarFicha = useCallback((idAlvo: string) => {
    if (pendente.current) gravar(); // o pendente e de outra ficha; nao pode sumir
    const r = doc.apagar(idAlvo);
    setFichas(r.lista);
    if (!r.ok) {
      avisar(r.detalhe ?? AVISO_DE_COTA);
      return;
    }
    if (idAlvo === d.id) {
      const a = doc.abrir(""); // sem hash: cai no ponteiro / mais recente / nova
      trocarPara(a.doc, a.avisos);
      enderecar(a.nova ? null : a.doc.id ?? null);
    }
  }, [avisar, d.id, gravar, trocarPara]);

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

  /**
   * Os slots que um feat ou heranca CONCEDEU naquele momento da ficha.
   *
   * Ate 2026-07-31 nenhum deles era desenhado: o motor abria o slot desde a
   * spec de 30/07 e a tela nunca o mostrava, entao quem pegava `Ancient Elf`
   * nao era perguntado nada. A identidade e a `flag` da fonte, e nao o nivel --
   * dois concessores podem cair no mesmo.
   * Ver `specs/2026-07-31-slot-concedido-generico.md`.
   */
  const slotsConcedidos = (em: number | "criacao") => {
    if (!p) return [];
    return p.slots_concedidos.filter((b) => b.em === em && b.flag).map((b) => {
      const flag = b.flag as string;
      const tipo = b.tipo || "feat";
      return (
        <Slot base={base!} key={`conc-${flag}`}
              rotulo={`${NOME_DO_TIPO[tipo] ?? tipo} de ${b.origem}`}
              tipo={tipo}
              candidatos={p.candidatos("feat_concedido", em, null, flag)}
              filtros={tipo === "feat" ? FILTROS_DE_FEAT : FILTROS_DE_RARIDADE}
              escolhido={doc.concedidoDe(d, flag)}
              aoEscolher={(x) => setD(doc.escolherConcedido(d, em, flag, x))}
              aoLimpar={() => setD(doc.limparConcedido(d, flag))} />
      );
    });
  };

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
          <button onClick={() => setSeletor(true)}>fichas ({fichas.length})</button>
          <button onClick={() => doc.exportar(d)}>exportar</button>
          <button onClick={() => arquivo.current?.click()}>importar</button>
          <input
            ref={arquivo} type="file" accept="application/json" hidden
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              const { doc: lido, erro: falha, aviso } = doc.importar(await f.text());
              if (falha) alert(falha);
              else if (lido) {
                // ficha importada e OUTRA ficha: entra pelo mesmo caminho de
                // troca, gravando o pendente antes de sair da atual
                trocarPara(lido, aviso ? [aviso] : []);
                enderecar(null); // so ganha endereco depois de gravada
              }
              e.target.value = "";
            }}
          />
        </div>
      </header>

      {/* AVISA, NUNCA RECUSA (principio 1): base divergente, esquema do futuro,
          endereco morto e cota estourada aparecem aqui, e a ficha abre inteira
          atras deles. */}
      {avisos.length > 0 && (
        <div className="avisos">
          {avisos.map((a, i) => (
            <p key={i}>
              <span>{a}</span>
              <button onClick={() => setAvisos((x) => x.filter((_, j) => j !== i))}>
                ok
              </button>
            </p>
          ))}
        </div>
      )}

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

            {slotsConcedidos("criacao")}

            <Boosts d={d} setD={setD}
                    declarados={v.boosts.declarados} direito={v.boosts.direito}
                    fontes={(v.boosts.fontes ?? []) as FonteDeBoost[]} />

            {/* PERICIAS TREINADAS -- o motor abria o slot desde 29/07 e a tela
                nunca desenhou, entao nao havia como treinar pericia nenhuma.
                Mesma familia do `feat_concedido` no item 106. */}
            <PericiasLivres base={base} p={p} d={d} setD={setD}
                            quantas={v.pericias_livres ?? 0} />
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

              {/* Cada EIXO e um slot proprio. O Campeao abre `cause` e dois
                  blocos de `outras-opcoes` no nivel 1; com a chave sem o eixo,
                  os tres liam e escreviam a mesma escolha e apareciam com o
                  mesmo valor. Os candidatos tambem sao por eixo -- oferecer as
                  opcoes de `cause` num slot de `outras-opcoes` e oferecer o
                  que nao cabe ali. */}
              {n <= nivel && v.subclasses.filter((b) => b.nivel === n).flatMap((b, i) => {
                const eixo = b.eixo ?? null;
                const doEixo = p.candidatos("subclasse", n)
                  .filter((c) => (b.opcoes_ids ?? []).includes(c.id));
                const rotulo = `${b.classe} / ${b.eixo ?? "sub-escolha"}`;
                // Os 52 blocos de `escolhe: 1` seguem exatamente como eram: uma
                // linha, substituindo ao escolher.
                if ((b.escolhe ?? 1) <= 1) {
                  return [
                    <Slot base={base} key={`sub${i}-${b.eixo ?? ""}`}
                          rotulo={rotulo} tipo="class" candidatos={doEixo}
                          escolhido={doc.subclasseEm(d, n, eixo)}
                          aoEscolher={(x) =>
                            setD(doc.escolherSubclasse(d, n, eixo, x))}
                          aoLimpar={() => setD(doc.limparSubclasse(d, n, eixo))} />,
                  ];
                }
                // `escolhe: N` (os tres ikons do Exemplar): uma linha por
                // escolha ja feita, mais UMA aberta enquanto faltar. Substituir
                // aqui faria a segunda escolha apagar a primeira.
                const feitas = doc.subclassesEm(d, n, eixo);
                const linhas = feitas.map((pego, j) => (
                  <Slot base={base} key={`sub${i}-${b.eixo ?? ""}-${pego}`}
                        rotulo={`${rotulo} ${j + 1}/${b.escolhe}`} tipo="class"
                        candidatos={doEixo}
                        escolhido={pego}
                        aoEscolher={(x) => setD(doc.adicionarSubclasse(
                          doc.removerSubclasse(d, n, eixo, pego), n, eixo, x))}
                        aoLimpar={() =>
                          setD(doc.removerSubclasse(d, n, eixo, pego))} />
                ));
                if (feitas.length < b.escolhe) {
                  linhas.push(
                    <Slot base={base} key={`sub${i}-${b.eixo ?? ""}-aberto`}
                          rotulo={`${rotulo} ${feitas.length + 1}/${b.escolhe}`}
                          tipo="class"
                          candidatos={doEixo.filter((c) => !feitas.includes(c.id))}
                          escolhido={null}
                          aoEscolher={(x) =>
                            setD(doc.adicionarSubclasse(d, n, eixo, x))}
                          aoLimpar={() => setD(d)} />,
                  );
                }
                return linhas;
              })}

              {n <= nivel && slotsConcedidos(n)}

              {/* Companheiro concedido por feat. O slot nasce do `grant_actor`
                  do proprio feat pego neste nivel -- ate 2026-07-29 pegar
                  `Animal Companion` nao abria nada e o bicho so entrava
                  editando o JSON a mao. A escolha vai para `doc.atores`, e nao
                  para `escolhas`: o ator tem nome e escolhas proprias. */}
              {n <= nivel && v.concessoes_de_ator
                .filter((c) => c.em === n)
                .map((c) => (
                  <Slot base={base} key={`ator-${c.origem}-${n}`}
                        rotulo={`${c.tipo} -- ${c.origem_nome}`} tipo="companheiro"
                        candidatos={p.candidatos(c.tipo, n)}
                        escolhido={c.escolhido}
                        aoEscolher={(x) =>
                          setD(doc.escolherAtor(d, c.origem, n, c.tipo, x))}
                        aoLimpar={() => setD(doc.limparAtor(d, c.origem, n))} />
                ))}

              {/* o que este nivel CONCEDEU -- nao e escolha, e consequencia */}
              {n <= nivel && (() => {
                const dadas = v.features.filter((f) => f.nivel_de_classe === n);
                return dadas.length ? (
                  <ul className="concedido-no-nivel">
                    {dadas.map((f, i) => (
                      <li key={i}>
                        {/* concedido tambem se le: o jogador precisa saber o
                            que ganhou, nao so o que escolheu */}
                        <button className="link-concedido"
                                disabled={!f.id}
                                onClick={() => f.id && setLendo(f.id)}>
                          {f.nome}
                        </button>
                      </li>
                    ))}
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

      {lendo && (
        <Detalhe base={base} id={lendo} aoFechar={() => setLendo(null)} />
      )}

      {seletor && (
        <Fichas fichas={fichas} atual={d.id}
                aoAbrir={abrirFicha} aoApagar={apagarFicha} aoNova={novaFicha}
                aoFechar={() => setSeletor(false)} />
      )}

      {/* atribuicao OGL/ORC -- exigida ao REDISTRIBUIR, e publicar e
          redistribuir. Ver componentes/Licenca.tsx */}
      <footer className="rodape"><Licenca /></footer>
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
  d, setD, declarados, direito, fontes,
}: {
  d: Documento; setD: (x: Documento) => void; declarados: number; direito: number;
  fontes: FonteDeBoost[];
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
      {aberto && <BoostPicker d={d} setD={setD} fontes={fontes} />}
    </>
  );
}

/**
 * As pericias treinadas da criacao -- `N + INT` pela classe.
 *
 * Nao existia na tela: `grep -rn pericias_livres app/src/` fora do motor dava
 * ZERO. O motor abria o slot desde 29/07 (`slots_abertos()` emite
 * `pericias treinadas (3 a escolher)`) e ninguem nunca foi perguntado, entao
 * nao havia como treinar pericia nenhuma no app. E `candidatos()` nem sequer
 * conhecia o slot: caia no `else` final e devolvia FEATS.
 *
 * A mesma lacuna aparece na METRICA: dos 723 pontos que ainda divergem contra
 * os iconics da Paizo, 450 sao exatamente este slot.
 * Spec: specs/2026-07-31-slots-de-criacao-na-tela.md
 */
function PericiasLivres({
  base, p, d, setD, quantas,
}: {
  base: Base; p: Personagem; d: Documento; setD: (x: Documento) => void;
  quantas: number;
}) {
  if (!quantas) return null;
  const escolhidas = doc.multiplas(d, "pericias_livres", "criacao");
  const candidatos = p.candidatos("pericias_livres");
  return (
    <>
      {Array.from({ length: quantas }, (_, i) => (
        <Slot base={base} key={i} rotulo="Pericia treinada" tipo="skill_increase"
              // as ja escolhidas saem da lista: treinar a mesma pericia duas
              // vezes gastaria o orcamento sem mudar rank nenhum
              candidatos={candidatos.filter(
                (c) => c.id === escolhidas[i] || !escolhidas.includes(c.id))}
              escolhido={escolhidas[i] ?? null}
              aoEscolher={(x) => setD(doc.definirMultipla(d, "pericias_livres", "criacao", i, x))}
              aoLimpar={() => setD(doc.definirMultipla(d, "pericias_livres", "criacao", i, null))} />
      ))}
    </>
  );
}

/**
 * Boost e o unico slot que aceita VARIAS entradas no mesmo nivel -- e as
 * entradas NAO sao intercambiaveis: cada uma pertence a uma FONTE.
 *
 * A primeira versao mostrava uma fileira unica de seis botoes com toggle, e
 * por isso clicar `STR` duas vezes DESMARCAVA. O efeito pratico, relatado pelo
 * Igor testando: "n tem como colocar +2 em nada".
 *
 * A regra de PF2e que aquela fileira achatava: os boosts de um MESMO bloco vao
 * cada um para um atributo diferente; blocos DIFERENTES podem cair no mesmo
 * atributo -- e assim que um Guerreiro humano chega a STR 18 no nivel 1. Uma
 * fileira so torna a regra inexprimivel: ou proibe tudo, ou permite o ilegal.
 *
 * O motor ja entregava as fontes separadas em `visao.boosts.fontes`; a tela é
 * que descartava o campo.
 *
 * O documento NAO ganha a fonte: ele grava DECISAO, nao derivacao (principio 3
 * do README). A associacao e posicional -- a fonte `i` consome as proximas
 * `quantidade` entradas, na ordem, e o motor soma tudo igual.
 * Spec: specs/2026-07-31-slots-de-criacao-na-tela.md
 */
function BoostPicker({
  d, setD, fontes,
}: { d: Documento; setD: (x: Documento) => void; fontes: FonteDeBoost[] }) {
  // lista PLANA na ordem em que as entradas estao no documento; leva antiga
  // com varios atributos e achatada na leitura, entao ficha salva continua
  // abrindo
  // uma ENTRADA por posicao, e posicao vazia vira `pega: []`. Compactar (so
  // gravar as preenchidas) fazia o mapeamento fonte->escolha DESLIZAR no
  // primeiro buraco: escolher na 4a fonte com as tres primeiras vazias gravava
  // no indice 0, e a regra "nao repete dentro do bloco" passava a olhar o
  // bloco errado. Medido: o motor ignora `pega: []` na soma e nao o conta em
  // `declarados`, entao a posicao vazia e barata.
  const plana = d.escolhas
    .filter((e) => e.slot === "boosts_livres")
    .map((e) => {
      const v = (Array.isArray(e.pega) ? e.pega : [e.pega]) as string[];
      return v[0] ?? "";
    });

  function definir(indiceGlobal: number, attr: string | null) {
    const nova = [...plana];
    while (nova.length <= indiceGlobal) nova.push("");
    nova[indiceGlobal] = attr ?? "";
    while (nova.length && nova[nova.length - 1] === "") nova.pop();  // sem cauda vazia
    const outras = d.escolhas.filter((e) => e.slot !== "boosts_livres");
    for (const a of nova) {
      outras.push({ em: "criacao", slot: "boosts_livres", pega: a ? [a] : [] });
    }
    setD({ ...d, escolhas: doc.ordenarEscolhas(outras) });
  }

  let offset = 0;
  return (
    <div className="boost-picker">
      {fontes.map((f, iFonte) => {
        const inicio = offset;
        offset += f.quantidade;
        const permitidos = (f.opcoes as string[] | null) ?? ATRIBUTOS;
        // dentro da MESMA fonte o atributo nao repete -- regra RAW, e so vale
        // aqui. Entre fontes repetir e o comportamento certo, e e o que da +2.
        const nesta = plana.slice(inicio, inicio + f.quantidade);
        return (
          <div className="boost-fonte" key={`${f.origem}-${iFonte}`}>
            <span className="boost-origem">{f.origem}</span>
            <div className="boost-seletores">
              {Array.from({ length: f.quantidade }, (_, k) => {
                const atual = plana[inicio + k] ?? "";
                return (
                  <div className="boost-linha" key={k}>
                    {permitidos.map((a) => {
                      const usadoNestaFonte = nesta.includes(a) && atual !== a;
                      return (
                        <button key={a}
                          className={atual === a ? "sel" : usadoNestaFonte ? "bloqueado" : ""}
                          disabled={usadoNestaFonte}
                          title={usadoNestaFonte
                            ? "cada boost deste bloco vai para um atributo diferente"
                            : undefined}
                          onClick={() => definir(inicio + k, atual === a ? null : a)}>
                          {a.toUpperCase()}
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
