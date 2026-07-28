/**
 * Limpa a marcacao do Pf2eTools que sobra no texto das fontes.
 *
 * `requires_texto` vem com a sintaxe de link do Pf2eTools em **53% dos 3.960
 * feats que tem requisito**: `trained in {@skill Athletics|PC1}` em vez de
 * "trained in Athletics", `{@feat Everstand Stance|LOCG}` em vez do nome. Sem
 * limpar, o pre-requisito -- que existe justamente para ser lido de relance --
 * fica ilegivel na tela.
 *
 * Formato: `{@tag Rotulo|FONTE|apelido}`. O que interessa e sempre o PRIMEIRO
 * campo depois da tag, exceto em `{@dice 1d6}`, onde o proprio texto e o valor.
 * As 20 tags observadas (feat, skill, class, action, spell, trait, ancestry,
 * ...) seguem todas a mesma forma, entao uma regra so serve.
 *
 * Isto e limpeza de APRESENTACAO, nao correcao de dado: a base guarda o que a
 * fonte deu, e o pipeline continua sendo o lugar de consertar o dado em si.
 */

const TAG = /\{@(\w+)\s+([^}]*)\}/g;

export function limparMarcacao(texto: string): string {
  // As tags ANINHAM -- `{@note (or {@feat Shape of the Cloud Dragon|SoT3})}` --
  // e `[^}]*` para no primeiro fecha-chaves. Resolver de dentro para fora ate
  // estabilizar cobre qualquer profundidade; o limite so impede laco infinito
  // se aparecer uma forma que a regra nao entenda.
  let antes = texto;
  for (let i = 0; i < 5; i++) {
    const depois = antes.replace(TAG, (_todo, tag: string, corpo: string) => {
      const partes = corpo.split("|");
      // `{@dice 1d6}` e `{@note ...}` nao tem rotulo separado: o corpo e o texto
      if (tag === "dice" || tag === "note") return partes[0].trim();
      // apelido explicito (`{@feat Sudden Charge|PC1|carga}`) ganha do nome
      const apelido = partes[2]?.trim();
      return (apelido || partes[0].trim());
    });
    if (depois === antes) break;
    antes = depois;
  }
  return antes.replace(/\s+/g, " ").trim();
}
