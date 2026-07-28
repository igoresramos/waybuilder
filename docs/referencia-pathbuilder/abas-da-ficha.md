# Pathbuilder 2e — Referência de UI das Abas da Ficha

Personagem de referência: Fighter nível 1, "Unknown Adventurer", recém-criado (Human, background Barkeep). Capturas em `capturas/06-aba-*.png`.

## Layout comum (contexto, não repetir por aba)

- Barra superior escura: hamburger "Menu" + nome/nível do personagem ("X Unknown Adventurer - Fighter 1").
- Faixa de cabeçalho da ficha: bloco "Hide Plan" / Level / XP / Character Name à esquerda; bloco de atributos (SIZE, SPEED, STR/DEX/CON/INT/WIS/CHA) abaixo; à direita botões globais "Rest", "Add Condition", "Add Custom Buff" (este último desabilitado, cinza).
- Logo abaixo: cartão de AC (escudo laranja grande "14") + campo HP + campo de escudo equipado ("No Shield") + coluna de saves (Fortitude, Reflex, Will) com badge de proficiência (círculo laranja "E"=Expert, "T"=Trained).
- Coluna esquerda (~370px): construção nível a nível (Ancestry, Background, Class, blocos "Level 1", "Level 2"...).
- Coluna de perícias (~194px), abaixo de "Hero Points" e "Fighter DC": Perception, Initiative, e lista alfabética de perícias com badge de proficiência (U=Untrained cinza, T=Trained laranja, E=Expert) e modificador.
- Barra de abas horizontal, laranja quando ativa, cinza quando inativa: Weapons | Defense | Gear | Spells | Pets | Details | Feats | Actions. Uma linha laranja fina sublinha toda a barra.
- Área de conteúdo da aba: painel(éis) com fundo cinza-azulado escuro, cantos levemente arredondados, sobre o fundo ainda mais escuro da página.
- Ícone de dado d20 laranja fixo no canto inferior direito da tela (provável atalho de rolagem), presente em todas as abas.

---

## Weapons

1. Um único painel largo no topo da área de conteúdo, sem colunas internas.
2. Cabeçalho: quatro badges de proficiência em linha — "Simple Weapons", "Martial Weapons", "Advanced Weapons", "Unarmed Attacks" — cada uma com círculo colorido (E laranja para Simple/Unarmed = Expert, T cinza-azulado para Martial/Advanced = Trained) e o valor numérico ao lado do rótulo.
3. Botões de ação: "Add Weapon" e "Print", lado a lado, alinhados à esquerda logo abaixo dos badges.
4. Item de lista: não há nenhuma arma equipada nesta captura (estado vazio), então o padrão de item individual não é visível aqui — presumir que apareceria abaixo dos botões.
5. Estado vazio: painel some direto para o fundo, sem placeholder textual "nenhuma arma" — só os badges de proficiência e os dois botões. Vazio = ausência de conteúdo, não mensagem.
6. Cor: badges "E" em laranja (proficiência mais alta/relevante), badge "T" (Martial/Advanced) em cinza-azulado neutro. Botões com borda cinza-clara e fundo transparente/escuro, texto branco.

## Defense

1. Dois painéis empilhados: (a) resumo de proficiências em armadura + ações; (b) armadura/escudo atualmente equipados, cada um como sub-bloco com sua própria linha de botões.
2. Cabeçalho do painel 1: quatro badges de proficiência — "Light Armor", "Medium Armor", "Heavy Armor", "Unarmored" (todos "T" = Trained, laranja). Linha logo abaixo com o cálculo do AC: "Base 10 · Item +0 · Dex +1 · Proficiency +3".
3. Botões: no painel 1 — "Stow Additional Armor", "Stow Additional Shield", "Print". No sub-bloco de armadura equipada — "Change", "Options", "Runes", "Stow". No sub-bloco de escudo — apenas "Change".
4. Item de armadura equipada ("Unarmored"): nome à esquerda; ao centro/direita ícones com valores — "Item Bonus +0" (ícone de escudo) e "Dex Cap -1" (ícone de seta para cima). Item de escudo: apenas texto "No Shield", sem stats (porque não há escudo).
5. Estado vazio: não existe estado "sem armadura" — o personagem sempre tem ao menos "Unarmored" como slot ativo, mostrado como um card completo com botões de ação. O escudo mostra "No Shield" como texto simples abaixo do botão "Change", sem stats.
6. Cor: badges "T" em laranja. Rótulos de stats (Item Bonus, Dex Cap) em cinza claro com ícone; valores em branco.

