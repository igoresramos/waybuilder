# Waybuilder -- app

Construtor de personagem de Pathfinder 2e com a regra caseira de multiclasse.
PWA client-side: sem backend, sem conta, funciona offline.

## Rodar

```bash
./sincronizar-base.sh     # copia o payload de pipeline/base/app/ para public/
npm install
npm run dev
```

Se a base mudou, rode `../pipeline/build.sh` antes -- `sincronizar-base.sh` so
copia o que o pipeline ja emitiu.

## Como esta montado

```
src/
  motor/          porte de motor/motor.py para TypeScript
    tipos.ts      o CONTRATO -- escrito antes do porte, e o que a UI conhece
    base.ts       Base: por_id, resolver(), multiclasse()
    personagem.ts as 22 regras da casa
  doc.ts          o documento de personagem + localStorage + export/import
  carregarBase.ts busca o payload; nucleo na primeira carga, prosa sob demanda
  componentes/
    Picker.tsx    UM componente de escolha, reusado em todo slot
  telas/
    Ficha.tsx     a visao calculada
```

## As duas regras que a tela nao pode quebrar

**1. O documento e a unica fonte de verdade.** A UI edita `escolhas[]`; HP,
proficiencia, slot e pendencia sao derivados a cada mudanca e nunca guardados.
E o que faz mudanca de regra re-derivar em vez de invalidar ficha salva.

**2. Principio zero: o requisito sugere e ORDENA, nunca bloqueia.** O que nao
atende aparece na lista, marcado, com o motivo -- nunca escondido. O slot
filtra por TIPO (so feat de arquetipo entra no slot gratuito); o requisito so
ordena. Uma tela que escondesse o que nao atende quebraria a regra central do
projeto sem que ninguem percebesse: o motor continuaria certo e o app estaria
mentindo.

## O porte, e como se prova que esta certo

O motor Python tem 95 testes e foi validado contra os iconics da Paizo. O porte
nao e "traduzir e torcer":

1. `python3 ../motor/gerar_fixtures.py` congela as 20 fichas de exemplo com a
   visao inteira em `../motor/fixtures/`;
2. `npx vitest run` roda os MESMOS documentos no TS e compara campo a campo.

Divergencia e falha. O Python **continua existindo** depois do porte, como
oraculo: `validar_iconics.py`, o teste de carga e os nove portoes rodam nele.

## Carga

O nucleo -- os oito kinds que montam ficha -- e **510 KB gzip**. Equipamento,
magia e catalogo de referencia ficam em `por-kind/` e entram quando a tela que
os usa existir. A prosa (17,9 MB) e buscada por registro, nunca na carga
inicial.

## Fora da fatia 1

Inventario e runas, magia na ficha, companheiro, importar do Pathbuilder,
exportar PDF, niveis 5-20. Ver `../specs/2026-07-28-app-fatia-1.md`.
