/**
 * Ordem de apresentacao das cores no seletor.
 *
 * Vive no app, e nao no pacote `waybuilder-avatar`, de proposito: nao e fato
 * sobre o acervo, e escolha de como a TELA mostra o que o acervo oferece.
 *
 * O problema que ela resolve: um canal chega a oferecer mais de cem rampas, e
 * elas chegam na ordem em que o arquivo de paleta as declara -- que nao tem
 * relacao nenhuma com a aparencia. Procurar "um verde escuro" nessa lista e
 * varrer botao por botao. Filtrar por nome tambem nao salva: os nomes do LPC
 * (`ivory`, `porcelain`, `lpcr`) descrevem a rampa, nao a cor. Sobra o pixel.
 */

/** Um par `[chave, amostra hex]`, como `coresDoCanal` devolve. */
export type Amostra = [string, string];

/** Um pedido de recolor, como `montarCamadas` o entrega. */
export type Recolor = {
  material: string; paleta: string; cor: string;
  base?: string; fonte?: string[];
};

/**
 * A identidade do bitmap recolorido: destino E origem, de todos os canais.
 *
 * O cache guarda o atlas inteiro ja repintado, chaveado por (arquivo, isto).
 * Faltando a ORIGEM, peca nenhuma que divida atlas e destino com outra ganha
 * bitmap proprio -- e o acervo esta cheio disso: 23 das 45 cabecas moram em
 * `head/L1/male.png` e todas herdam o mesmo tom de pele, mas nascem em seis
 * rampas distintas. A primeira desenhada respondia pelas 22 restantes, e o orc
 * (`ulpc.green`) recebia o bitmap do porco (`ulpc.light`), onde o recolor e
 * um no-op. Resultado na tela: cabeca verde num corpo cor de pele.
 */
export function chaveDoRecolor(recolors: Recolor[]): string {
  return recolors
    .map((r) => {
      // `fonte` vence `base`: quando a peca traz as cores embutidas, e ela que
      // diz em que rampa a arte foi pintada
      const origem = r.fonte?.length ? r.fonte.join(",") : (r.base ?? "");
      return `${r.material}|${r.paleta}|${r.cor}|${origem}`;
    })
    .join("+");
}

/** Quanto de saturacao uma cor precisa para ter matiz que valha agrupar. */
const PISO_DE_CROMA = 0.12;

/** Largura de cada faixa de matiz, em graus. 12 faixas cobrem a roda. */
const FAIXA = 30;

type Perfil = { faixa: number; luz: number; croma: number };

/** `#rrggbb` -> `[0..1, 0..1, 0..1]`, ou `null` se nao for hex de 6 digitos. */
function paraRgb(hex: string): [number, number, number] | null {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return null;
  const n = parseInt(m[1]!, 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

/**
 * Onde a cor cai na roda, quao clara e e quanto de croma tem.
 *
 * Matiz vira FAIXA, e nao angulo cru, porque o pedido e "td q e verde fica
 * junto e vai meio q por degrade": ordenar pelo angulo continuo intercala tons
 * de 118 e 122 graus e o degrade vira serrote. A faixa e deslocada meia
 * largura para que o vermelho puro (0 graus) fique no MEIO da primeira, junto
 * com os 350 -- senao a mesma familia nasce partida nas duas pontas da roda.
 */
function perfilar(hex: string): Perfil {
  const rgb = paraRgb(hex);
  // cor ilegivel nao inventa lugar: cai junto dos acromaticos, no fim
  if (!rgb) return { faixa: Infinity, luz: 0, croma: 0 };
  const [r, g, b] = rgb;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  const luz = (max + min) / 2;
  const croma = d === 0 ? 0 : d / (1 - Math.abs(2 * luz - 1));
  if (croma < PISO_DE_CROMA) return { faixa: Infinity, luz, croma };

  let h: number;
  if (max === r) h = ((g - b) / d) % 6;
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  h = (h * 60 + 360) % 360;
  return { faixa: Math.floor(((h + FAIXA / 2) % 360) / FAIXA), luz, croma };
}

/**
 * As cores agrupadas por familia, cada familia em degrade do escuro ao claro.
 *
 * Cinza, branco e preto nao tem familia -- vao para o fim, tambem em degrade
 * entre si, para nao poluir o meio da roda com uma coluna sem cor.
 *
 * A ordem nao depende da ordem de entrada: croma e chave desempatam o que luz
 * e faixa nao resolveram. Sem isso a mesma paleta sairia diferente conforme o
 * arquivo fosse lido, e o jogador perderia a memoria de onde a cor estava.
 */
export function ordenarPorMatiz(cores: Amostra[]): Amostra[] {
  const perfis = new Map<string, Perfil>();
  for (const [chave, hex] of cores) perfis.set(chave, perfilar(hex));
  return [...cores].sort(([ca], [cb]) => {
    const a = perfis.get(ca)!;
    const b = perfis.get(cb)!;
    return a.faixa - b.faixa || a.luz - b.luz || b.croma - a.croma
      || ca.localeCompare(cb);
  });
}
