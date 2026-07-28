import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

/**
 * Offline de verdade -- nao "funciona com cache do navegador se der sorte".
 *
 * O uso e mesa de jogo: pode nao ter rede, e o app tem de abrir. Como nao ha
 * backend, tudo que ele precisa sao arquivos estaticos, e o service worker
 * garante que estejam no dispositivo depois da primeira visita.
 *
 * `base: "./"` deixa o build funcionar servido de subpasta ou aberto direto do
 * disco -- e um app pessoal, nao um deploy.
 */
export default defineConfig({
  base: "./",
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        globPatterns: ["**/*.{js,css,html,json,webmanifest}"],
        // A PROSA FICA DE FORA DO PRE-CACHE. Sao 6,3 MB contra 4,2 MB do
        // nucleo: pre-cachear tudo faria a primeira visita baixar 10,9 MB para
        // mostrar uma tela que precisa de 4,2 -- e contra a razao de a prosa
        // viver em arquivo separado. Ela entra no cache quando o jogador abre
        // um registro, pela regra de runtime abaixo.
        globIgnores: ["**/base/text/**"],
        // NUNCA responder um pedido de dado com a pagina.
        //
        // O `navigateFallback` do plugin manda o `index.html` quando uma rota
        // nao esta no precache. Isso e certo para navegacao e VENENO para
        // `/base/`: o `fetch` recebe HTML, o `JSON.parse` estoura com
        // `Unexpected token '<', "<!doctype "...` e a tela diz "nao carregou a
        // base" -- um erro que nao aponta para lugar nenhum. Aconteceu com um
        // service worker de build anterior ainda registrado no navegador.
        navigateFallbackDenylist: [/^\/base\//],
        // o indice do nucleo passa de 2 MB cru, e o default do Workbox e 2 MiB:
        // sem isto o arquivo MAIS importante ficaria de fora, em silencio, e o
        // app abriria offline sem base nenhuma
        maximumFileSizeToCacheInBytes: 12 * 1024 * 1024,
        runtimeCaching: [
          {
            urlPattern: /\/base\/text\/.*\.json$/,
            // a prosa nao muda entre builds da mesma base: uma vez baixada,
            // serve do cache para sempre
            handler: "CacheFirst",
            options: {
              cacheName: "waybuilder-prosa",
              expiration: { maxEntries: 60 },
            },
          },
        ],
      },
      manifest: {
        name: "Waybuilder",
        short_name: "Waybuilder",
        description:
          "Construtor de personagem de Pathfinder 2e com multiclasse por nivel",
        theme_color: "#14161a",
        background_color: "#14161a",
        display: "standalone",
        start_url: "./",
      },
    }),
  ],
});
