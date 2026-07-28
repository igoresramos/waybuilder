/**
 * Lista virtualizada -- so o que cabe na tela vira DOM.
 *
 * O picker de Free Archetype tem 2.128 feats e o de equipamento 6.122 itens.
 * Renderizar tudo cria milhares de <button> a cada tecla digitada na busca, e a
 * digitacao passa a engasgar num app cujo motor deriva a ficha inteira em
 * 0,30 ms -- o gargalo seria a lista, nao a regra.
 *
 * Sem biblioteca: a linha tem altura fixa, entao a conta e uma divisao. Uma
 * dependencia a mais custaria mais que as trinta linhas daqui.
 *
 * Isto NAO e paginacao e nao esconde nada: a barra de rolagem tem o tamanho da
 * lista inteira e qualquer item e alcancavel rolando -- o principio zero do
 * projeto continua valendo.
 */
import { useState, type ReactNode } from "react";

const ALTURA = 30;   // altura da linha, casada com o CSS de .modal-lista li
const BUFFER = 8;    // linhas extras acima e abaixo, para o scroll rapido

export function ListaVirtual<T>({
  itens, altura, children, className, vazio,
}: {
  itens: T[];
  /** altura visivel do container, em px */
  altura: number;
  children: (item: T, indice: number) => ReactNode;
  className?: string;
  vazio?: ReactNode;
}) {
  const [topo, setTopo] = useState(0);

  if (!itens.length) {
    return <ul className={className}>{vazio}</ul>;
  }

  const primeiro = Math.max(0, Math.floor(topo / ALTURA) - BUFFER);
  const visiveis = Math.ceil(altura / ALTURA) + BUFFER * 2;
  const ultimo = Math.min(itens.length, primeiro + visiveis);
  const janela = itens.slice(primeiro, ultimo);

  return (
    <ul className={className} onScroll={(e) => setTopo(e.currentTarget.scrollTop)}>
      {/* espacadores mantem a barra de rolagem do tamanho da lista inteira */}
      <li style={{ height: primeiro * ALTURA }} aria-hidden />
      {janela.map((item, i) => children(item, primeiro + i))}
      <li style={{ height: (itens.length - ultimo) * ALTURA }} aria-hidden />
    </ul>
  );
}
