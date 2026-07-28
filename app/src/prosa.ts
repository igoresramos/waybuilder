/**
 * Le o bloco corrido que vem das fontes e devolve as partes separadas.
 *
 * A prosa chega como UM paragrafo unico com tudo colado dentro -- nome, custo
 * de acao, livro, gatilho, requisito, o efeito, os quatro graus de sucesso e,
 * nas ancestralidades, seis secoes de fantasia. Lido assim, o jogador nao acha
 * a regra e nao sabe onde a regra acaba e o sabor comeca:
 *
 *   "Human Source Player Core pg. 62 Humans are diverse and adaptable people
 *    with wide potential... You Might... Strive to achieve greatness... Others
 *    Probably... Respect your flexibility..."
 *
 * Ha DUAS familias de texto, e a diferenca esta no dado, nao no chute:
 *
 * 1. **Com `---`** (feat 98%, spell 100%, weapon 91%, equipment 89%): a fonte
 *    ja separa cabecalho de corpo. O cabecalho carrega custo de acao, livro e
 *    os campos curtos de regra (Trigger, Requirements, Frequency).
 * 2. **Sem `---`** (ancestry, heritage, background, class, archetype: 0%): o
 *    texto e descritivo e se divide por RÓTULOS nomeados, todos presentes em
 *    50/50 das ancestralidades -- `You Might`, `Others Probably`,
 *    `Physical Description`, `Society`, `Alignment and Religion`, `Names`.
 *
 * A classificacao regra-x-sabor sai desses rotulos, que sao vocabulario fixo
 * da Paizo. Nada aqui adivinha pelo conteudo.
 */

/** Campos curtos de regra: valem uma linha `rotulo: valor`. */
const CAMPOS = [
  "Frequency", "Trigger", "Requirements", "Requirement", "Prerequisites",
  "Cost", "Access", "Activate", "Usage", "Bulk", "Hands", "Price", "Onset",
  "Saving Throw", "Duration", "Maximum Duration", "Range", "Area", "Targets",
  "Craft Requirements",
];

/** Blocos de regra que valem um paragrafo proprio. A ordem importa: */
/* "Critical Success" tem de ser testado antes de "Success". */
const BLOCOS_DE_REGRA = [
  "Critical Success", "Critical Failure", "Success", "Failure",
  "Effect", "Special", "Heightened",
];

/** Fantasia. Nao muda um numero da ficha. */
const BLOCOS_DE_SABOR = [
  "You Might", "Others Probably", "Physical Description",
  "Alignment and Religion", "Society", "Adventurers", "Ethnicities", "Names",
];

const CUSTOS = [
  "Single Action", "Two Actions", "Three Actions", "Free Action", "Reaction",
];

export interface Secao {
  rotulo: string | null;
  texto: string;
  tipo: "regra" | "sabor";
}

export interface ProsaAnalisada {
  custoDeAcao: string | null;
  fonte: string | null;
  /** Trigger, Requirements, Frequency... -- curtos, vao no topo */
  campos: Secao[];
  /** o efeito e os graus de sucesso */
  regra: Secao[];
  /** a fantasia */
  sabor: Secao[];
  /** true quando nao houve nada a separar -- a tela cai no texto cru */
  cru: boolean;
}

const escapar = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** `Rotulo` como palavra, nao no meio de outra (evita casar "Successor"). */
const marcador = (rotulos: string[]) =>
  new RegExp(`(?<![A-Za-z])(${rotulos.map(escapar).join("|")})(?![a-z])`, "g");

const TODOS = [...BLOCOS_DE_REGRA, ...BLOCOS_DE_SABOR, ...CAMPOS];

/** Quebra um trecho nos rotulos conhecidos, preservando o que vem antes. */
function fatiar(texto: string): Array<{ rotulo: string | null; texto: string }> {
  const re = marcador(TODOS);
  const saida: Array<{ rotulo: string | null; texto: string }> = [];
  let ultimo = 0;
  let rotuloAtual: string | null = null;
  let m: RegExpExecArray | null;

  while ((m = re.exec(texto)) !== null) {
    const antes = texto.slice(ultimo, m.index).trim();
    if (antes) saida.push({ rotulo: rotuloAtual, texto: antes });
    rotuloAtual = m[1];
    ultimo = m.index + m[0].length;
  }
  const resto = texto.slice(ultimo).trim();
  if (resto) saida.push({ rotulo: rotuloAtual, texto: resto });
  return saida;
}

