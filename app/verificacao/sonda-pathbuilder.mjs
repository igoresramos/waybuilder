/**
 * Colhe do Pathbuilder O QUE ELE OFERECE num slot, e grava em JSON.
 *
 * E o oraculo de COMPORTAMENTO -- a tese que justifica ter o Pathbuilder
 * rodando local. O export JSON do proprio app da o resultado final
 * (proficiencia em numero, feats escolhidos), mas a pergunta que interessa e
 * outra: "num Fighter 1, que feats de classe ele oferece?" Isso so a tela
 * responde, e e o que o `candidatos()` do Waybuilder tem de bater.
 *
 * Estrutura mapeada em 2026-07-29 (receita em docs/2026-07-29_pathbuilder-local.md):
 *
 *     #divBuildLevels .build-section       <- um por nivel
 *       #id_header                         <- "Level 1"
 *       #id_parent_feats .div-button       <- um por slot
 *         .small-text.grey-text            <- rotulo ("Class Feat")
 *         .button-selection                <- valor ("Not Selected")
 *
 * Uso: node verificacao/sonda-pathbuilder.mjs [nivel]
 * Saida: docs/comparacao/pathbuilder-fighter-class_feat-nv<N>.json
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { abrirPathbuilder } from "./pathbuilder-comum.mjs";
import { docs } from "./caminhos.mjs";

const [CLASSE = "Fighter", NIVEL_TXT = "1", SLOT = "Class Feat"] = process.argv.slice(2);
const NIVEL = Number(NIVEL_TXT);
const SAIDA = docs("comparacao");
const chave = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");

const { navegador, pagina } = await abrirPathbuilder();

// tela inicial -> criacao -> construtor (Human / Barkeep / Fighter 1, o default)
await pagina.locator("img[src*='character_new']").first().click({ timeout: 10_000 });
await pagina.waitForTimeout(2500);
// "Allow outdated CRB and APG?" nasce Off, e ai o Pathbuilder esconde todo o
// conteudo legado -- que a NOSSA base inclui. Sem ligar, a comparacao acusa
// como buraco o que e so recorte diferente: `Dragging Strike` (APG),
// `Dragon Disciple`, `Horizon Walker`, `Loremaster`, `Shadowdancer` (todos APG).
//
// O interruptor e um `<label class="switch">` com um checkbox DENTRO -- clicar
// no texto do rotulo (que fica num `<span>` irmao) nao alterna nada.
await pagina.evaluate(() => {
  for (const c of document.querySelectorAll(".checkbox-container")) {
    if (/outdated/i.test(c.textContent || "")) c.querySelector("label.switch")?.click();
  }
});
await pagina.waitForTimeout(600);
console.log("toggles:", (await pagina.locator("#root").innerText())
  .replace(/\n+/g, " | ").match(/Allow outdated[^|]*\|[^|]*/)?.[0]?.trim());

await pagina.locator(".modal-button", { hasText: "Get Started" }).first().click();
await pagina.waitForTimeout(3500);
// o modal fica no DOM depois de fechado e INTERCEPTA o clique -- some com Escape
await pagina.keyboard.press("Escape").catch(() => {});
await pagina.waitForTimeout(800);
console.log("modais no DOM:", await pagina.locator(".modal").count(),
            "| visiveis:", await pagina.locator(".modal:visible").count());

/**
 * O `.div-button` de um slot, dentro do bloco daquele nivel.
 *
 * Por INDICE, e nao por texto do cabecalho: `#id_header` esta repetido em todos
 * os 20 blocos (id duplicado, e a pagina e assim mesmo) e `hasText: "Level 1"`
 * casaria tambem "Level 10" ate "Level 19".
 *
 * O indice e o proprio nivel porque a PRIMEIRA `.build-section` nao e um nivel:
 * e o bloco de identidade (Ancestry / Background / Class / Dual Class).
 */
const slotDoNivel = (rotulo, nivel) =>
  pagina.locator(".build-section").nth(nivel)
        .locator(`.div-button:has-text("${rotulo}")`)
        .first();

/**
 * Tudo que a lista aberta oferece: nome, nivel e se o Pathbuilder o marca como
 * indisponivel.
 *
 * `.listview-title.red-text` e o "nao atende" DELES -- e a confirmacao de que o
 * Pathbuilder tambem MOSTRA o que o personagem nao pode pegar, em vermelho, em
 * vez de esconder. Mesma decisao do principio zero do Waybuilder, tomada de
 * forma independente.
 *
 * Mesma armadilha da lista virtualizada do proprio Waybuilder: contar o que
 * esta no DOM subconta, e acumular cada leitura num array faz o total crescer
 * para sempre. Acumula em Map por nome e rola ate parar de aparecer novidade.
 */
async function opcoesDaLista() {
  const achados = new Map();
  let paradas = 0;
  while (paradas < 3) {
    const antes = achados.size;
    for (const linha of await pagina.evaluate(() =>
      // dentro do MODAL: `.listview-item` tambem existe na arvore de niveis do
      // fundo, e sem o escopo a colheita trazia as features da ficha
      // ("Reactive Strike", "Free Feat: Shield Block") junto com os candidatos
      [...document.querySelectorAll(".modal-content-listview .listview-item")].map((e) => ({
        nome: (e.querySelector(".listview-title")?.textContent ?? "").trim(),
        nivel: (e.querySelector(".listview-item-level")?.textContent ?? "").trim(),
        atende: !e.querySelector(".listview-title.red-text"),
      })))) {
      if (linha.nome) achados.set(linha.nome, linha);
    }
    const rolou = await pagina.evaluate(() => {
      const alvo = document.querySelector(".div-listview-scroller");
      if (!alvo) return false;
      const topo = alvo.scrollTop;
      alvo.scrollTop += 600;
      return alvo.scrollTop !== topo;
    });
    await pagina.waitForTimeout(120);
    paradas = (achados.size === antes && !rolou) ? paradas + 1 : 0;
  }
  return [...achados.values()];
}

