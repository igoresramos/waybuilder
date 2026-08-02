/**
 * O boneco gira de verdade -- spec, decisao 3b3 @12.
 *
 * O acervo passou a trazer duas direcoes (frente e perfil direito) lado a lado
 * no eixo X do atlas, e o endereco de um frame virou
 * `x + (indice_da_direcao * frames + k) * 64`. Errar esse indice tem um modo de
 * falha que NAO da erro: o canvas desenha, so que a arte errada -- ou a mesma
 * dos dois lados (offset ignorado), ou o boneco de costas (se a ordem das
 * direcoes fosse a do LPC, onde a frente e a terceira linha).
 *
 * Por isso a prova nao pergunta "mudou alguma coisa": ela exige que o conjunto
 * de pixels seja DIFERENTE entre as duas direcoes e que nenhuma das duas saia
 * vazia. Comparar por conjunto de cores nao bastaria -- girar mantem a paleta e
 * muda a forma --, entao a comparacao e por assinatura do bitmap inteiro.
 */
import { chromium } from "playwright";

const falhas = [];
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 900 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));

await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(2500);

/** Assinatura do palco: quantos pixels opacos e a soma dos canais. */
const assinatura = () =>
  p.evaluate(() => {
    const cv = document.querySelector(".avatar-palco canvas");
    if (!cv) return null;
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    let opacos = 0, soma = 0;
    for (let i = 0; i < d.length; i += 4)
      if (d[i + 3] > 0) { opacos++; soma += d[i] + d[i + 1] * 3 + d[i + 2] * 7 + i % 97; }
    return { opacos, soma };
  });

const botoes = p.locator(".avatar-direcoes button");
const n = await botoes.count();
if (n === 0) falhas.push("nenhum botao de direcao na tela -- o controle nao apareceu");

const rotulos = [];
for (let i = 0; i < n; i++) rotulos.push((await botoes.nth(i).innerText()).trim());

// O palco ANIMA a 8 FPS, entao uma unica captura por direcao nao prova nada:
// duas leituras da MESMA direcao ja diferem so por estarem em quadros
// diferentes do ciclo. A comparacao valida e entre CONJUNTOS de quadros -- se
// girar mudasse alguma coisa, nenhum quadro de uma direcao apareceria na outra.
const AMOSTRAS = 8;
const vistas = [];
for (let i = 0; i < n; i++) {
  await botoes.nth(i).click();
  await p.waitForTimeout(600);
  const quadros = new Set();
  let opacosMax = 0;
  for (let t = 0; t < AMOSTRAS; t++) {
    const a = await assinatura();
    if (!a) { falhas.push(`direcao "${rotulos[i]}": canvas do palco nao encontrado`); break; }
    quadros.add(a.soma);
    opacosMax = Math.max(opacosMax, a.opacos);
    await p.waitForTimeout(160);
  }
  if (opacosMax === 0) falhas.push(`direcao "${rotulos[i]}": o boneco saiu VAZIO`);
  vistas.push({ direcao: rotulos[i], quadrosDistintos: quadros.size, opacosMax, quadros });
}

// Nenhum quadro pode ser comum a duas direcoes: se for, o offset nao foi
// aplicado e as duas estao desenhando a mesma arte.
for (let i = 0; i < vistas.length; i++)
  for (let j = i + 1; j < vistas.length; j++) {
    const comuns = [...vistas[i].quadros].filter((q) => vistas[j].quadros.has(q));
    if (comuns.length)
      falhas.push(
        `"${vistas[i].direcao}" e "${vistas[j].direcao}" compartilham ${comuns.length}`
        + " quadro(s) identico(s) -- o offset da direcao nao esta sendo aplicado");
  }
for (const v of vistas) delete v.quadros;

const seg = erros.filter((e) => /SecurityError/i.test(e));
if (seg.length) falhas.push(`SecurityError: ${seg[0]}`);

console.log(JSON.stringify({ direcoes: rotulos, vistas, falhas }, null, 1));
await b.close();
process.exit(falhas.length === 0 ? 0 : 1);