const tipoDe = (rotulo: string | null): "regra" | "sabor" =>
  rotulo && BLOCOS_DE_SABOR.includes(rotulo) ? "sabor" : "regra";

/**
 * @param texto a prosa crua
 * @param nome  o nome do registro, para tirar a repeticao do inicio
 */
export function analisarProsa(texto: string, nome?: string): ProsaAnalisada {
  let t = texto.replace(/\s+/g, " ").trim();

  // 1. o nome se repete no comeco do texto -- ja esta no titulo da tela
  if (nome && t.startsWith(nome)) t = t.slice(nome.length).trim();

  // 2. custo de acao vem logo apos o nome
  let custoDeAcao: string | null = null;
  for (const c of CUSTOS) {
    if (t.startsWith(c)) {
      custoDeAcao = c;
      t = t.slice(c.length).trim();
      break;
    }
  }

  // 3. `Source <livro> pg. N[, <livro> pg. N]`.
  //
  // Delimitar pelo PROXIMO ROTULO nao serve: na ancestralidade nao ha rotulo
  // nenhum entre a fonte e o texto, e a fonte engolia a descricao inteira. O
  // que fecha a fonte e o proprio formato dela -- `<livro> pg. <numero>`,
  // repetivel por virgula.
  let fonte: string | null = null;
  const fonteRe = /^Source\s+((?:[^,]+?\s+pg\.\s+\d+)(?:\s*,\s*[^,]+?\s+pg\.\s+\d+)*)/;
  const mf = fonteRe.exec(t);
  if (mf) {
    fonte = mf[1].trim();
    t = t.slice(mf[0].length).trim();
  }

  // `Archetypes X (Level 4), Y (Level 2)` -- por onde mais se chega ao feat.
  // E informacao de acesso, nao a regra dele; sai do corpo para nao poluir.
  t = t.replace(/^Archetypes\s+.+?(?=\s+(?:Frequency|Trigger|Requirements?|Cost|---)|$)/, "").trim();

  // 4. o `---` que a fonte usa para separar cabecalho de corpo
  const corte = t.indexOf("---");
  const cabeca = corte >= 0 ? t.slice(0, corte).trim() : "";
  const corpo = corte >= 0 ? t.slice(corte + 3).trim() : t;

  const campos: Secao[] = [];
  const regra: Secao[] = [];
  const sabor: Secao[] = [];

  const partes = [...fatiar(cabeca), ...fatiar(corpo)];

  // A abertura SEM rotulo e ambigua, e o desempate esta na companhia dela: num
  // feat ela e o efeito; numa ancestralidade e a descricao que vem antes de
  // `You Might`. Se o registro tem blocos de sabor e nao tem `---` (as duas
  // marcas do texto descritivo), a abertura pertence ao sabor.
  const temSabor = partes.some((p) => tipoDe(p.rotulo) === "sabor");
  const descritivo = temSabor && corte < 0;

  partes.forEach((parte, i) => {
    if (!parte.texto) return;
    // `You Might... Strive a fazer X` -- a reticencia sobra do rotulo
    const texto = parte.texto.replace(/^[.…\s]+/, "").trim();
    if (!texto) return;

    const abertura = i === 0 && parte.rotulo === null;
    const tipo = descritivo && abertura ? "sabor" : tipoDe(parte.rotulo);
    const secao: Secao = { rotulo: parte.rotulo, texto, tipo };

    if (tipo === "sabor") sabor.push(secao);
    else if (parte.rotulo && CAMPOS.includes(parte.rotulo)) campos.push(secao);
    else regra.push(secao);
  });

  return {
    custoDeAcao, fonte, campos, regra, sabor,
    cru: campos.length === 0 && sabor.length === 0 && regra.length <= 1,
  };
}
