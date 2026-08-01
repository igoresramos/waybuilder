/**
 * PROVA INDEPENDENTE da issue #1 -- escrita pelo verificador, nao por quem
 * implementou. Nao importa nada de `app/src`: so mede o que o NAVEGADOR deixa
 * na chave `waybuilder:personagens`, que e o banco de verdade deste app.
 *
 * O defeito medido era: `App.tsx:54` cunhava `doc.novoId()` a cada mount e
 * `App.tsx:63-65` so gravava, nunca lia -- entao cada recarga deixava UMA
 * entrada nova e a ficha do jogador nunca voltava.
 *
 * Os tres experimentos, todos com F5 de verdade (`page.reload()`):
 *
 *   A. ficha com conteudo + 3 recargas -> quantas entradas? (era 4, tem de ser 1)
 *   B. a ficha VOLTA depois do F5? (nome, id e escolhas)
 *   C. visita ociosa + 3 recargas -> tem de deixar ZERO entrada
 *
 * Uso: node docs/_verificacao/prova-issue-1.mjs <url>
 *      (precisa do dev server de pe na url dada)
 *
 * O mesmo arquivo roda contra o codigo NOVO e contra o worktree em HEAD (que
 * ainda tem o defeito): o antes/depois vem do mesmo instrumento.
 */
import { chromium } from "/home/igor0/waybuilder/app/node_modules/playwright/index.mjs";

const URL_APP = process.argv[2] ?? "http://localhost:5199/";
const CHAVE = "waybuilder:personagens";
const ESPERA_DEBOUNCE = 1200; // o debounce do app e 500 ms; sobra folga

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${detalhe ? `   ${detalhe}` : ""}`);
};

/** O que existe em disco, lido de dentro da pagina -- nao de dentro do app. */
const estado = (pagina) => pagina.evaluate((chave) => {
  const cru = localStorage.getItem(chave);
  let lista = null;
  try { lista = JSON.parse(cru ?? "null"); } catch { lista = "ILEGIVEL"; }
  return {
    bytes: cru ? cru.length : 0,
    entradas: Array.isArray(lista) ? lista.length : (cru === null ? 0 : -1),
    ids: Array.isArray(lista) ? lista.map((e) => e?.id ?? null) : [],
    idsInternos: Array.isArray(lista) ? lista.map((e) => e?.doc?.id ?? null) : [],
    nomes: Array.isArray(lista) ? lista.map((e) => e?.doc?.identidade?.nome ?? null) : [],
    escolhas: Array.isArray(lista) ? lista.map((e) => (e?.doc?.escolhas ?? []).length) : [],
    chaves: Object.keys(localStorage).sort(),
  };
}, CHAVE);

const pronto = (pagina) => pagina.waitForSelector("input.nome", { timeout: 60_000 });

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1400, height: 1000 } });
const errosDeConsole = [];
pagina.on("pageerror", (e) => errosDeConsole.push(String(e)));
pagina.on("console", (m) => { if (m.type() === "error") errosDeConsole.push(m.text()); });

console.log(`\nPROVA DA ISSUE #1 -- ${URL_APP}`);

// -- limpeza: o banco comeca vazio, senao nada aqui significa nada ----------
await pagina.goto(URL_APP);
await pronto(pagina);
await pagina.evaluate(() => localStorage.clear());

// == A e B: ficha com conteudo sobrevive a 3 recargas ======================
console.log("\nA/B -- uma ficha com conteudo, tres recargas");
await pagina.reload();
await pronto(pagina);

