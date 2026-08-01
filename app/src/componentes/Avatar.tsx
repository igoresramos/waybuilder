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
  type Selecao,
} from "waybuilder-avatar";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ListaVirtual } from "./ListaVirtual";

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

// -- picker de um slot --------------------------------------------------------

function Picker({
  catalogo, slot, itens, selecao, corpo, aoEscolher, aoFechar,
}: {
  catalogo: Catalogo; slot: string; itens: Item[]; selecao: Selecao;
  corpo: string; aoEscolher: (id: string | null) => void; aoFechar: () => void;
}) {
  const [busca, setBusca] = useState("");
  const filtrados = useMemo(() => {
    const q = busca.trim().toLowerCase();
    return q ? itens.filter((i) => i.nome.toLowerCase().includes(q)) : itens;
  }, [itens, busca]);

  return (
    <div className="modal-fundo" onClick={aoFechar}>
      <div className="modal avatar-picker" onClick={(e) => e.stopPropagation()}>
        <header>
          <input
            autoFocus className="busca" value={busca} placeholder={`buscar em ${slot}`}
            onChange={(e) => setBusca(e.target.value)}
            aria-label={`buscar peca de ${slot}`}
          />
          <button onClick={aoFechar} aria-label="fechar">x</button>
        </header>
        <div className="modal-corpo">
          <ListaVirtual
            className="avatar-grade" itens={filtrados} altura={520}
            vazio={<li className="vazio">nada com esse nome</li>}
          >
            {(item: Item) => {
              // (5b) a celula mostra a peca NO personagem, nao isolada
              const previa: Selecao = { ...selecao, [slot]: { id: item.id } };
              const falta = item.sem_arte?.includes(corpo);
              return (
                <li key={item.id}>
                  <button
                    className={selecao[slot]?.id === item.id ? "sel" : ""}
                    onClick={() => { aoEscolher(item.id); aoFechar(); }}
                    title={item.nome}
                  >
                    <Boneco catalogo={catalogo} selecao={previa} corpo={corpo}
                            zoom={1} titulo={item.nome} />
                    <span className="nome">{item.nome}</span>
                    {/* sem isto a celula mostraria o boneco inalterado e o
                        preview mentiria por omissao -- 130 itens no acervo */}
                    {falta && <span className="avatar-sem-arte">sem arte neste corpo</span>}
                  </button>
                </li>
              );
            }}
          </ListaVirtual>
        </div>
        <footer>
          <button onClick={() => { aoEscolher(null); aoFechar(); }}>
            deixar vazio
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
  const [corpo, setCorpo] = useState(corpoInicial);
  const [aberto, setAberto] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${RAIZ}catalogo.json`)
      .then((r) => r.json())
      .then(setCatalogo)
      .catch(() => setErro("nao carregou o acervo do avatar"));
  }, []);

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

  const escolher = useCallback((slot: string, id: string | null) => {
    setSelecao((s) => {
      const novo = { ...s };
      if (id === null) delete novo[slot];
      else novo[slot] = { id };
      return novo;
    });
  }, []);

  if (erro) return <div className="avatar-erro">{erro}</div>;
  if (!catalogo) return <div className="avatar-carregando">carregando o acervo...</div>;

  return (
    <div className="avatar">
      <aside className="avatar-palco">
        <Boneco catalogo={catalogo} selecao={selecao} corpo={corpo} zoom={4} />
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
          aoEscolher={(id) => escolher(aberto, id)}
          aoFechar={() => setAberto(null)}
        />
      )}
    </div>
  );
}
