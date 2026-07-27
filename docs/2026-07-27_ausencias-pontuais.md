---
projeto: waybuilder
tipo: verificacao
data: 2026-07-27
escopo: itens 18 e 23 do TODO -- ausencias pontuais reportadas contra o PDF
---

# Ausencias pontuais: o que era real e o que era premissa errada

Verificacao dos seis nomes que o TODO listava como ausentes da base, cada um
checado contra as tres fontes locais (dump do AoN, checkout do Foundry no pin,
pf2etools) e, onde precisou, contra o PDF oficial.

| nome reportado | veredito | evidencia |
|---|---|---|
| `Life-Saving Yowl` | **premissa errada -- o feat existe com outro nome** | Nenhuma fonte tem esse nome, e o PDF do Player Core 2 tambem nao. O feat de Catfolk que "da um uivo para trazer o aliado de volta da beira da inconsciencia" chama-se **Caterwaul**, FEAT 13 (reaction, auditory/concentrate/emotion/mental). O AoN confirma o par legado->remaster: `feat-1267` (Advanced Player's Guide) -> `feat-5564` (Player Core 2). Esta na base como `wb:feat/caterwaul`, nivel 13 |
| `Cavern Kobold` | **ausencia real** | `heritage-63` no AoN (Advanced Player's Guide), sem `remaster_id` -- nao foi renomeado, so nao foi extraido. O Foundry nao carrega a heranca legada (so aparece num pregen), e o extrator enumerava heritage a partir do Foundry |
| `Spellscale Kobold` | **ausencia real** | `heritage-65` no AoN (APG), mesmo caso do anterior |
| `Triggerbrand Salvo` | **presente** | esta na saida do extrator de feats |
| `Chronicler's Wayfinder`, `Spellsight Wayfinder`, `Sturdy Wayfinder` (PFS Guide) | **gap das fontes, nao do pipeline** | zero ocorrencias no dump do AoN e zero no checkout do Foundry. Nao ha o que extrair: entrariam so por digitacao manual do PFS Guide |

## O que isso muda

1. O item 18 do TODO cita `Life-Saving Yowl` como buraco de cobertura. Nao e:
   e um nome que nunca existiu em fonte nenhuma. **Nome citado de memoria nao e
   gabarito** -- so lista do proprio livro ou censo de fonte serve.
2. As duas herancas de kobold expoem uma falha de metodo maior que elas:
   **a enumeracao de `heritage` sai so do Foundry**, entao toda heranca legada
   que o Foundry nao carrega desaparece da base -- o que contraria o principio
   "nada e descartado". A correcao e enumerar tambem pelo AoN.
3. Os wayfinders do PFS Guide viram limite declarado de cobertura, nao pendencia
   em aberto: nenhuma das tres fontes cobre o PFS Guide.