// A classe entra no bloco de IDENTIDADE (o `.build-section` de indice 0), nao
// num nivel. Trocar exige subir o personagem antes? Nao: a arvore mostra os 20
// niveis desde o inicio, e o Pathbuilder deixa abrir slot de nivel futuro.
if (CLASSE !== "Fighter") {
  const linha = pagina.locator(".build-section").nth(0)
                      .locator('.div-button:has-text("Class")').first();
  await linha.click({ timeout: 15_000 });
  await pagina.waitForTimeout(1500);
  console.log("abas do modal de classe:",
              JSON.stringify(await pagina.locator(".section-menu").allTextContents()));
  console.log("primeiros itens:",
              JSON.stringify((await pagina.locator(".modal-content-listview .listview-title")
                                .allTextContents()).slice(0, 8)));
  await pagina.locator(".modal-content-listview .listview-title",
                       { hasText: new RegExp(`^${CLASSE}$`) }).first().click();
  await pagina.waitForTimeout(800);
  await pagina.locator(".modal-button", { hasText: /^(Select|OK|Accept)$/ }).first()
              .click({ timeout: 4000 }).catch(() => {});
  await pagina.waitForTimeout(2500);
}

const alvo = slotDoNivel(SLOT, NIVEL);
if (await alvo.count() === 0) {
  // falha com o que EXISTE no bloco, e nao com stack trace: um Fighter 1 nao
  // tem `Skill Feat` (so no nivel 2), e a mensagem tem de dizer isso
  const tem = await pagina.locator(".build-section").nth(NIVEL)
                          .locator(".grey-text").allTextContents();
  console.log(`FALHA: nivel ${NIVEL} de ${CLASSE} nao tem slot "${SLOT}". `
              + `Tem: ${tem.filter(Boolean).join(", ")}`);
  await navegador.close();
  process.exit(2);
}
await alvo.scrollIntoViewIfNeeded();
await alvo.click({ timeout: 15_000 });
await pagina.waitForTimeout(2500);

// O modal tem QUATRO abas, e comparar so a primeira mente: o Waybuilder aceita
// feat de arquetipo no slot de class feat (RAW), e o Pathbuilder tambem -- so
// que em outra aba. Sem percorrer as quatro, a diferenca aparecia como 2.135
// feats "so no Waybuilder", que e ruido de recorte, nao defeito.
// As abas MUDAM por slot: `Class Feat` abre quatro (Class/Dedication/Archetype
// Class/All), `General Feat` abre so `All Feats`, e `Skill Feat` tem as suas.
// Lista fixa fazia a colheita voltar vazia sem dizer por que -- entao as abas
// sao DESCOBERTAS, tirando as nove do menu da ficha, que nao sao do modal.
//
// A busca tem de ficar PRESA ao `.modal:visible` -- em Wizard/Cleric o menu da
// ficha ganha uma aba extra com o NOME DA CLASSE (ex.: "Wizard"), que nao cabe
// na barra e fica no DOM com largura/altura zero (confirmado com getBoundingClientRect,
// dentroDeModal: false). Um `.section-menu` sem escopo pega essa aba fantasma,
// ela nao esta na lista fixa `MENU_DA_FICHA`, e o clique fica 30s tentando um
// elemento que nunca fica visivel -- TimeoutError, so em classe com essa aba
// extra (Fighter/Rogue nao tem, por isso passavam).
const MENU_DA_FICHA = new Set(["Weapons", "Defense", "Gear", "Spells", "Pets",
                               "Details", "Feats", "Actions", "Rituals"]);
const ABAS = (await pagina.locator(".modal:visible .section-menu").allTextContents())
  .map((t) => t.trim()).filter((t) => t && !MENU_DA_FICHA.has(t));
console.log("abas do modal:", JSON.stringify(ABAS));
const porAba = {};
for (const aba of ABAS) {
  const botao = pagina.locator(".modal:visible .section-menu", { hasText: aba }).first();
  if (await botao.count() === 0) { console.log(`  (aba ausente: ${aba})`); continue; }
  await botao.click();
  await pagina.waitForTimeout(1200);
  await pagina.evaluate(() => {
    const alvo = document.querySelector(".div-listview-scroller");
    if (alvo) alvo.scrollTop = 0;
  });
  const lista = await opcoesDaLista();
  porAba[aba] = lista;
  const atendem = lista.filter((o) => o.atende).length;
  console.log(`  ${aba.padEnd(22)} ${String(lista.length).padStart(5)} opcoes `
              + `(${atendem} disponiveis, ${lista.length - atendem} em vermelho)`);
}
// `All Feats` e a lista completa do slot; sem ela (slots que nao a oferecem),
// vale a uniao das abas
const opcoes = porAba["All Feats"] ?? Object.values(porAba).flat();

mkdirSync(SAIDA, { recursive: true });
const arquivo = `${SAIDA}/pathbuilder-${chave(CLASSE)}-${chave(SLOT)}-nv${NIVEL}.json`;
writeFileSync(arquivo, JSON.stringify(
  { fonte: "pathbuilder 2e web 108, remaster on, legado ligado",
    classe: CLASSE, nivel: NIVEL, slot: chave(SLOT), abas: porAba, opcoes },
  null, 2));
console.log(`-> ${arquivo}`);

await pagina.screenshot({ path: docs("screenshots/2026-07-29_pathbuilder-slot.png") });
await navegador.close();
