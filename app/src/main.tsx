import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import { Avatar } from './componentes/Avatar.tsx'

/**
 * Rota de dev do avatar -- `#/avatar` (spec, passo 3 da ordem).
 *
 * A escolha e feita AQUI, antes de montar: dentro do `App` ela viraria um
 * return antes dos hooks, e mudar de rota sem recarregar quebraria o React
 * com "rendered fewer hooks than expected".
 *
 * Fica no proprio app, com o mesmo build e o mesmo versionamento (decisao 10):
 * a promocao a modal e mover um componente.
 */
const noAvatar = location.hash.startsWith('#/avatar')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {noAvatar ? (
      <main style={{ padding: 'var(--u)' }}>
        <h2 style={{ marginTop: 0 }}>Avatar (rota de dev)</h2>
        <Avatar />
      </main>
    ) : (
      <App />
    )}
  </StrictMode>,
)
