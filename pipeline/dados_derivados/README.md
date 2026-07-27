# dados_derivados/

Artefato **derivado a mao** -- lido, conferido ou arbitrado por uma pessoa a
partir de uma fonte que nenhum script alcanca. Vai para o git, sempre.

## Por que este diretorio existe

`dados_brutos/` esta no `.gitignore` com a justificativa "reconstruiveis pelos
pins registrados na spec". Isso e verdade para o clone do Foundry
(`buscar_fontes.sh`) e para o dump do AoN (`dump_aon.py`). Era **falso** para
`tabelas_conjuracao_pdf.json`, que foi gravado la por engano e se perdeu.

Aquele arquivo continha as tabelas de conjuracao lidas dos PDFs oficiais. O
War of Immortals e um PDF imagem-only, sem camada de texto: as paginas foram
renderizadas com `pdftoppm` e as tabelas lidas a olho. Nao ha pin, script nem
comando que reproduza isso. Estava num diretorio ignorado, sumiu em silencio, e
o `TODO.md` seguiu marcando o item como CONCLUIDO.

## A regra

| Onde | O que | Versionado |
|---|---|---|
| `dados_brutos/` | dump de fonte, reproduzivel por script a partir de um pin | nao |
| `dados_derivados/` | tudo que exigiu leitura, julgamento ou arbitragem humana | **sim** |

Na duvida, pergunte: **existe comando que refaz isso sozinho?** Se a resposta
for nao, o arquivo pertence aqui.

## Portao 8

`portoes.py` verifica que todo caminho citado em documento versionado existe no
disco, exceto os que estao sob uma raiz reconstruivel. Perda nova quebra o
build; perda ja conhecida fica registrada em `artefatos_perdidos.json`, com
motivo e decisao pendente -- visivel, nunca silenciosa.
