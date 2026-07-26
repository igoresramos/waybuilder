# Lost Omens (region/organization) -- flavor ou mecanica?

**Veredito:** Ha mecanica real amarrada a regiao/organizacao, mas ela ja esta quase toda carregada na base como feat/equipment/weapon/armor normais. O que falta nao e "texto de ambientacao" -- e a estrutura do campo `requires` para checar programaticamente afiliacao/origem, que hoje fica presa em prosa (`requires_texto` ou texto bruto) com `requires: null`. Nao recomendo criar `kind: region`/`kind: organization` para carregar capitulos de historia/geografia/cultura (isso e flavor puro, confirmado por amostragem). Recomendo, como item separado e bem menor, criar stubs leves de referencia (id + nome, sem prosa) para as organizacoes/regioes que ja aparecem como pre-requisito/access em ~300 registros existentes, e estender o schema de `requires` para referencia-los -- so vale a pena se o Igor quiser que o builder efetivamente bloqueie/libere esses feats e itens por afiliacao, hoje isso e so texto informativo.

## Metodo

1. Varredura estrutural de `pipeline/base/index.json` (18.176 registros) e dos textos completos em `pipeline/base/text/*.json`.
2. Amostragem de 3 PDFs indicados: *Pathfinder Society Guide* (130 pag.), *The Mwangi Expanse* (314 pag.), *Impossible Lands* (346 pag.). Todos com fontes embutidas (nao sao scan), `pdftotext -layout` funcionou em faixas.
3. Cruzamento: para cada pre-requisito/"Access" que cita organizacao/regiao/etnia encontrado nos PDFs, verifiquei se o feat/item correspondente ja existe na base e se o campo `requires` estruturado captura a condicao.

## Evidencia -- a mecanica ja existe na base, mas nao esta estruturada

### 1. O schema de `requires` nao tem vocabulario para organizacao/regiao

Levantei todas as chaves usadas em `requires` nos 3.540 registros que tem esse campo preenchido:

```
ability, acrobatics, all, any, arcana, athletics, [pericias], cha/con/dex/int/str/wis,
class_level, has, lore:*, proficiency, spell-attack, spell-dc, spellcasting_tradition,
trait, weapon:*, [classes: barbarian, bard, ...]
```

`trait` existe, mas se refere a tracos de criatura/ancestria (`goblin`, `fleshwarp`, `holy`, `unholy`), nunca a organizacao ou regiao. Nao ha `organization`, `region`, `membership` ou `origin` em lugar nenhum do schema.

### 2. Dezenas de feats ja na base tem pre-requisito textual de organizacao/regiao, sem checagem estruturada

68 registros de `kind: feat`/`archetype` tem a string "member of", "you are from" ou "ethnicity" dentro de `requires_texto` (o campo de pre-requisito em prosa) -- e em todos eles `requires` (o campo estruturado, que o builder de fato usa) e `null` ou nao cobre essa parte. Exemplos reais:

- `wb:feat/pathfinder-agent-dedication` -- `requires_texto: "member of the Pathfinder Society"`, `requires: null`
- `wb:feat/hellknight-armiger-dedication` -- `requires_texto: "member of a Hellknight order..."`, `requires: null`
- `wb:feat/red-mantis-assassin-dedication` -- `requires_texto: "...member of the Red Mantis assassins"`, `requires: null`
- `wb:feat/ulfen-guard-dedication` -- `requires_texto: "member of the Ulfen Guard..."`, `requires: null`
- `wb:feat/wylderheart-dedication` -- `requires_texto: "member of the Wylderhearts"`, `requires: null`
- `wb:feat/share-thoughts` -- `requires: {"trait": ...}` nao usado aqui; pre-requisito real e "Mualijae ethnicity, Ilverani ethnicity, or Vourinoi ethnicity" (nomes de subculturas elficas do Impossible Lands), sem representacao estruturada
- `wb:feat/shory-aeromancer` -- pre-requisito "Garundi ethnicity, Mauxi ethnicity, or Tian-Yae ethnicity"

### 3. Alem de "Prerequisites", o PDF usa uma linha separada "Access" (regra de raridade uncommon/rare) que tambem cita organizacao/regiao -- e essa linha nao e parseada em NENHUM kind

Busquei a linha "Access" nos textos completos (`text/*.json`) de todos os kinds e contei quantos registros ja presentes na base tem esse "Access" citando organizacao, regiao ou etnia:

| Kind | Registros com Access gate por org/regiao |
|---|---|
| equipment | 155 |
| feat | 134 |
| weapon | 13 |
| armor | 3 |
| **Total** | **305** |

Nenhum desses 305 tem isso capturado em campo estruturado -- `equipment`, `weapon` e `armor` nem tem `requires_texto` (esse campo so existe em `feat`/`archetype`, 3.973 e 201 registros respectivamente). Para esses kinds a unica pista e a prosa dentro do blob de texto. Exemplos confirmados na base:

