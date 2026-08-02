/**
 * O avatar do personagem -- spec `2026-08-01-avatar-do-personagem.md` (passo 3).
 *
 * A tela e um painel de CASAS, uma por slot (decisao 5c): a casa mostra o que
 * esta equipado e clicar abre o picker daquele slot. A exclusividade fica
 * visivel -- uma casa, uma peca -- e os 41 slots de peca unica viram
 * liga/desliga em vez de grade.
 *
 * Composicao, ordem e recolor vem do pacote `waybuilder-avatar`. Aqui so mora
 * o que precisa de DOM: carregar imagem, desenhar no canvas e a interacao.
 */
import {
  CacheDeRecolor,
  montarCamadas,
  recolorirPixels,
  type CamadaDesenhavel,
  type Catalogo,
  type Item,
  type Escolha,
  type Selecao,
} from "waybuilder-avatar";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const RAIZ = "/avatar/";
const Q = 64;

/** Ordem das secoes no painel. As demais entram depois, em ordem alfabetica. */
const ORDEM_DOS_GRUPOS = [
  "Corpo", "Cabeca", "Rosto", "Cabelo", "Chapeu", "Torso",
  "Pernas e pes", "Armadura", "Acessorios", "Armas", "Marcas",
];

// -- carregamento -------------------------------------------------------------

const imagens = new Map<string, Promise<HTMLImageElement>>();

function carregarImagem(arq: string): Promise<HTMLImageElement> {
  const guardada = imagens.get(arq);
  if (guardada) return guardada;
  const p = new Promise<HTMLImageElement>((ok, falha) => {
    const im = new Image();
    im.onload = () => ok(im);
    im.onerror = () => falha(new Error(arq));
    im.src = RAIZ + arq;
  });
  imagens.set(arq, p);
  return p;
}

const paletas = new Map<string, Promise<Record<string, string[]>>>();
const metas = new Map<string, Promise<{ base: string; default: string }>>();

function lerJson<T>(rel: string, cache: Map<string, Promise<T>>): Promise<T> {
  const guardado = cache.get(rel);
  if (guardado) return guardado;
  const p = fetch(RAIZ + rel).then((r) => r.json() as Promise<T>);
  cache.set(rel, p);
  return p;
}

/**
 * O bitmap de uma camada, ja recolorido se preciso.
 *
 * O cache e por (arquivo, paleta, cor): a grade compoe o personagem inteiro em
 * cada celula, e o maior slot tem 89 pecas -- sem ele, seria uma varredura de
 * pixels por celula a cada navegacao.
 */
const cacheRecolor = new CacheDeRecolor<Promise<CanvasImageSource>>();

async function bitmapDa(camada: CamadaDesenhavel): Promise<CanvasImageSource> {
  const imagem = await carregarImagem(camada.arq);
  if (!camada.recolor?.length) return imagem;

  const pedido = camada.recolor[0]!;
  return cacheRecolor.obter(camada.arq, pedido.paleta, pedido.cor, async () => {
    const cv = document.createElement("canvas");
    cv.width = imagem.width;
    cv.height = imagem.height;
    const ctx = cv.getContext("2d", { willReadFrequently: true })!;
    ctx.drawImage(imagem, 0, 0);
    const dados = ctx.getImageData(0, 0, cv.width, cv.height);

    for (const r of camada.recolor!) {
      const meta = await lerJson<{ base: string; default: string }>(
        `paletas/${r.material}/meta_${r.material}.json`, metas);
      const paleta = await lerJson<Record<string, string[]>>(
        `paletas/${r.material}/${r.material}_${r.paleta}.json`, paletas);
      const de = paleta[meta.base];
      const para = paleta[r.cor];
      if (de && para) recolorirPixels(dados.data, de, para);
    }
    ctx.putImageData(dados, 0, 0);
    return cv;
  });
}

// -- o boneco -----------------------------------------------------------------

