/**
 * Todo seletor de cor e um quadradinho -- spec, decisao 5f.
 *
 * O painel tinha duas aparencias para o mesmo gesto: quadradinho colorido nas
 * 391 pecas com paleta e o NOME escrito nas 227 do formato antigo, onde a cor
 * mora na arte e o app nao tinha o RGB. O build passou a dizer a cor, e esta
 * prova exige que a tela use.
 *
 * O modo de falha que ela pega: acervo publicado sem o campo `amostras`, ou
 * catalogo velho em cache. Nos dois casos a tela cai no nome escrito -- sem
 * erro nenhum -- e a inconsistencia volta calada.
 *
 * Por que checar a COR do quadradinho e nao so a presenca dele: um swatch que
 * existe mas sai transparente ou preto em tudo tambem "padroniza", e mente.
 */
import { chromium } from "playwright";

// pecas do formato ANTIGO (faixa de atlas), que antes mostravam o nome escrito
const SLOTS = ["hat", "shield", "cape"];
const falhas = [];

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5183/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(2500);

const vistos = [];
for (const slot of SLOTS) {
  const casa = p.locator(`.avatar-casa[data-slot="${slot}"]`).first();
  if (!(await casa.count())) { falhas.push(`slot "${slot}": sem casa no painel`); continue; }
  await casa.click();
  await p.waitForTimeout(1800);

  const r = await p.evaluate(() => {
    const botoes = [...document.querySelectorAll(".avatar-picker .avatar-tons button")];
    if (!botoes.length) return null;
    let comSwatch = 0, semSwatch = 0;
    const cores = new Set();
    for (const bt of botoes) {
      const sp = bt.querySelector(".avatar-tom");
      if (sp) {
        comSwatch++;
        cores.add(getComputedStyle(sp).backgroundColor);
      } else semSwatch++;
    }
    return { total: botoes.length, comSwatch, semSwatch, coresDistintas: cores.size,
             amostraDeCores: [...cores].slice(0, 3) };
  });

  if (!r) { falhas.push(`slot "${slot}": nenhum botao de cor no picker`); await p.keyboard.press("Escape"); continue; }
  if (r.semSwatch > 0)
    falhas.push(`slot "${slot}": ${r.semSwatch} de ${r.total} cores ainda como NOME escrito`);
  // um swatch por cor, todos iguais, seria padronizacao mentirosa
  if (r.comSwatch > 1 && r.coresDistintas < 2)
    falhas.push(`slot "${slot}": ${r.comSwatch} quadradinhos e so ${r.coresDistintas} cor distinta`);
  vistos.push({ slot, ...r });
  await p.keyboard.press("Escape");
  await p.waitForTimeout(300);
}

const seg = erros.filter((e) => /SecurityError/i.test(e));
if (seg.length) falhas.push(`SecurityError: ${seg[0]}`);

console.log(JSON.stringify({ vistos, falhas }, null, 1));
await b.close();
process.exit(falhas.length === 0 ? 0 : 1);
