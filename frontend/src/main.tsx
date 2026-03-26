import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ApiProvider } from './api'
import { UserProvider } from './contexts'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from './contexts/ToastContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ApiProvider>
      <UserProvider>
        <QueryClientProvider client={new QueryClient()}>
          <ToastProvider>
            <App />
          </ToastProvider>
        </QueryClientProvider>
      </UserProvider>
    </ApiProvider>
  </StrictMode>,
)