function Boneco({
  catalogo, selecao, corpo, zoom = 3, titulo,
}: {
  catalogo: Catalogo; selecao: Selecao; corpo: string; zoom?: number;
  titulo?: string;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const { camadas } = useMemo(
    () => montarCamadas(catalogo, selecao, corpo, "idle"),
    [catalogo, selecao, corpo],
  );

  useEffect(() => {
    let vivo = true;
    const cv = canvas.current;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;

    (async () => {
      const prontos = await Promise.all(
        camadas.map(async (c) => {
          try { return [c, await bitmapDa(c)] as const; } catch { return null; }
        }),
      );
      if (!vivo) return;
      ctx.clearRect(0, 0, cv.width, cv.height);
      ctx.imageSmoothingEnabled = false; // pixel art nao interpola
      for (const par of prontos) {
        if (!par) continue;
        const [c, bmp] = par;
        ctx.drawImage(bmp, c.x, c.y, Q, Q, 0, 0, Q * zoom, Q * zoom);
      }
    })();

    return () => { vivo = false; };
  }, [camadas, zoom]);

  return (
    <canvas
      ref={canvas}
      width={Q * zoom}
      height={Q * zoom}
      className="avatar-boneco"
      role="img"
      aria-label={titulo ?? "avatar do personagem"}
    />
  );
}

// -- picker de um slot: uma peca por vez, com setas -------------------------

/**
 * Uma peca por vez, no proprio boneco, com setas para andar pela lista --
 * o esquema do Stardew (decisao 5b, reescrita em @8).
 *
 * A grade de todas as pecas montava o personagem inteiro em cada celula: 89
 * composicoes de uma vez so para abrir `hair`. Aqui abre UMA, e cada seta
 * compoe mais uma.
 */
function Picker({
  catalogo, slot, itens, selecao, corpo, aoEscolher, aoFechar,
}: {
  catalogo: Catalogo; slot: string; itens: Item[]; selecao: Selecao;
  corpo: string; aoEscolher: (e: Escolha | null) => void; aoFechar: () => void;
}) {
  const equipado = selecao[slot];
  const partida = Math.max(0, itens.findIndex((i) => i.id === equipado?.id));
  const [n, setN] = useState(partida);
  const [cores, setCores] = useState<Record<string, string>>(equipado?.cores ?? {});

  const item = itens[n];
  const andar = useCallback((passo: number) => {
    setN((v) => (v + passo + itens.length) % itens.length);
    setCores({});
  }, [itens.length]);

  // as rampas de cada canal da peca atual
  const [rampas, setRampas] = useState<Record<string, [string, string][]>>({});
  useEffect(() => {
    if (!item?.canais_de_cor?.length) { setRampas({}); return; }
    let vivo = true;
    Promise.all(item.canais_de_cor.map(async (c) => {
      // TODAS as paletas que o canal declara, nao so a primeira: um cabelo
      // declara ulpc + lpcr + all.lpcr, e cada uma traz rampas proprias.
      // Usar so a primeira mostrava uma fracao das cores disponiveis.
      // `all.lpcr` quer dizer MATERIAL `all`, paleta `lpcr` -- o ponto separa
      // os dois. Tratar como nome unico procurava `hair/hair_all_lpcr.json`,
      // que nao existe, e engolia as 75 rampas da paleta universal: um cabelo
      // oferece 26 (ulpc) + 20 (lpcr) + 75 (all.lpcr) = 121 cores.
      const listas = await Promise.all(
        c.paletas.map((nome) => {
          const [mat, pal] = nome.includes(".")
            ? (nome.split(".") as [string, string])
            : [c.material, nome];
          return lerJson<Record<string, string[]>>(
            `paletas/${mat}/${mat}_${pal}.json`, paletas,
          ).catch(() => ({}) as Record<string, string[]>);
        }),
      );
      // TODAS as rampas, qualificadas por paleta: 18 dos 19 nomes repetidos
      // sao cores DIFERENTES (ha tres `white` e tres `orange`). Deduplicar por
      // nome descartava cor real; a identidade e o par paleta+nome.
      const todas: [string, string][] = [];
      const vistas = new Set<string>();
      listas.forEach((r, i) => {
        const qual = c.paletas[i] ?? "";
        for (const [k, v] of Object.entries(r)) {
          const meio = v[Math.floor(v.length / 2)] ?? "#000";
          if (vistas.has(`${qual}:${k}`)) continue;
          vistas.add(`${qual}:${k}`);
          todas.push([`${qual}:${k}`, meio]);
        }
      });
      return [c.nome, todas] as const;
    })).then((pares) => { if (vivo) setRampas(Object.fromEntries(pares)); });
    return () => { vivo = false; };
  }, [item]);

  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") andar(-1);
      else if (e.key === "ArrowRight") andar(1);
      else if (e.key === "Escape") aoFechar();
    };
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [andar, aoFechar]);

  if (!item) return null;
  // As cores de uma peca vem de dois lugares, e ate @8 o picker so via um:
  //   - `canais_de_cor` (415 pecas): recolor por paleta, em runtime
  //   - faixas do atlas (241 pecas com `variants`): a cor E o arquivo
  // Peca com `variants` e sem `recolors` nao mostrava seletor nenhum, apesar
  // de ter as cores gravadas -- o Tricorne tem 24 e aparecia sem escolha.
  const faixas = Object.keys(
    item.camadas[0]?.corpos[corpo]?.cores ?? {},
  ).filter((c) => c !== "base");

  // A peca ja aparece colorida: cada canal cai na primeira rampa ate o jogador
  // escolher outra. Sem isso ela abriria na cor crua da arte.
  const padrao: Record<string, string> = {};
  for (const c of item.canais_de_cor ?? []) {
    const primeira = rampas[c.nome]?.[0]?.[0];
    if (primeira) padrao[c.nome] = primeira;
  }
  if (faixas.length > 0 && padrao["cor"] === undefined) padrao["cor"] = faixas[0]!;
  const efetivas = { ...padrao, ...cores };
  const previa: Selecao = { ...selecao, [slot]: { id: item.id, cores: efetivas } };
  const falta = item.sem_arte?.includes(corpo);

  return (
    <div className="modal-fundo" onClick={aoFechar}>
      <div className="modal avatar-picker" onClick={(e) => e.stopPropagation()}>
        <header>
          <span className="avatar-picker-slot">{slot}</span>
          <span className="avatar-picker-conta">{n + 1} / {itens.length}</span>
          <button onClick={aoFechar} aria-label="fechar">x</button>
        </header>

        <div className="avatar-picker-palco">
          <button className="avatar-seta" onClick={() => andar(-1)}
                  aria-label="peca anterior">‹</button>
          <div className="avatar-picker-peca">
            <Boneco catalogo={catalogo} selecao={previa} corpo={corpo} zoom={3}
                    titulo={item.nome} />
            <strong>{item.nome}</strong>
            {falta && <span className="avatar-sem-arte">sem arte neste corpo</span>}
          </div>
          <button className="avatar-seta" onClick={() => andar(1)}
                  aria-label="proxima peca">›</button>
        </div>

        {faixas.length > 0 && (
          <div className="avatar-canal">
            <span className="avatar-canal-nome">cor</span>
            <div className="avatar-tons avatar-tons-nome">
              {faixas.map((nome) => (
                <button
                  key={nome} className={efetivas["cor"] === nome ? "sel" : ""}
                  onClick={() => setCores((c) => ({ ...c, cor: nome }))}
                  aria-pressed={efetivas["cor"] === nome}
                >{nome}</button>
              ))}
            </div>
          </div>
        )}

        {(item.canais_de_cor ?? []).map((canal) => (
          <div key={canal.nome} className="avatar-canal">
            <span className="avatar-canal-nome">{canal.rotulo ?? canal.nome}</span>
            <div className="avatar-tons">
              {(rampas[canal.nome] ?? []).map(([nome, amostra]) => (
                <button
                  key={nome} className={efetivas[canal.nome] === nome ? "sel" : ""}
                  onClick={() => setCores((c) => ({ ...c, [canal.nome]: nome }))}
                  title={nome.replace(":", " · ")}
                  aria-label={`${canal.nome} ${nome.replace(":", " ")}`}
                  aria-pressed={efetivas[canal.nome] === nome}
                >
                  <span className="avatar-tom" style={{ background: amostra }}
                        aria-hidden="true" />
                </button>
              ))}
            </div>
          </div>
        ))}

        <footer>
          <button onClick={() => { aoEscolher(null); aoFechar(); }}>
            deixar vazio
          </button>
          <button className="primario"
                  onClick={() => { aoEscolher({ id: item.id, cores: efetivas }); aoFechar(); }}>
            equipar
          </button>
        </footer>
      </div>
    </div>
  );
}