// conteudo: um nome que o jogador digitou (nao o "Sem nome" do documento novo)
await pagina.fill("input.nome", "Prova Issue Um");
// e uma escolha de verdade, pelo mesmo caminho que o jogador usa
const linhaAncestria = pagina.locator(".slot-linha", { hasText: /ancestralidade/i }).first();
let escolheu = false;
try {
  await linhaAncestria.scrollIntoViewIfNeeded({ timeout: 5000 });
  await linhaAncestria.click({ timeout: 5000 });
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill("Dwarf");
  await pagina.waitForTimeout(400);
  await pagina.locator(".modal-lista .nome", { hasText: /^Dwarf$/i }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
  escolheu = true;
} catch (e) {
  console.log(`  (nao consegui clicar a ancestria: ${String(e).slice(0, 90)})`);
}
await pagina.waitForTimeout(ESPERA_DEBOUNCE);

const depoisDaEdicao = await estado(pagina);
console.log(`  apos editar: ${depoisDaEdicao.entradas} entrada(s), ids=${JSON.stringify(depoisDaEdicao.ids)}`);
checar(depoisDaEdicao.entradas === 1, "a edicao deixa exatamente 1 entrada",
       `entradas=${depoisDaEdicao.entradas}`);
const idOriginal = depoisDaEdicao.ids[0];

const trilha = [];
for (let i = 1; i <= 3; i++) {
  await pagina.reload();
  await pronto(pagina);
  await pagina.waitForTimeout(ESPERA_DEBOUNCE); // deixa o debounce agir se for gravar
  const e = await estado(pagina);
  const naTela = await pagina.inputValue("input.nome");
  trilha.push({ recarga: i, entradas: e.entradas, bytes: e.bytes, ids: e.ids, naTela });
  console.log(`  recarga ${i}: ${e.entradas} entrada(s), ${e.bytes} bytes, `
              + `nome na tela = ${JSON.stringify(naTela)}, ids=${JSON.stringify(e.ids)}`);
}

const fim = await estado(pagina);
checar(fim.entradas === 1, "3 recargas -> ainda 1 entrada (o defeito dava 4)",
       `entradas=${fim.entradas}`);
checar(fim.ids[0] === idOriginal, "o id da entrada nao muda a cada mount",
       `${idOriginal} -> ${fim.ids[0]}`);
checar(fim.idsInternos[0] === fim.ids[0], "o id vive DENTRO do documento (nao so no indice)",
       `doc.id=${fim.idsInternos[0]} indice=${fim.ids[0]}`);
checar(await pagina.inputValue("input.nome") === "Prova Issue Um",
       "a ficha do jogador VOLTA depois do F5 (nome)",
       `tela=${JSON.stringify(await pagina.inputValue("input.nome"))}`);
if (escolheu) {
  checar(fim.escolhas[0] > 0, "e as escolhas voltam junto", `escolhas=${fim.escolhas[0]}`);
}

// == C: visita ociosa nao pode deixar entrada ==============================
console.log("\nC -- visita ociosa, tres recargas (nenhuma edicao)");
await pagina.evaluate(() => localStorage.clear());
for (let i = 1; i <= 3; i++) {
  await pagina.reload();
  await pronto(pagina);
  await pagina.waitForTimeout(ESPERA_DEBOUNCE);
  const e = await estado(pagina);
  console.log(`  recarga ${i}: ${e.entradas} entrada(s), ${e.bytes} bytes`);
}
const ocioso = await estado(pagina);
checar(ocioso.entradas === 0, "abrir o app sem editar nao deixa ficha nenhuma",
       `entradas=${ocioso.entradas}`);

// == D: crescimento -- o sintoma que enchia a cota =========================
console.log("\nD -- crescimento em bytes ao longo das recargas de A/B");
console.log(`  ${trilha.map((t) => `${t.bytes}`).join(" -> ")} bytes`);
const cresceu = trilha[trilha.length - 1].bytes > trilha[0].bytes * 1.5;
checar(!cresceu, "o disco nao cresce a cada recarga",
       trilha.map((t) => t.bytes).join(" -> "));

// == E: a SESSAO REAL -- editar, recarregar, editar de novo ================
//
// Este e o experimento que reproduz o crescimento ilimitado, e o de A/B nao
// reproduzia: no codigo com defeito o `salvar` so dispara com
// `d.escolhas.length` (`App.tsx:64` em HEAD), entao uma recarga OCIOSA nao
// escreve nada -- ela apenas perde a ficha. A entrada nova nasce quando o
// jogador, sem saber que perdeu, faz a primeira escolha do "novo" personagem:
// o id daquele mount e outro, e `salvar(id, d)` nunca colide com o anterior.
// E o ciclo normal de uso: abrir, montar, fechar, voltar amanha.
console.log("\nE -- sessao real: editar / F5 / editar de novo, tres vezes");
await pagina.evaluate(() => localStorage.clear());
await pagina.reload();
await pronto(pagina);

const ciclos = [];
for (let i = 1; i <= 4; i++) {
  await pagina.fill("input.nome", `Sessao ${i}`);
  const linha = pagina.locator(".slot-linha", { hasText: /ancestralidade/i }).first();
  try {
    await linha.click({ timeout: 5000 });
    await pagina.waitForSelector(".modal", { timeout: 10_000 });
    await pagina.locator(".modal .busca").fill("Dwarf");
    await pagina.waitForTimeout(400);
    await pagina.locator(".modal-lista .nome", { hasText: /^Dwarf$/i }).first().click();
    await pagina.locator(".modal footer .aceitar").click();
    await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
  } catch { /* ja escolhida neste mount: a edicao do nome basta */ }
  await pagina.waitForTimeout(ESPERA_DEBOUNCE);
  const e = await estado(pagina);
  ciclos.push(e);
  console.log(`  edicao ${i}: ${e.entradas} entrada(s), ${e.bytes} bytes, `
              + `nomes=${JSON.stringify(e.nomes)}`);
  if (i < 4) { await pagina.reload(); await pronto(pagina); await pagina.waitForTimeout(600); }
}
const ultimo = ciclos[ciclos.length - 1];
checar(ultimo.entradas === 1,
       "4 sessoes de edicao com F5 entre elas -> 1 ficha, nao 4",
       `entradas=${ultimo.entradas} ids=${JSON.stringify(ultimo.ids)}`);
checar(ultimo.nomes.length === 1 && ultimo.nomes[0] === "Sessao 4",
       "e a ficha e a MESMA, com a ultima edicao dentro",
       `nomes=${JSON.stringify(ultimo.nomes)}`);

console.log(`\nerros de console/pagina: ${errosDeConsole.length}`);
for (const e of errosDeConsole.slice(0, 5)) console.log(`  [erro] ${e.slice(0, 160)}`);

console.log(`\n${falhas === 0 ? "TUDO VERDE" : `${falhas} FALHA(S)`}\n`);
await navegador.close();
process.exit(falhas === 0 ? 0 : 1);