- `wb:equipment/body-recovery-kit` (Envoy's Alliance Gear, PFS Guide pg. 26) -- texto completo diz `Access Membership in the Envoy's Alliance Pathfinder Society faction` e ainda cita a regra de Organized Play: *"Players can gain access to faction-specific gear by taking the corresponding Faction Gear Access Game Reward, available when they reach 20 reputation with the respective faction."* -- `requires: null`, `rarity: uncommon`. Isso e mecanica real (gate de reputacao/facção), zero estruturada.
- `wb:weapon/lions-call`, `wb:weapon/stiletto-pen` -- ambas `rarity: uncommon`, `requires: null`, mas o texto diz "member of the Lion Blades" / "Member of the Pathfinder Society"
- `wb:equipment/aeon-stone-agate-ellipsoid` e variantes -- todas "Access Member of the Pathfinder Society", sem campo estruturado

O trecho da PFS Guide (pg. 120, secao "Secrets of the Pathfinder Society") deixa a regra explicita: *"All characters affiliated with the Pathfinder Society have access to the uncommon options in this section."* -- isto e uma regra de acesso a conteudo uncommon via filiacao, exatamente o criterio "conta como mecanica" do briefing.

### 4. O conteudo mecanico dos capitulos de regiao/organizacao ja esta quase todo importado -- so faltam alguns itens pontuais

Testei a hipotese "sera que o kind novo seria so pra guardar o item que falta" contra listas de item/feat/archetype citados nos 3 PDFs amostrados. Resultado: a esmagadora maioria ja esta na base (feats de faccao, backgrounds de origem, archetypes, animal companions, armas exclusivas). Confirmei presenca de:

- `wb:background/bright-lion` (Bright Lion background, World Guide)
- `wb:archetype/shieldmarshal`, `wb:feat/shieldmarshal-dedication`, `wb:weapon/triggerbrand*`, `wb:equipment/alkenstar-ice-wine`, `wb:equipment/plated-duster`, `wb:equipment/pocket-watch`, `wb:equipment/wrenchgear`, `wb:animal-companion/water-wraith` (todos do capitulo "Adventuring in Alkenstar", Impossible Lands pg. 106-108, secao que tambem usa a mesma regra "Characters from Alkenstar have access to the uncommon options in this section")

Gaps pontuais encontrados (nao relacionados ao kind region/organization, sao so registros de equipment faltando):
- `Elemental Wayfinder`, `Homeward Wayfinder`, `Hummingbird Wayfinder`, `Fashionable Wayfinder` (PFS Guide pg. 120-122) -- ausentes da base
- `Triggerbrand Salvo` (feat, Impossible Lands pg. 108) -- ausente da base

Esses sao itens/feats individuais faltando no pipeline de ingestao normal (kind `equipment`/`feat`), nao uma lacuna que "region"/"organization" resolveriam.

## O que e flavor puro (confirmado por amostragem)

Amostrei o capitulo "People of the Mwangi" (Alijae, Mwangi Expanse pg. 32-41): historia, religiao, geografia da cidade, politica de faccoes internas -- nada disso e mecanica. O unico ponto de contato com regras e um quadro "Alijae Characters" que **sugere** heranças/feats existentes ("Alijae elves often have the woodland elf or seer elf heritage... often have the Know Your Own and Elven Lore ancestry feats") -- isso e recomendacao de interpretacao, nao pre-requisito. Bate exatamente com o criterio "Nao conta" do briefing.

Da mesma forma, os capitulos de Geografia (Bandu Hills, Mwangi Jungle, etc.) e as fichas de cidade (Bloodcove, Jaha, Kibwe...) sao descricao de lugar/cultura/NPC sem efeito de regra sobre personagem -- e alem disso sao conteudo de mestre (geografia, hazards), fora do escopo de um construtor de personagem, que nao tem sequer um `kind: hazard`.

## Recomendacao

1. **Nao criar `region`/`organization` para importar os capitulos de ambientacao dos livros Lost Omens.** Confirmado: e flavor (historia, geografia, cultura, NPCs, sugestao de interpretacao).
2. **Ha uma lacuna real e diferente da proposta original**: ~305 registros ja presentes na base (feat/equipment/weapon/armor) dependem de afiliacao a organizacao ou origem regional/etnica como pre-requisito de acesso a conteudo uncommon/rare, e isso hoje e so texto solto (`requires: null`). Se o Igor quiser que o Waybuilder efetivamente valide isso (em vez de so mostrar o texto), o trabalho e:
   - Criar stubs minimos de `kind: organization`/`kind: region` -- so `id` + `name` (sem prosa de ambientacao), cobrindo as ~20-25 entidades que aparecem como pre-requisito real (Pathfinder Society + faccoes, Red Mantis Assassins, Hellknight Orders, Eagle Knights, Bellflower Network, Ulfen Guard, Knights of Lastwall, Wylderhearts, etc.; Absalom, Mwangi Expanse, Ustalav, Kyonin, Isger, Alkenstar, Jalmeray, etnias como Garundi/Mauxi/Mualijae/Ilverani/Vourinoi).
   - Estender o schema de `requires` com uma chave tipo `organization`/`region` referenciando esses ids.
   - Isso e trabalho de retrofit em cima do que ja existe, nao de importacao de novo conteudo -- e um escopo bem menor que a proposta original.
3. Preencher os poucos itens faltando identificados (4 wayfinders da PFS Guide, Triggerbrand Salvo) via ingestao normal de `equipment`/`feat`, sem relacao com kinds novos.

## Amostra e limites

Analisei estruturalmente toda a base (18.176 registros). Nos PDFs, li integralmente 3 livros indicados como amostra (nao os 10 books de Lost Omens da base) mais trechos direcionados de Impossible Lands (introducao + "Adventuring in Alkenstar"). Achados de itens faltando (wayfinders, Triggerbrand Salvo) sao pontuais dessa amostra -- pode haver mais gaps de equipment em livros nao verificados aqui, isso nao foi objeto desta analise.