// -- o painel -----------------------------------------------------------------

export function Avatar({ corpoInicial = "male" }: { corpoInicial?: string }) {
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [selecao, setSelecao] = useState<Selecao>({});
  const [semeado, setSemeado] = useState(false);
  const [corpo, setCorpo] = useState(corpoInicial);
  const [aberto, setAberto] = useState<string | null>(null);
  const [tons, setTons] = useState<[string, string][]>([]);

  // as rampas da paleta de pele; o `meta` traz a padrao e a rampa da arte
  useEffect(() => {
    Promise.all([
      fetch(`${RAIZ}paletas/body/meta_body.json`).then((r) => r.json()),
      fetch(`${RAIZ}paletas/body/body_ulpc.json`).then((r) => r.json()),
    ])
      .then(([, rampas]: [unknown, Record<string, string[]>]) =>
        // a amostra e a cor do meio da rampa: as pontas sao contorno e brilho
        setTons(Object.entries(rampas).map(([n, r]) => [n, r[Math.floor(r.length / 2)] ?? "#000"])))
      .catch(() => setTons([]));
  }, []);

  const peleAtual = selecao["body"]?.cores?.["cor"] ?? "light";
  const trocarPele = useCallback((tom: string) => {
    setSelecao((s) => {
      const body = s["body"];
      if (!body) return s;
      return { ...s, body: { ...body, cores: { ...body.cores, cor: tom } } };
    });
  }, []);

  useEffect(() => {
    fetch(`${RAIZ}catalogo.json`)
      .then((r) => r.json())
      .then(setCatalogo)
      .catch(() => setErro("nao carregou o acervo do avatar"));
  }, []);

  // A semente e a MESMA do gerador oficial do LPC (`selectDefaults()`, em
  // `sources/state/state.ts:159`): corpo + cabeca humana + expressao neutra,
  // os tres na cor `light`. Sem cabeca o boneco abre decapitado -- no LPC o
  // corpo nao inclui a cabeca, ela e slot proprio.
  //
  // A expressao neutra ainda nao entra: as 12 faces do acervo tem `${head}` no
  // caminho e o build ainda nao interpola.
  useEffect(() => {
    if (!catalogo || semeado) return;
    const semente: Selecao = {};
    const por = (id: string) => catalogo.itens.find((i) => i.id === id);
    if (por("body/body-color")) semente["body"] = { id: "body/body-color", cores: { cor: "light" } };
    if (por("head/human-male")) semente["head"] = { id: "head/human-male", cores: { color_1: "light" } };
    setSelecao((s) => ({ ...semente, ...s }));
    setSemeado(true);
  }, [catalogo, semeado]);

  const porSlot = useMemo(() => {
    const m = new Map<string, Item[]>();
    for (const i of catalogo?.itens ?? []) {
      const lista = m.get(i.slot) ?? [];
      lista.push(i);
      m.set(i.slot, lista);
    }
    return m;
  }, [catalogo]);

  const grupos = useMemo(() => {
    const m = new Map<string, string[]>();
    for (const [slot, itens] of porSlot) {
      const g = itens[0]!.grupo;
      const lista = m.get(g) ?? [];
      lista.push(slot);
      m.set(g, lista);
    }
    for (const lista of m.values()) lista.sort();
    return [...m].sort(
      (a, b) =>
        (ORDEM_DOS_GRUPOS.indexOf(a[0]) + 1 || 99) -
        (ORDEM_DOS_GRUPOS.indexOf(b[0]) + 1 || 99) || a[0].localeCompare(b[0]),
    );
  }, [porSlot]);

  const escolher = useCallback((slot: string, e: Escolha | null) => {
    setSelecao((s) => {
      const novo = { ...s };
      if (e === null) delete novo[slot];
      else novo[slot] = e;
      return novo;
    });
  }, []);

  if (erro) return <div className="avatar-erro">{erro}</div>;
  if (!catalogo) return <div className="avatar-carregando">carregando o acervo...</div>;

  return (
    <div className="avatar">
      <aside className="avatar-palco">
        <Boneco catalogo={catalogo} selecao={selecao} corpo={corpo} zoom={4} />
        {tons.length > 0 && (
          <div className="avatar-tons" role="group" aria-label="tom de pele">
            {tons.map(([nome, amostra]) => (
              <button
                key={nome} className={nome === peleAtual ? "sel" : ""}
                onClick={() => trocarPele(nome)} title={nome}
                aria-label={`tom de pele ${nome}`} aria-pressed={nome === peleAtual}
              >
                <span className="avatar-tom" style={{ background: amostra }}
                      aria-hidden="true" />
              </button>
            ))}
          </div>
        )}
        <div className="avatar-corpos" role="group" aria-label="tipo de corpo">
          {catalogo.recorte.corpos.map((c) => (
            <button key={c} className={c === corpo ? "sel" : ""}
                    onClick={() => setCorpo(c)}>{c}</button>
          ))}
        </div>
      </aside>

      <div className="avatar-casas">
        {grupos.map(([grupo, slots]) => (
          <section key={grupo}>
            <h3>{grupo}</h3>
            <div className="avatar-grupo">
              {slots.map((slot) => {
                const equipado = selecao[slot];
                const item = equipado
                  ? porSlot.get(slot)!.find((i) => i.id === equipado.id)
                  : undefined;
                return (
                  <button
                    key={slot} className={`avatar-casa ${item ? "cheia" : "vazia"}`}
                    onClick={() => setAberto(slot)}
                    title={`${slot}${item ? `: ${item.nome}` : " (vazio)"}`}
                  >
                    {item
                      ? <Boneco catalogo={catalogo} selecao={{ [slot]: equipado! }}
                                corpo={corpo} zoom={1} titulo={item.nome} />
                      : <span className="avatar-casa-vazia" aria-hidden="true" />}
                    <span className="avatar-casa-nome">{slot}</span>
                  </button>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      {aberto && (
        <Picker
          catalogo={catalogo} slot={aberto} itens={porSlot.get(aberto) ?? []}
          selecao={selecao} corpo={corpo}
          aoEscolher={(e) => escolher(aberto, e)}
          aoFechar={() => setAberto(null)}
        />
      )}
    </div>
  );
}
