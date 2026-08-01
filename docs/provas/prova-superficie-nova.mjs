/**
 * O QUE A CORRECAO DA ISSUE #1 TROUXE DE NOVO -- e que ninguem tinha medido.
 *
 * `prova-issue-1.mjs` mostra que o defeito morreu. Este arquivo ataca o que
 * nasceu no lugar dele, porque cada peca nova e um caminho novo de perder
 * ficha -- que e exatamente o que a issue #1 fazia:
 *
 *   F. DEBOUNCE SEM FLUSH seria regressao: o codigo antigo gravava a cada
 *      tecla. Editar e recarregar dentro dos 500 ms tem de sobreviver.
 *   G. o seletor de fichas (`Fichas.tsx`) -- abrir, nova, apagar, e o que
 *      acontece com a ficha aberta quando ela mesma e apagada.
 *   H. `#/p/<id>`: endereco vivo retoma a ficha certa; endereco MORTO nao pode
 *      abrir outra ficha nem gravar por cima dela.
 *   I. duas fichas coexistindo: editar a segunda nao pode tocar na primeira.
 *
 * Uso: node docs/_verificacao/prova-superficie-nova.mjs <url>
 */
import { chromium } from "/home/igor0/waybuilder/app/node_modules/playwright/index.mjs";

const URL_APP = process.argv[2] ?? "http://localhost:5199/";
const CHAVE = "waybuilder:personagens";

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${detalhe ? `   ${detalhe}` : ""}`);
};

const estado = (pagina) => pagina.evaluate((chave) => {
  const lista = JSON.parse(localStorage.getItem(chave) ?? "[]");
  return {
    entradas: lista.length,
    ids: lista.map((e) => e?.id),
    nomes: lista.map((e) => e?.doc?.identidade?.nome ?? null),
    ultima: localStorage.getItem("waybuilder:ultima"),
    chaves: Object.keys(localStorage).sort(),
  };
}, CHAVE);

const pronto = (p) => p.waitForSelector("input.nome", { timeout: 60_000 });
const naTela = (p) => p.inputValue("input.nome");

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1400, height: 1000 } });
const erros = [];
pagina.on("pageerror", (e) => erros.push(String(e)));
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
// o `confirm()` de apagar: aceitar sempre, senao o teste trava
pagina.on("dialog", (d) => d.accept());

console.log(`\nSUPERFICIE NOVA DA CORRECAO -- ${URL_APP}`);
await pagina.goto(URL_APP);
await pronto(pagina);
await pagina.evaluate(() => localStorage.clear());

// == F: editar e recarregar DENTRO da janela do debounce ===================
console.log("\nF -- editar e recarregar em menos de 500 ms (o debounce nao pode comer)");
await pagina.reload();
await pronto(pagina);
await pagina.fill("input.nome", "Antes Do Debounce");
await pagina.reload();                 // sem esperar: dispara pagehide na hora
await pronto(pagina);
await pagina.waitForTimeout(900);
const f = await estado(pagina);
console.log(`  disco: ${f.entradas} entrada(s), nomes=${JSON.stringify(f.nomes)}`);
checar(f.entradas === 1 && f.nomes[0] === "Antes Do Debounce",
       "a edicao sobrevive ao F5 imediato (flush no pagehide)",
       `nomes=${JSON.stringify(f.nomes)}`);
checar(await naTela(pagina) === "Antes Do Debounce",
       "e ela volta na tela", `tela=${JSON.stringify(await naTela(pagina))}`);

// == G: o seletor de fichas ================================================
console.log("\nG -- o seletor: nova ficha, alternar, apagar");
await pagina.click("button:has-text('fichas')");
await pagina.waitForSelector(".fichas", { timeout: 10_000 });
checar((await pagina.locator(".fichas li").count()) === 1,
       "o seletor lista a ficha que existe",
       `li=${await pagina.locator(".fichas li").count()}`);

await pagina.click(".fichas button.nova");
await pagina.waitForSelector(".fichas", { state: "detached", timeout: 10_000 });
// `novoDocumento()` nomeia "Sem nome", e `temConteudo()` nao conta esse nome
// como conteudo -- e por isso que a ficha em branco nao vai ao disco
checar(await naTela(pagina) === "Sem nome",
       "'+ nova ficha' abre um documento em branco",
       `tela=${JSON.stringify(await naTela(pagina))}`);
const aposNova = await estado(pagina);
checar(aposNova.entradas === 1,
       "e a ficha em branco NAO e gravada antes de ter conteudo",
       `entradas=${aposNova.entradas}`);

await pagina.fill("input.nome", "Segunda Ficha");
await pagina.waitForTimeout(900);
const duas = await estado(pagina);
console.log(`  disco: ${duas.entradas} entrada(s), nomes=${JSON.stringify(duas.nomes)}`);
checar(duas.entradas === 2, "editar a segunda cria a SEGUNDA entrada, nao substitui a primeira",
       `nomes=${JSON.stringify(duas.nomes)}`);
checar(duas.nomes.includes("Antes Do Debounce") && duas.nomes.includes("Segunda Ficha"),
       "as duas fichas coexistem intactas", JSON.stringify(duas.nomes));
const idPrimeira = duas.ids[duas.nomes.indexOf("Antes Do Debounce")];
const idSegunda = duas.ids[duas.nomes.indexOf("Segunda Ficha")];
checar(idPrimeira !== idSegunda, "com ids distintos", `${idPrimeira} / ${idSegunda}`);

// alternar de volta para a primeira
await pagina.click("button:has-text('fichas')");
await pagina.waitForSelector(".fichas", { timeout: 10_000 });
await pagina.locator(".fichas li", { hasText: "Antes Do Debounce" }).locator("button.abrir").click();
await pagina.waitForTimeout(400);
checar(await naTela(pagina) === "Antes Do Debounce",
       "abrir pelo seletor troca para a ficha certa",
       `tela=${JSON.stringify(await naTela(pagina))}`);
checar((await pagina.evaluate(() => location.hash)) === `#/p/${idPrimeira}`,
       "e o endereco passa a nomear a ficha aberta",
       await pagina.evaluate(() => location.hash));