## Gear

1. Um painel superior de recursos (moedas + bulk) e, abaixo, um painel de inventário rotulado.
2. Cabeçalho do painel superior: quatro "moedas" em card retangular — Platinum, Gold (15), Silver, Copper — cada uma com ícone circular colorido (platina cinza-claro, ouro amarelo, prata cinza, cobre marrom) e valor abaixo do rótulo. Linha central: "Total Bulk 0" e "Unencumbered (Enc: 8; Max: 13)".
3. Botões: "Add Gear", "Add Container", "Add Formula", "Print" — quatro em linha, centralizados sob o resumo de moedas/bulk.
4. Abaixo, painel separado com título em laranja "Main Inventory" — vazio, sem itens listados (não há padrão de item de gear visível nesta captura).
5. Estado vazio: painel "Main Inventory" existe como cabeçalho de seção mas fica em branco por baixo — nenhum placeholder tipo "nenhum item", só o título.
6. Cor: ícones de moeda com cor temática própria (não laranja-padrão do app); "Main Inventory" em laranja (rótulo de seção); valores numéricos em branco.

## Spells

1. Um único painel com um cabeçalho de seção e botões de ação — o mais minimalista das abas vistas.
2. Cabeçalho de seção em laranja: "Rituals" (com linha divisória fina abaixo, mesmo padrão da barra de abas).
3. Botões: "Add Ritual" e "Print", lado a lado, centralizados dentro do painel abaixo do título.
4. Nenhum item de lista presente para descrever o padrão (personagem Fighter não tem magias).
5. Estado vazio: apenas o título de seção + os dois botões; nenhuma lista de spell slots, tradições ou spellcasting visível — condizente com uma classe não-caster. Sugere que outras seções (Cantrips, Spell Slots por nível, tradições) só apareceriam se a classe tivesse spellcasting.
6. Cor: título "Rituals" em laranja; resto em cinza/branco padrão.

## Pets

1. Painel único, de conteúdo mínimo: uma única linha de aviso.
2. Sem cabeçalhos de seção nem rótulos de dados.
3. Nenhum botão de ação visível (nem "Add Pet" nem "Print") — a aba está totalmente bloqueada.
4. N/A — não há itens.
5. Estado vazio: mensagem textual explícita de paywall — "Animal Companions, Eidolons, Constructs and Familiars are only available in the fully unlocked version of this app." Este é o único caso, entre as oito abas, em que o vazio é comunicado com texto explicativo em vez de apenas ausência de conteúdo + botão de adicionar.
6. Cor: texto em branco/cinza-claro padrão, sem destaque em laranja — não é tratado como alerta, é um aviso neutro.

## Details

1. Dois painéis empilhados: (a) bloco de identidade/retrato + campos, (b) bloco de notas em texto livre.
2. Sem cabeçalhos de seção com título (diferente de "Rituals" ou "Main Inventory") — os rótulos ficam junto de cada campo.
3. Botão de ação: "Save Notes", no topo do painel de notas, alinhado à esquerda.
4. Layout do painel 1: retrato/avatar placeholder (silhueta cinza de pessoa, com ícone de câmera/editar no canto) ocupa a lateral esquerda; à direita, grade de campos rotulados — "Deity" (linha cheia), depois "Age" e "Gender" lado a lado, depois "Languages" (linha cheia). Cada campo mostra rótulo cinza pequeno em cima e valor "Not set" / "None selected" em branco abaixo, dentro de um retângulo com borda.
5. Estado vazio: cada campo mostra explicitamente "Not set" ou "None selected" como placeholder de valor (não fica em branco puro) — padrão diferente das outras abas, mais próximo de formulário. Notas: área de texto vazia sob o rótulo "Notes", sem placeholder textual.
6. Cor: rótulos de campo em cinza; valores "Not set"/"None selected" em branco (leem como valor real de texto, não itálico/diferenciado); ícone de avatar cinza neutro.

## Feats

1. Painel de avisos no topo + dois painéis lado a lado (2 colunas) para as categorias de feats.
2. Cabeçalhos de seção em laranja: "General Feats", "Skill Feats" (coluna esquerda) e "Specials" (coluna direita).
3. Botões: dois botões "Print" idênticos, um no topo de cada coluna (esquerda e direita), acima dos respectivos cabeçalhos de seção.
4. Item de lista: nome do feat em branco à esquerda, com um ícone de seta (↗) à direita do nome quando o feat tem uma ação associada (ex.: "Shield Block ↗", "Reactive Strike ↗"); "Hobnobber" aparece sem seta. Indentado sob o cabeçalho da sua categoria.
5. Estado vazio/parcial: painel de avisos no topo lista pendências em texto simples com marcador "•" — "You have not yet assigned level 1 ability boosts in your character plan." e "You have 3 unselected feats up to this level in your character plan." Mesmo com feats pendentes, os feats já concedidos (free feats) aparecem normalmente nas colunas.
6. Cor: cabeçalhos de seção (General Feats, Skill Feats, Specials) em laranja; itens de feat em branco; setas de ação em branco.

