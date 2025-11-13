# Integração Chatwoot

## Configuração Inicial

### 1. Subir os serviços
```bash
docker-compose up -d postgres chatwoot chatwoot-sidekiq
```

### 2. Acessar Chatwoot
- URL: http://localhost:3001
- Criar conta de administrador no primeiro acesso

### 3. Criar Inbox Website
1. Settings → Inboxes → Add Inbox
2. Selecionar "Website"
3. Copiar o código do widget (será algo como `websiteToken`)

## Integração no Frontend React

### Método 1: Script direto no index.html

Adicionar no `frontend/index.html` antes do `</body>`:

```html
<script>
  (function(d,t) {
    var BASE_URL="http://localhost:3001";
    var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
    g.src=BASE_URL+"/packs/js/sdk.js";
    g.defer = true;
    g.async = true;
    s.parentNode.insertBefore(g,s);
    g.onload=function(){
      window.chatwootSDK.run({
        websiteToken: 'SEU_WEBSITE_TOKEN_AQUI',
        baseUrl: BASE_URL
      })
    }
  })(document,"script");
</script>
```

### Método 2: Hook React customizado

Criar `frontend/src/hooks/useChatwoot.ts`:

```typescript
import { useEffect } from 'react';

interface ChatwootConfig {
  websiteToken: string;
  baseUrl?: string;
}

export function useChatwoot(config: ChatwootConfig) {
  useEffect(() => {
    const BASE_URL = config.baseUrl || 'http://localhost:3001';

    // Adicionar script
    const script = document.createElement('script');
    script.src = `${BASE_URL}/packs/js/sdk.js`;
    script.defer = true;
    script.async = true;

    script.onload = () => {
      (window as any).chatwootSDK?.run({
        websiteToken: config.websiteToken,
        baseUrl: BASE_URL
      });
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [config.websiteToken, config.baseUrl]);
}
```

Usar no `App.tsx`:

```typescript
import { useChatwoot } from './hooks/useChatwoot';

function App() {
  useChatwoot({
    websiteToken: import.meta.env.VITE_CHATWOOT_TOKEN,
    baseUrl: 'http://localhost:3001'
  });

  return <div>...</div>;
}
```

Adicionar no `.env`:
```
VITE_CHATWOOT_TOKEN=seu-website-token
```

### Método 3: Componente React

Criar `frontend/src/components/ChatwootWidget.tsx`:

```typescript
import { useEffect } from 'react';

interface ChatwootWidgetProps {
  websiteToken: string;
  baseUrl?: string;
}

export function ChatwootWidget({ websiteToken, baseUrl = 'http://localhost:3001' }: ChatwootWidgetProps) {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = `${baseUrl}/packs/js/sdk.js`;
    script.defer = true;
    script.async = true;

    script.onload = () => {
      (window as any).chatwootSDK?.run({
        websiteToken,
        baseUrl
      });
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [websiteToken, baseUrl]);

  return null;
}
```

Usar no App:
```typescript
<ChatwootWidget websiteToken="seu-token" />
```

## Métodos JavaScript API

Após carregar, você pode controlar o widget:

```javascript
// Abrir widget
window.$chatwoot.toggle('open');

// Fechar widget
window.$chatwoot.toggle('close');

// Definir usuário
window.$chatwoot.setUser('user-id', {
  email: 'user@example.com',
  name: 'User Name'
});

// Adicionar label
window.$chatwoot.setLabel('label-name');

// Eventos customizados
window.$chatwoot.setCustomAttributes({
  plan: 'premium',
  account_id: '123'
});
```

## Configurações Avançadas

### Customizar aparência

```javascript
window.chatwootSDK.run({
  websiteToken: 'token',
  baseUrl: 'http://localhost:3001',
  position: 'right', // left ou right
  locale: 'pt_BR',
  type: 'standard', // standard ou expanded_bubble
  launcherTitle: 'Chat com Suporte',
  showPopoutButton: true
});
```

### Identificar usuário logado

```typescript
// Após login do usuário
const user = getCurrentUser(); // sua função de auth

window.$chatwoot?.setUser(user.id, {
  email: user.email,
  name: user.name,
  phone_number: user.phone,
  avatar_url: user.avatar
});
```

## Variáveis de Ambiente

Adicionar ao `frontend/.env`:

```env
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=seu-website-token
VITE_CHATWOOT_BASE_URL=http://localhost:3001
```

Em produção:
```env
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=seu-token-production
VITE_CHATWOOT_BASE_URL=https://chat.seudominio.com
```

## Segurança em Produção

⚠️ **IMPORTANTE**: Antes de produção:

1. Gerar SECRET_KEY_BASE forte:
```bash
docker-compose exec chatwoot bundle exec rake secret
```

2. Configurar FRONTEND_URL correta
3. Configurar SMTP para emails (opcional)
4. Usar HTTPS em produção
5. Backup do banco PostgreSQL

## URLs dos Serviços

- **Chatwoot Admin**: http://localhost:3001
- **PostgreSQL**: localhost:5432
- **Redis** (compartilhado): localhost:6379

## Comandos Úteis

```bash
# Ver logs do Chatwoot
docker-compose logs -f chatwoot

# Reiniciar Chatwoot
docker-compose restart chatwoot chatwoot-sidekiq

# Executar console Rails
docker-compose exec chatwoot bundle exec rails console

# Criar admin via CLI
docker-compose exec chatwoot bundle exec rails runner "User.create!(email: 'admin@example.com', password: 'password', name: 'Admin', role: 'administrator')"
```

## Troubleshooting

### Widget não aparece
- Verificar se script carregou no Network do DevTools
- Verificar console do browser por erros
- Confirmar websiteToken correto

### Erro de CORS
- Verificar FRONTEND_URL no docker-compose
- Em dev, usar http://localhost:3001 como baseUrl

### Performance
- Widget carrega assíncrono, não bloqueia página
- Cache de assets habilitado
- Lazy load automático
