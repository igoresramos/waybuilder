/**
 * A prosa de um registro, em partes -- regra separada de sabor.
 *
 * O texto das fontes chega como um paragrafo unico com tudo dentro, e nele o
 * jogador nao acha o que precisa: o gatilho da reacao fica no meio da frase, e
 * numa ancestralidade a descricao de folclore ocupa dez vezes o espaco da
 * mecanica. Aqui a ordem e a de quem esta montando ficha:
 *
 *   1. os campos curtos (Trigger, Requirements, Frequency) -- o que decide se
 *      da para usar;
 *   2. o efeito e os graus de sucesso -- a regra;
 *   3. a fantasia, RECOLHIDA. Ela nao some, porque e metade da graca de
 *      escolher uma ancestralidade; ela so nao ocupa a tela de quem esta
 *      comparando dois feats.
 *
 * O criterio nao e nosso: sai dos rotulos que a Paizo usa (`You Might`,
 * `Physical Description`, `Society`...), que aparecem em 50 das 50
 * ancestralidades.
 */
import { useState } from "react";
import { analisarProsa, type Secao } from "../prosa";
import { limparMarcacao } from "../marcacao";

function Bloco({ s }: { s: Secao }) {
  return (
    <p className={`bloco-prosa ${s.tipo}`}>
      {s.rotulo && <b className="rotulo-bloco">{s.rotulo}</b>}
      {limparMarcacao(s.texto)}
    </p>
  );
}

export function Prosa({ texto, nome }: { texto: string; nome?: string }) {
  const [verSabor, setVerSabor] = useState(false);
  const p = analisarProsa(texto, nome);

  // nada a separar: melhor o texto cru do que uma casca vazia em volta dele
  if (p.cru && !p.campos.length) {
    return <div className="prosa">{limparMarcacao(texto)}</div>;
  }

  return (
    <div className="prosa">
      {p.campos.length > 0 && (
        <div className="campos-de-regra">
          {p.campos.map((c, i) => (
            <div key={i} className="campo">
              <b>{c.rotulo}</b>
              <span>{limparMarcacao(c.texto)}</span>
            </div>
          ))}
        </div>
      )}

      {p.regra.map((s, i) => <Bloco key={`r${i}`} s={s} />)}

      {p.sabor.length > 0 && (
        <div className="sabor">
          <button className="link" onClick={() => setVerSabor(!verSabor)}
                  aria-expanded={verSabor}>
            {verSabor ? "esconder" : "ler"} a descricao
            <span className="conta"> ({p.sabor.length})</span>
          </button>
          {verSabor && p.sabor.map((s, i) => <Bloco key={`s${i}`} s={s} />)}
        </div>
      )}

      {p.fonte && <p className="fonte">{p.fonte}</p>}
    </div>
  );
}

/** O custo em acoes, para a tela por ao lado do nome. */
export function custoDeAcao(texto: string, nome?: string): string | null {
  return analisarProsa(texto, nome).custoDeAcao;
}
