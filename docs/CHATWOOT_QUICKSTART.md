# Chatwoot - Início Rápido

## 1. Subir serviços

```bash
# Subir tudo
docker-compose up -d

# Ou só Chatwoot
docker-compose up -d postgres chatwoot chatwoot-sidekiq
```

## 2. Acessar e configurar

1. Abrir http://localhost:3001
2. Criar conta admin (primeiro acesso)
3. Settings → Inboxes → Add Inbox → Website
4. Copiar `websiteToken`

## 3. Integrar no React

### App.tsx

```typescript
import { ChatwootWidget } from './components/ChatwootWidget';

function App() {
  return (
    <>
      <ChatwootWidget websiteToken="SEU_TOKEN_AQUI" />
      {/* resto da app */}
    </>
  );
}
```

### Com usuário logado

```typescript
import { ChatwootWidget } from './components/ChatwootWidget';
import { useAuth } from './hooks/useAuth';

function App() {
  const { user } = useAuth();

  return (
    <>
      <ChatwootWidget
        websiteToken="SEU_TOKEN_AQUI"
        user={user ? {
          id: user.id,
          email: user.email,
          name: user.name
        } : undefined}
      />
      {/* resto da app */}
    </>
  );
}
```

### Controlar widget programaticamente

```typescript
import { useChatwoot } from './components/ChatwootWidget';

function SupportButton() {
  const { open } = useChatwoot();

  return (
    <button onClick={open}>
      Falar com Suporte
    </button>
  );
}
```

## 4. Variáveis de ambiente

### frontend/.env

```env
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=seu-website-token
VITE_CHATWOOT_BASE_URL=http://localhost:3001
```

## 5. Produção

### Gerar SECRET_KEY_BASE

```bash
docker-compose exec chatwoot bundle exec rake secret
```

Adicionar ao `.env`:
```env
CHATWOOT_SECRET_KEY_BASE=chave-gerada-aqui
CHATWOOT_FRONTEND_URL=https://chat.seudominio.com
```

## URLs

- Chatwoot: http://localhost:3001
- PostgreSQL: localhost:5432
- Frontend: http://localhost:3000

## Comandos úteis

```bash
# Logs
docker-compose logs -f chatwoot

# Restart
docker-compose restart chatwoot chatwoot-sidekiq

# Criar admin CLI
docker-compose exec chatwoot bundle exec rails runner \
  "User.create!(email: 'admin@example.com', password: 'Pass123!', name: 'Admin', role: 'administrator')"
```

## Troubleshooting

**Widget não aparece?**
- Verificar console do browser
- Confirmar websiteToken correto
- Verificar se Chatwoot está rodando: `docker-compose ps`

**Erro de conexão?**
- Verificar CHATWOOT_FRONTEND_URL
- Em dev, usar http://localhost:3001

**Performance lenta?**
- Widget carrega assíncrono, não bloqueia
- Verificar logs: `docker-compose logs chatwoot`