## Actions

1. A aba mais densa: um painel de filtros/busca no topo e, abaixo, uma lista longa de ações em duas colunas (nome à esquerda, categoria à direita), sem separação visual em cards — é uma tabela implícita.
2. Sem cabeçalho de seção com título; a "seção" é definida pelos checkboxes de filtro.
3. Botão de ação: "Print", único, canto superior esquerdo do painel de filtros.
4. Linha de filtro: checkboxes com rótulo — "Class", "Skills", "Gear", "Basic", "Exploration", "Downtime / Activity" — cada um com um ícone de tipo de ação ao lado (losango = free action, seta = single action, seta dupla = duas ações). Abaixo, campo de busca "search" (placeholder) e dropdown "Names" à direita.
5. Item de lista: nome da ação à esquerda (ex.: "Administer First Aid (Medicine)"), ícone de custo de ação logo após o nome quando aplicável (losango/seta/setas duplas), e a categoria da ação alinhada à direita da mesma linha (ex.: "Skill (Medicine)", "Basic", "Exploration"). Não há bordas entre linhas — só espaçamento vertical.
6. Estado vazio: não aplicável — esta lista vem do compêndio de regras (sempre populada), não é uma lista de itens do personagem.
6b. Cor: nomes de ação em branco/azul-claro (parecem clicáveis); categorias à direita em laranja; ícones de custo de ação em branco.

---

## Padrões transversais

- **Barra de abas**: sempre as mesmas 8 abas na mesma ordem (Weapons, Defense, Gear, Spells, Pets, Details, Feats, Actions); aba ativa em laranja com sublinhado, inativas em cinza.
- **Botão "Print"**: presente em praticamente toda aba com conteúdo do personagem (Weapons, Defense, Gear, Spells, Feats) — sempre com borda simples, canto do painel, para exportar/imprimir aquela seção.
- **Botões "Add X"**: padrão consistente de botão de borda fina, fundo escuro, texto branco, para criar novo item (Add Weapon, Add Gear, Add Container, Add Formula, Add Ritual). Ficam agrupados perto do topo do painel, antes de qualquer listagem.
- **Cabeçalhos de seção em laranja**: qualquer rótulo de bloco/categoria (Rituals, Main Inventory, General Feats, Skill Feats, Specials) usa a cor de destaque laranja do app — mesma cor da aba ativa e do AC.
- **Badges de proficiência**: círculo colorido + letra (U/T/E/M) reaparece tanto na coluna de perícias quanto nos cabeçalhos de Weapons e Defense — é o componente central de "nível de treino" no app inteiro. Laranja = nível mais alto disponível/relevante; cinza-azulado = nível mais baixo (Trained/Untrained conforme contexto).
- **Estado vazio é maioria "silencioso"**: a maior parte das abas (Weapons, Gear, Spells) não escreve nenhuma mensagem "vazio" — simplesmente omite a listagem e deixa só cabeçalho + botões de ação. Só duas exceções: Pets (mensagem de paywall) e Feats (avisos de pendência de build). Details usa "Not set"/"None selected" como valor de placeholder por campo, não como aviso de seção.
- **Ícones inline**: setas (↗ ação simples, ↗↗ duas ações, ◇ free action) aparecem tanto em Feats quanto em Actions para indicar custo/tipo de ação — reaproveitado como vocabulário visual comum de PF2e.
- **Sem paginação/scroll interno visível**: cada painel de conteúdo cresce livremente dentro da área direita; não há abas dentro de abas nem cards colapsáveis nas capturas vistas (exceto os sub-blocos "Change/Options/Runes/Stow" em Defense).
- **Estrutura de duas/uma coluna conforme densidade**: abas com poucas categorias usam painel único de largura total (Weapons, Gear resumo, Spells, Pets); abas com categorias paralelas usam duas colunas lado a lado (Feats: General/Skill vs Specials); Actions usa uma "coluna dupla" por linha (nome | categoria) dentro de um único painel largo.
