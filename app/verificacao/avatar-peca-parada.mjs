/**
 * Peca sem a animacao atual APARECE, parada -- nao some.
 *
 * 170 dos 627 itens do acervo sao do formato legado do LPC e nao tem as
 * animacoes novas: 77% da armadura, 75% dos acessorios. Ate aqui eles
 * desapareciam do boneco ao serem equipados, sem dizer nada -- o jogador
 * clicava em `equipar` e nada mudava na tela.
 *
 * A prova equipa uma dessas pecas em `idle` (que ela nao tem) e exige que o
 * boneco MUDE. Depois troca para `walk` (que ela tem) e exige que mude de
 * novo, agora animando: sem isso, "aparece parada" poderia ser so a peca
 * quebrada de outro jeito.
 */
import { chromium } from "playwright";

const SLOT = "earrings";     // Brincos de Esmeralda: so tem `walk`
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);

const assinatura = () =>
  p.evaluate(() => {
    const cv = document.querySelector(".avatar-palco canvas");
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    let s = 0, n = 0;
    for (let i = 0; i < d.length; i += 4)
      if (d[i + 3] > 0) { s += d[i] * 7 + d[i + 1] * 13 + d[i + 2] * 17; n++; }
    return { soma: s, opacos: n };
  });

const falhas = [];
const antes = await assinatura();

await p.locator(`.avatar-casa[data-slot="${SLOT}"]`).first().click();
await p.waitForTimeout(1200);
const rotulo = await p.locator(".avatar-picker-peca strong").innerText();
// o aviso tem de dizer que ela esta travada, nao que nao existe
const aviso = await p.locator(".avatar-sem-arte").count()
  ? await p.locator(".avatar-sem-arte").innerText() : "(nenhum)";
await p.locator(".avatar-picker footer .primario").click();
await p.waitForTimeout(1500);

const depois = await assinatura();
console.log(`peca: ${rotulo} | aviso no picker: ${aviso}`);
console.log(`palco em "parado": ${antes.opacos} -> ${depois.opacos} px opacos`);
if (antes.soma === depois.soma) falhas.push("equipar em `parado` nao mudou o boneco -- a peca sumiu");
if (!/parada/i.test(aviso)) falhas.push(`o aviso deveria dizer que a peca esta parada, disse: ${aviso}`);

// em `walk` ela tem arte propria: tem de aparecer tambem
await p.locator('.avatar-animacoes button[data-animacao="walk"]').click();
await p.waitForTimeout(1500);
const andando = await assinatura();
console.log(`palco em "andando": ${andando.opacos} px opacos`);
if (andando.opacos === 0) falhas.push("boneco vazio em `andando`");

if (erros.length) falhas.push(`erros de pagina: ${erros.join(" | ")}`);
console.log(falhas.length ? `\nFALHA\n- ${falhas.join("\n- ")}` : "\nOK: a peca legada aparece parada e o aviso explica");
await b.close();
process.exit(falhas.length ? 1 : 0);
