import { describe, expect, test } from "vitest";
import { chaveDoRecolor, ordenarPorMatiz, type Amostra } from "./cores";

/**
 * O cache de bitmap recolorido guarda por (atlas, transformacao). Se a chave
 * nao descreve a transformacao inteira, uma peca recebe o bitmap de outra.
 *
 * Medido no acervo: 23 das 45 cabecas dividem o atlas `head/L1/male.png` e
 * caem no mesmo destino `body|ulpc|light` -- mas nascem em SEIS rampas de
 * origem diferentes (`ulpc.green` no orc, `ulpc.light` no porco,
 * `lpcr.ivory` no rato...). Com a chave so do destino, a primeira desenhada
 * responde por todas: o orc ficava verde porque recebia o bitmap do porco,
 * cujo recolor `light -> light` nao muda pixel nenhum.
 */
describe("chaveDoRecolor", () => {
  test("origens diferentes para o mesmo destino sao bitmaps diferentes", () => {
    const orc = [{ material: "body", paleta: "ulpc", cor: "light", base: "ulpc.green" }];
    const porco = [{ material: "body", paleta: "ulpc", cor: "light", base: "ulpc.light" }];
    expect(chaveDoRecolor(orc)).not.toBe(chaveDoRecolor(porco));
  });

  test("a mesma transformacao da a mesma chave -- o cache tem de servir", () => {
    const a = [{ material: "body", paleta: "ulpc", cor: "light", base: "ulpc.green" }];
    const b = [{ material: "body", paleta: "ulpc", cor: "light", base: "ulpc.green" }];
    expect(chaveDoRecolor(a)).toBe(chaveDoRecolor(b));
  });

  test("distingue pela cor embutida quando nao ha `base`", () => {
    const um = [{ material: "cloth", paleta: "ulpc", cor: "red", fonte: ["#111111", "#222222"] }];
    const outro = [{ material: "cloth", paleta: "ulpc", cor: "red", fonte: ["#333333", "#444444"] }];
    expect(chaveDoRecolor(um)).not.toBe(chaveDoRecolor(outro));
  });

  test("todos os canais entram: trocar so o segundo muda a chave", () => {
    const azul = [
      { material: "body", paleta: "ulpc", cor: "light", base: "ulpc.light" },
      { material: "eye", paleta: "ulpc", cor: "blue", base: "ulpc.blue" },
    ];
    const verde = [
      { material: "body", paleta: "ulpc", cor: "light", base: "ulpc.light" },
      { material: "eye", paleta: "ulpc", cor: "green", base: "ulpc.blue" },
    ];
    expect(chaveDoRecolor(azul)).not.toBe(chaveDoRecolor(verde));
  });
});

/**
 * Pedido literal do dono: "ordenasse as cores por gradiente [...] tipo, td q e
 * verde fica junto e vai meio q por degrade as demais". Filtrar por nome nao
 * resolve -- os nomes das rampas do LPC nao descrevem a cor (`ivory`,
 * `porcelain`, `lpcr`), entao a unica pista confiavel e o pixel.
 */

const chaves = (l: Amostra[]) => l.map(([k]) => k);

describe("ordenarPorMatiz", () => {
  test("junta o que e do mesmo matiz, mesmo separado na entrada", () => {
    const entrada: Amostra[] = [
      ["verde-claro", "#88ff88"],
      ["vermelho", "#ff0000"],
      ["verde-escuro", "#004400"],
    ];
    // os dois verdes tem de sair vizinhos: o vermelho nao pode ficar no meio
    const saida = chaves(ordenarPorMatiz(entrada));
    const i = saida.indexOf("verde-claro");
    const j = saida.indexOf("verde-escuro");
    expect(Math.abs(i - j)).toBe(1);
  });

  test("dentro do matiz vai do escuro ao claro -- o degrade", () => {
    const entrada: Amostra[] = [
      ["medio", "#008800"],
      ["claro", "#88ff88"],
      ["escuro", "#002200"],
    ];
    expect(chaves(ordenarPorMatiz(entrada))).toEqual(["escuro", "medio", "claro"]);
  });

  test("comeca no vermelho e segue a roda: vermelho, verde, azul", () => {
    const entrada: Amostra[] = [
      ["azul", "#0000ff"],
      ["verde", "#00ff00"],
      ["vermelho", "#ff0000"],
    ];
    expect(chaves(ordenarPorMatiz(entrada))).toEqual(["vermelho", "verde", "azul"]);
  });

  test("cor sem matiz -- cinza, branco, preto -- vai para o fim", () => {
    const entrada: Amostra[] = [
      ["cinza", "#808080"],
      ["vermelho", "#ff0000"],
      ["branco", "#ffffff"],
    ];
    const saida = chaves(ordenarPorMatiz(entrada));
    expect(saida[0]).toBe("vermelho");
    // e os acromaticos tambem em degrade entre si
    expect(saida.slice(1)).toEqual(["cinza", "branco"]);
  });

  test("nao perde nem inventa cor", () => {
    const entrada: Amostra[] = [
      ["a", "#ff0000"], ["b", "#00ff00"], ["c", "#0000ff"],
      ["d", "#808080"], ["e", "#123456"], ["f", "#fedcba"],
    ];
    const saida = ordenarPorMatiz(entrada);
    expect(saida).toHaveLength(entrada.length);
    expect([...chaves(saida)].sort()).toEqual(["a", "b", "c", "d", "e", "f"]);
  });

  test("hex torto nao derruba a lista", () => {
    const entrada: Amostra[] = [
      ["boa", "#ff0000"],
      ["torta", "nao-e-hex"],
      ["vazia", ""],
    ];
    const saida = ordenarPorMatiz(entrada);
    expect(saida).toHaveLength(3);
    expect(chaves(saida)).toContain("boa");
  });

  test("mesma entrada em ordem diferente da a mesma saida", () => {
    const a: Amostra[] = [["x", "#ff0000"], ["y", "#ff0202"], ["z", "#00ff00"]];
    const b: Amostra[] = [["z", "#00ff00"], ["y", "#ff0202"], ["x", "#ff0000"]];
    expect(chaves(ordenarPorMatiz(a))).toEqual(chaves(ordenarPorMatiz(b)));
  });
});
