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
  type CanalDeCor,
  type Catalogo,
  type Item,
  type Escolha,
  type Selecao,
} from "waybuilder-avatar";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const RAIZ = "/avatar/";

/**
 * O rotulo de uma cor.
 *
 * Duas fontes, um so rotulo: `ulpc:orange` (paleta) e `kite_blue_blue`
 * (faixa do atlas). O nome da faixa vem prefixado com o slug da peca -- o
 * escudo Kite mostrava "Kite Blue Blue", repetindo o proprio nome. Limpamos o
 * ROTULO, nunca o dado: o valor gravado na selecao continua sendo a faixa.
 */
function rotuloDaCor(
  chave: string, slug?: string, mapa?: Record<string, string>,
): string {
  const cru = chave.includes(":") ? chave.split(":")[1]! : chave;
  // a traducao e chaveada pelo nome CRU (com prefixo) e ja resolve o corte
  const traduzido = mapa?.[cru];
  if (traduzido) return traduzido;
  let so = cru;
  if (slug) {
    const p = slug.replace(/-/g, "_") + "_";
    if (so.startsWith(p) && so.length > p.length) so = so.slice(p.length);
  }
  return so.replace(/[_-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** O nome que a tela mostra: pt-BR quando existe, original como fallback. */
function nomeDoItem(item: Item): string {
  return item.nome_ptbr || item.nome;
}
const Q = 64;

/**
 * O tom de pele que o boneco abre. Qualificado (`paleta:nome`) porque a
 * identidade da cor e o par: ha tres `white` distintos entre as paletas.
 */
const PELE_PADRAO = "ulpc:light";

/** Os seis corpos do gerador, em pt-BR. */
const ROTULO_DO_CORPO: Record<string, string> = {
  male: "Masculino", female: "Feminino", teen: "Adolescente",
  child: "Criança", muscular: "Musculoso", pregnant: "Gestante",
};

const ROTULO_DA_ANIMACAO: Record<string, string> = {
  idle: "Parado", combat_idle: "Em guarda", walk: "Andando",
  sit: "Sentado", run: "Correndo",
};

/** Ordem das secoes no painel. As demais entram depois, em ordem alfabetica. */
const ORDEM_DOS_GRUPOS = [
  "Corpo", "Cabeça", "Rosto", "Cabelo", "Chapéu", "Torso",
  "Pernas e Pés", "Armadura", "Acessórios", "Armas", "Marcas",
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

function lerJson<T>(rel: string, cache: Map<string, Promise<T>>): Promise<T> {
  const guardado = cache.get(rel);
  if (guardado) return guardado;
  const p = fetch(RAIZ + rel).then((r) => r.json() as Promise<T>);
  cache.set(rel, p);
  return p;
}

/**
 * `all.lpcr` -> `["all", "lpcr"]`; `ulpc` -> `[material do canal, "ulpc"]`.
 *
 * O ponto separa MATERIAL de paleta. Tratar como nome unico procurava
 * `hair/hair_all.lpcr.json`, que nao existe -- e engolia as 75 rampas da
 * paleta universal, onde moram cores como `emerald`.
 */
function quebrarPaleta(token: string, material: string): [string, string] {
  return token.includes(".")
    ? (token.split(".") as [string, string])
    : [material, token];
}

function rampaDaPaleta(token: string, material: string) {
  const [mat, pal] = quebrarPaleta(token, material);
  return lerJson<Record<string, string[]>>(
    `paletas/${mat}/${mat}_${pal}.json`,
    paletas,
  ).catch(() => ({}) as Record<string, string[]>);
}

/**
 * A rampa em que a arte do canal foi pintada.
 *
 * `fonte` vence: quando a peca traz as cores embutidas, nao ha paleta a
 * consultar (`state/palettes.ts:179-182` do gerador). Senao vale o `base`, que
 * o build ja resolve para `<versao>.<rampa>`.
 */
async function rampaDeOrigem(
  canal: { material: string; base?: string; fonte?: string[] },
): Promise<string[] | null> {
  if (canal.fonte?.length) return canal.fonte;
  if (!canal.base?.includes(".")) return null;
  const [ver, nome] = canal.base.split(".") as [string, string];
  const p = await lerJson<Record<string, string[]>>(
    `paletas/${canal.material}/${canal.material}_${ver}.json`,
    paletas,
  ).catch(() => ({}) as Record<string, string[]>);
  return p[nome] ?? null;
}

/**
 * As cores que este canal REALMENTE consegue aplicar, como `[chave, amostra]`.
 *
 * Pedido literal do dono: "as cores que aparecem para selecao devem ser todas
 * reais e possiveis de serem pareadas com o asset". Uma cor so entra quando a
 * rampa de origem existe, a de destino existe, e a de destino cobre a de
 * origem -- recolorir com uma rampa mais curta deixaria parte da arte na cor
 * velha, o que na tela e a peca em duas cores.
 *
 * A chave e `paleta:nome` porque a identidade da cor e o PAR: medido, 18 dos
 * 19 nomes repetidos entre as paletas de um canal sao rampas diferentes -- ha
 * tres `white` e tres `orange`.
 */
async function coresDoCanal(canal: CanalDeCor): Promise<[string, string][]> {
  const origem = await rampaDeOrigem(canal);
  if (!origem?.length) return []; // canal que nao pinta nao oferece cor
  const listas = await Promise.all(
    canal.paletas.map((t) => rampaDaPaleta(t, canal.material)),
  );
  const fora: [string, string][] = [];
  const vistas = new Set<string>();
  listas.forEach((rampas, i) => {
    const token = canal.paletas[i] ?? "";
    for (const [nome, cores] of Object.entries(rampas)) {
      if (!cores?.length || cores.length < origem.length) continue;
      const chave = `${token}:${nome}`;
      if (vistas.has(chave)) continue;
      vistas.add(chave);
      // a amostra e a cor do meio: as pontas sao contorno e brilho
      fora.push([chave, cores[Math.floor(cores.length / 2)] ?? "#000"]);
    }
  });
  return fora;
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

  // A chave cobre TODOS os canais. Com so o primeiro, trocar a cor dos olhos
  // de uma cabeca devolvia o bitmap guardado da cor de pele: a lista mudava e
  // o boneco nao -- medido em `avatar-cor-que-pinta`.
  const chave = camada.recolor.map((r) => `${r.material}|${r.paleta}|${r.cor}`).join("+");
  return cacheRecolor.obter(camada.arq, chave, "", async () => {
    const cv = document.createElement("canvas");
    cv.width = imagem.width;
    cv.height = imagem.height;
    const ctx = cv.getContext("2d", { willReadFrequently: true })!;
    ctx.drawImage(imagem, 0, 0);
    const dados = ctx.getImageData(0, 0, cv.width, cv.height);

    for (const r of camada.recolor!) {
      // ORIGEM e DESTINO sao mundos separados. A origem e a rampa em que a
      // arte foi pintada -- vem do canal, ja resolvida pelo build. O destino
      // pode estar em OUTRO material: `all.lpcr` e a paleta universal, e e la
      // que moram cores como `emerald`. Montar o caminho como
      // `hair/hair_all.lpcr.json` nao acha nada, e era por isso que a cor
      // aparecia na lista e nao pintava no boneco.
      const de = await rampaDeOrigem(r);
      const destino = await rampaDaPaleta(r.paleta, r.material);
      const para = destino[r.cor];
      if (de && para) recolorirPixels(dados.data, de, para);
    }
    ctx.putImageData(dados, 0, 0);
    return cv;
  });
}

// -- o boneco -----------------------------------------------------------------

/** Quem pediu menos movimento nao ve animacao -- so o primeiro frame. */
function movimentoReduzido(): boolean {
  return typeof window !== "undefined"
    && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;
}

function Boneco({
  catalogo, selecao, corpo, zoom = 3, titulo, animacao = "idle", animar = false,
}: {
  catalogo: Catalogo; selecao: Selecao; corpo: string; zoom?: number;
  titulo?: string; animacao?: string; animar?: boolean;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const { camadas } = useMemo(
    () => montarCamadas(catalogo, selecao, corpo, animacao),
    [catalogo, selecao, corpo, animacao],
  );

  // O gerador nao toca os frames em ordem crua: cada animacao tem um CICLO
  // (`state/constants.ts:124-154`). `walk` e [1..8] e pula o frame 0, que e
  // pose parada -- na ordem crua a caminhada soluca a cada volta.
  const ciclo = useMemo(
    () => catalogo.recorte.ciclos?.[animacao] ?? [0],
    [catalogo, animacao],
  );
  const fps = catalogo.recorte.fps ?? 8;

  const prontos = useRef<(readonly [CamadaDesenhavel, CanvasImageSource] | null)[]>([]);
  const [passo, setPasso] = useState(0);

  const desenhar = useCallback((frame: number) => {
    const cv = canvas.current;
    const ctx = cv?.getContext("2d");
    if (!cv || !ctx) return;
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.imageSmoothingEnabled = false; // pixel art nao interpola
    for (const par of prontos.current) {
      if (!par) continue;
      const [c, bmp] = par;
      // frame que a peca nao tem cai no ultimo dela: as tiras tem contagens
      // diferentes e recortar fora da tira desenharia a peca vizinha
      const f = Math.min(frame, Math.max(0, c.frames - 1));
      ctx.drawImage(bmp, c.x + f * Q, c.y, Q, Q, 0, 0, Q * zoom, Q * zoom);
    }
  }, [zoom]);

  useEffect(() => {
    let vivo = true;
    (async () => {
      const carregados = await Promise.all(
        camadas.map(async (c) => {
          try { return [c, await bitmapDa(c)] as const; } catch { return null; }
        }),
      );
      if (!vivo) return;
      prontos.current = carregados;
      desenhar(ciclo[passo % ciclo.length] ?? 0);
    })();
    return () => { vivo = false; };
    // `passo` de proposito fora: o relogio redesenha sozinho, e reagir aqui
    // recarregaria todos os bitmaps a cada frame
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [camadas, desenhar]);

  // O relogio anda so no PALCO. As casas e a celula do picker ficam num frame
  // so -- animar 89 celulas de uma vez e jank garantido.
  useEffect(() => {
    if (!animar || movimentoReduzido() || ciclo.length < 2) return;
    const t = setInterval(() => setPasso((p) => p + 1), 1000 / fps);
    return () => clearInterval(t);
  }, [animar, ciclo.length, fps]);

  useEffect(() => {
    desenhar(ciclo[passo % ciclo.length] ?? 0);
  }, [passo, ciclo, desenhar]);

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
  catalogo, slot, itens, selecao, corpo, animacao, aoEscolher, aoFechar,
}: {
  catalogo: Catalogo; slot: string; itens: Item[]; selecao: Selecao;
  corpo: string; animacao: string;
  aoEscolher: (e: Escolha | null) => void; aoFechar: () => void;
}) {
  const equipado = selecao[slot];
  // Peca que nao existe neste corpo nao entra na lista -- e o que o gerador
  // faz (`components/tree/TreeNode.ts:163`: `required` vem dos corpos
  // declarados no `layer_1`, e o item some da arvore quando o corpo atual nao
  // esta la). A EQUIPADA fica, marcada: sem isso, trocar de corpo faria a peca
  // sumir da lista sem explicacao.
  const disponiveis = useMemo(
    () => itens.filter(
      (i) => !i.sem_arte?.includes(corpo) || i.id === equipado?.id,
    ),
    [itens, corpo, equipado?.id],
  );
  const partida = Math.max(0, disponiveis.findIndex((i) => i.id === equipado?.id));
  const [n, setN] = useState(partida);
  const [cores, setCores] = useState<Record<string, string>>(equipado?.cores ?? {});

  const item = disponiveis[n];
  const andar = useCallback((passo: number) => {
    setN((v) => (v + passo + disponiveis.length) % disponiveis.length);
    setCores({});
  }, [disponiveis.length]);

  // as rampas de cada canal da peca atual
  // Canal que herda o tom de pele NAO e escolha da peca: o gerador forca a cor
  // do corpo nesses itens em render (`state/palettes.ts:119-123`). Oferecer a
  // lista dava 106 botoes que nao mudavam pixel nenhum.
  const canais = useMemo(
    () => (item?.canais_de_cor ?? []).filter(
      (c) => !(item?.segue_cor_do_corpo && c.material === "body"),
    ),
    [item],
  );

  const [rampas, setRampas] = useState<Record<string, [string, string][]>>({});
  useEffect(() => {
    if (!canais.length) { setRampas({}); return; }
    let vivo = true;
    // TODAS as paletas que o canal declara, nao so a primeira -- mas so as
    // cores que o recolor consegue mesmo aplicar (`coresDoCanal`).
    Promise.all(canais.map(async (c) =>
      [c.nome, await coresDoCanal(c)] as const,
    )).then((pares) => { if (vivo) setRampas(Object.fromEntries(pares)); });
    return () => { vivo = false; };
  }, [canais]);

  // trocar de corpo encurta a lista; sem isto o indice apontaria para fora
  useEffect(() => {
    setN((v) => (v < disponiveis.length ? v : 0));
  }, [disponiveis.length]);

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
  // as faixas do escudo Kite vem `kite_blue_blue`: o nome da peca repetido
  const slug = item.id.split("/")[1];

  // A peca ja aparece colorida: cada canal cai na primeira rampa ate o jogador
  // escolher outra. Sem isso ela abriria na cor crua da arte.
  const padrao: Record<string, string> = {};
  for (const c of canais) {
    const primeira = rampas[c.nome]?.[0]?.[0];
    if (primeira) padrao[c.nome] = primeira;
  }
  if (faixas.length > 0 && padrao["cor"] === undefined) padrao["cor"] = faixas[0]!;
  const efetivas = { ...padrao, ...cores };
  const previa: Selecao = { ...selecao, [slot]: { id: item.id, cores: efetivas } };
  const oferecidos = [
    ...(faixas.length > 0 ? ["cor"] : []),
    ...canais.map((c) => c.nome).filter((n) => !(faixas.length > 0 && n === "cor")),
  ];
  const varios = oferecidos.length > 1;
  const rotulados = oferecidos
    .filter((n) => efetivas[n] !== undefined)
    .map((n) => {
      const rot = rotuloDaCor(efetivas[n]!, slug, catalogo.cores);
      const canal = canais.find((c) => c.nome === n);
      return varios ? `${canal?.rotulo ?? n}: ${rot}` : rot;
    });
  const falta = item.sem_arte?.includes(corpo);
  // peca sem a animacao atual nao desenha (`montarCamadas`): sem dizer isso, a
  // celula mostra o boneco inalterado e o preview mente por omissao
  const semEstaAnimacao = !item.camadas.some(
    (c) => c.corpos[corpo]?.animacoes.some((a) => a.nome === animacao),
  );

  return (
    <div className="modal-fundo" onClick={aoFechar}>
      <div className="modal avatar-picker" onClick={(e) => e.stopPropagation()}>
        <header>
          <span className="avatar-picker-slot">
            {catalogo.slots?.[slot] ?? slot}
          </span>
          <span className="avatar-picker-conta">{n + 1} / {disponiveis.length}</span>
          <button onClick={aoFechar} aria-label="fechar">x</button>
        </header>

        <div className="avatar-picker-palco">
          <button className="avatar-seta" onClick={() => andar(-1)}
                  aria-label="peca anterior">‹</button>
          <div className="avatar-picker-peca">
            <Boneco catalogo={catalogo} selecao={previa} corpo={corpo} zoom={3}
                    animacao={animacao} titulo={nomeDoItem(item)} />
            <strong>{nomeDoItem(item)}</strong>
            {/* o jogador precisa saber QUAL cor pegou -- ha tres `white` e
                tres `orange` distintos entre as paletas */}
            {/* so o que a peca REALMENTE oferece: o canal que segue o tom de
                pele nao aparece, senao a etiqueta anuncia uma escolha que o
                jogador nao fez nem pode desfazer aqui */}
            {rotulados.length > 0 && (
              <span className="avatar-etiqueta">
                {rotulados.join("  ·  ")}
              </span>
            )}
            {falta && <span className="avatar-sem-arte">sem arte neste corpo</span>}
            {!falta && semEstaAnimacao && (
              <span className="avatar-sem-arte">
                sem a animação “{ROTULO_DA_ANIMACAO[animacao] ?? animacao}”
              </span>
            )}
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
                >{rotuloDaCor(nome, slug, catalogo.cores)}</button>
              ))}
            </div>
          </div>
        )}

        {canais.map((canal) => (
          <div key={canal.nome} className="avatar-canal">
            <span className="avatar-canal-nome">{canal.rotulo ?? canal.nome}</span>
            <div className="avatar-tons">
              {(rampas[canal.nome] ?? []).map(([nome, amostra]) => (
                <button
                  key={nome} className={efetivas[canal.nome] === nome ? "sel" : ""}
                  onClick={() => setCores((c) => ({ ...c, [canal.nome]: nome }))}
                  title={`${rotuloDaCor(nome, undefined, catalogo.cores)} (${nome.split(":")[0]})`}
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
  const [animacao, setAnimacao] = useState("idle");
  const [tons, setTons] = useState<[string, string][]>([]);

  // O tom de pele sai do CANAL do corpo, nao de um arquivo fixo: `body`
  // declara `ulpc`, `lpcr` e `all.lpcr`, e carregar so `body_ulpc.json` deixava
  // 22 tons na tela quando o acervo oferece muito mais. Mesma validacao do
  // picker -- so entra tom que o recolor consegue aplicar.
  const canalDoCorpo = useMemo(
    () => catalogo?.itens.find((i) => i.id === "body/body-color")
      ?.canais_de_cor?.[0],
    [catalogo],
  );
  useEffect(() => {
    if (!canalDoCorpo) { setTons([]); return; }
    let vivo = true;
    coresDoCanal(canalDoCorpo)
      .then((c) => { if (vivo) setTons(c); })
      .catch(() => { if (vivo) setTons([]); });
    return () => { vivo = false; };
  }, [canalDoCorpo]);

  const peleAtual = selecao["body"]?.cores?.["cor"] ?? PELE_PADRAO;
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
    if (por("body/body-color")) semente["body"] = { id: "body/body-color", cores: { cor: PELE_PADRAO } };
    if (por("head/human-male")) semente["head"] = { id: "head/human-male", cores: { color_1: PELE_PADRAO } };
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

  /** A casa mostrava o slot cru (`facial_eyes`); o rotulo e o que se le. */
  const rotuloDoSlot = useCallback(
    (slot: string) => catalogo?.slots?.[slot] ?? slot,
    [catalogo],
  );

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
        <Boneco catalogo={catalogo} selecao={selecao} corpo={corpo} zoom={4}
                animacao={animacao} animar />
        {tons.length > 0 && (
          <div className="avatar-tons" role="group" aria-label="tom de pele">
            {tons.map(([nome, amostra]) => (
              <button
                key={nome} className={nome === peleAtual ? "sel" : ""}
                onClick={() => trocarPele(nome)}
                title={`${rotuloDaCor(nome, undefined, catalogo.cores)} (${nome.split(":")[0]})`}
                aria-label={`tom de pele ${nome.replace(":", " ")}`}
                aria-pressed={nome === peleAtual}
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
                    data-corpo={c}
                    onClick={() => setCorpo(c)}>{ROTULO_DO_CORPO[c] ?? c}</button>
          ))}
        </div>
        {/* so o palco anima; as casas e a celula do picker seguem num frame so */}
        <div className="avatar-animacoes" role="group" aria-label="animação">
          {catalogo.recorte.animacoes.map((a) => (
            <button key={a} className={a === animacao ? "sel" : ""}
                    data-animacao={a}
                    onClick={() => setAnimacao(a)}>{ROTULO_DA_ANIMACAO[a] ?? a}</button>
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
                    // gancho estavel para a prova: o rotulo e traduzido e muda
                    data-slot={slot}
                    onClick={() => setAberto(slot)}
                    title={`${rotuloDoSlot(slot)}${item ? `: ${nomeDoItem(item)}` : " (vazio)"}`}
                  >
                    {item
                      ? <Boneco catalogo={catalogo} selecao={{ [slot]: equipado! }}
                                corpo={corpo} zoom={1} titulo={nomeDoItem(item)} />
                      : <span className="avatar-casa-vazia" aria-hidden="true" />}
                    <span className="avatar-casa-nome">{rotuloDoSlot(slot)}</span>
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
          selecao={selecao} corpo={corpo} animacao={animacao}
          aoEscolher={(e) => escolher(aberto, e)}
          aoFechar={() => setAberto(null)}
        />
      )}
    </div>
  );
}
