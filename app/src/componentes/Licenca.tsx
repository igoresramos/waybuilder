/**
 * Atribuicao de licenca -- obrigatoria a partir do momento em que o app e
 * PUBLICADO, e nao antes.
 *
 * Enquanto rodava so na maquina do Igor isto nao se aplicava. Publicar e
 * redistribuir, e as duas licencas que cobrem a base exigem atribuicao:
 * medido, sao **13.105 registros ORC** e **7.020 OGL**, de 239 livros.
 * `LESSONS.md` ja registrava a regra ("regra sob OGL/ORC e reutilizavel com
 * atribuicao; arte e outra coisa") -- o que faltava era a tela cumpri-la.
 *
 * A ARTE FICA DE FORA, e por isso os icones do app sao desenhados a mao em
 * SVG: o EULA da arte da Paizo e de "exclusive use within that project", que
 * nao e licenca publica. Ver `Icones.tsx`.
 *
 * ATENCAO -- este texto e a atribuicao MINIMA e nao substitui revisao do
 * Igor. A OGL 1.0a exige reproduzir a licenca INTEIRA junto do material
 * derivado, e o texto integral nao esta aqui: ha um link para o oficial. Quem
 * decide o que basta e o dono do projeto, nao eu.
 */
import { useState } from "react";

const LIVROS = [
  "Player Core", "Player Core 2", "GM Core", "Monster Core",
  "Treasure Vault", "Secrets of Magic", "Rage of Elements", "Battlecry!",
  "Guns & Gears", "War of Immortals", "Divine Mysteries",
  "Tian Xia Character Guide", "Howl of the Wild",
];

export function Licenca() {
  const [aberto, setAberto] = useState(false);
  return (
    <>
      <button className="rodape-licenca" onClick={() => setAberto(true)}>
        Licencas e atribuicao
      </button>
      {aberto && (
        <div className="modal-fundo" onClick={() => setAberto(false)}>
          <div className="modal licenca" onClick={(e) => e.stopPropagation()}>
            <header><h2>Licencas e atribuicao</h2></header>
            <div className="licenca-corpo">
              <p>
                O Waybuilder e uma ferramenta nao oficial de construcao de
                personagem para <strong>Pathfinder Second Edition</strong>.
                Nao e afiliado nem endossado pela Paizo Inc.
              </p>

              <h3>ORC</h3>
              <p>
                Parte do conteudo de regras deste aplicativo
                (<strong>13.105 registros</strong>) e distribuida sob a{" "}
                <strong>ORC License</strong>, publicada pela Azora Law em nome
                da Paizo Inc. Material de Pathfinder usado sob a ORC; obras
                originais Paizo Inc.
              </p>

              <h3>OGL 1.0a</h3>
              <p>
                Outra parte (<strong>7.020 registros</strong>, conteudo
                pre-remaster) vem da{" "}
                <strong>Open Game License Version 1.0a</strong>. Open Game
                Content usado sob a OGL 1.0a; System Reference Document e
                material Pathfinder, Copyright Paizo Inc.
              </p>

              <h3>Livros de origem</h3>
              <p className="fraco">{LIVROS.join(" - ")} e outros. Cada
              registro carrega o livro e a licenca proprios, visiveis no
              detalhe do item.</p>

              <h3>Marcas e arte</h3>
              <p>
                Pathfinder e o logotipo Pathfinder sao marcas registradas da
                Paizo Inc. <strong>Nenhuma arte da Paizo e usada</strong> -- os
                icones deste app sao originais. Nomes proprios do cenario
                Golarion sao Product Identity e nao sao redistribuidos como
                conteudo aberto.
              </p>

              <p className="fraco">
                Textos integrais das licencas:{" "}
                <a href="https://paizo.com/orclicense" target="_blank" rel="noreferrer">
                  ORC
                </a>
                {" - "}
                <a href="https://paizo.com/pathfinder/compatibility/ogl" target="_blank" rel="noreferrer">
                  OGL 1.0a
                </a>
              </p>
            </div>
            <footer>
              <button className="aceitar" onClick={() => setAberto(false)}>
                fechar
              </button>
            </footer>
          </div>
        </div>
      )}
    </>
  );
}