// == H: o endereco ========================================================
console.log("\nH -- `#/p/<id>`: endereco vivo retoma; endereco morto avisa e nao sobrescreve");
// CARGA de verdade, e nao `goto` so trocando o hash: mudar so o fragmento e
// navegacao no MESMO documento -- o React nao remonta e `abrir()` nao roda.
// E o que um jogador faz ao colar o endereco numa aba nova, ou dar F5 nela.
await pagina.goto(`${URL_APP}#/p/${idSegunda}`);
await pagina.reload();
await pronto(pagina);
await pagina.waitForTimeout(600);
checar(await naTela(pagina) === "Segunda Ficha",
       "abrir a URL de uma ficha retoma AQUELA ficha",
       `tela=${JSON.stringify(await naTela(pagina))}`);

await pagina.goto(`${URL_APP}#/p/p-nao-existe-9999`);
await pagina.reload();
await pronto(pagina);
await pagina.waitForTimeout(900);
const morto = await estado(pagina);
const textoAviso = await pagina.locator(".avisos").innerText().catch(() => "");
console.log(`  aviso: ${JSON.stringify(textoAviso.slice(0, 110))}`);
checar(await naTela(pagina) === "Sem nome",
       "endereco morto abre ficha NOVA, nao a de outro jogador",
       `tela=${JSON.stringify(await naTela(pagina))}`);
checar(/nao existe/i.test(textoAviso), "e AVISA em vez de recusar (principio 1)");
checar(morto.entradas === 2, "e nao grava nada por cima das duas que existem",
       `entradas=${morto.entradas} nomes=${JSON.stringify(morto.nomes)}`);

// == G2: apagar a ficha ABERTA ============================================
console.log("\nG2 -- apagar a ficha que esta aberta agora");
await pagina.goto(`${URL_APP}#/p/${idSegunda}`);
await pagina.reload();
await pronto(pagina);
await pagina.waitForTimeout(500);
checar(await naTela(pagina) === "Segunda Ficha", "  (pre-condicao: a Segunda esta aberta)",
       `tela=${JSON.stringify(await naTela(pagina))}`);
await pagina.click("button:has-text('fichas')");
await pagina.waitForSelector(".fichas", { timeout: 10_000 });
await pagina.locator(".fichas li", { hasText: "Segunda Ficha" }).locator("button.apagar").click();
await pagina.waitForTimeout(900);
const aposApagar = await estado(pagina);
console.log(`  disco: ${aposApagar.entradas} entrada(s), nomes=${JSON.stringify(aposApagar.nomes)}`);
checar(aposApagar.entradas === 1 && aposApagar.nomes[0] === "Antes Do Debounce",
       "apagar tira SO a escolhida", JSON.stringify(aposApagar.nomes));
await pagina.waitForTimeout(600);
checar(await naTela(pagina) === "Antes Do Debounce",
       "e o app cai na ficha que sobrou, sem tela orfa",
       `tela=${JSON.stringify(await naTela(pagina))}`);
await pagina.reload();
await pronto(pagina);
await pagina.waitForTimeout(900);
const depois = await estado(pagina);
checar(depois.entradas === 1, "e a apagada nao ressuscita no F5 seguinte",
       `entradas=${depois.entradas} nomes=${JSON.stringify(depois.nomes)}`);

// == identidade de build ==================================================
console.log("\nJ -- identidade de build carimbada no documento (achado 6/7/17)");
const carimbo = await pagina.evaluate((chave) => {
  const l = JSON.parse(localStorage.getItem(chave) ?? "[]");
  return l[0]?.doc?.base ?? null;
}, CHAVE);
console.log(`  base do documento: ${JSON.stringify(carimbo)}`);
checar(!!carimbo?.pin, "a ficha grava sob QUAL base foi editada", JSON.stringify(carimbo));
checar(!!carimbo?.nascida_em_pin, "e sob qual nasceu", JSON.stringify(carimbo?.nascida_em_pin));

console.log(`\nerros de console/pagina: ${erros.length}`);
for (const e of erros.slice(0, 6)) console.log(`  [erro] ${e.slice(0, 160)}`);
console.log(`\n${falhas === 0 ? "TUDO VERDE" : `${falhas} FALHA(S)`}\n`);
await navegador.close();
process.exit(falhas === 0 ? 0 : 1);
