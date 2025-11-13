# Chatwoot - Plataforma de Atendimento

Integração completa do Chatwoot como plataforma de suporte ao cliente.

## 📋 O que foi configurado

✅ Chatwoot web app (porta 3001)
✅ PostgreSQL database para Chatwoot
✅ Sidekiq workers para jobs assíncronos
✅ Componente React pronto para usar
✅ Hooks customizados
✅ Tipos TypeScript
✅ Comandos Make para gerenciamento
✅ Documentação completa

## 🚀 Início Rápido (3 passos)

### 1. Subir Chatwoot
```bash
make chatwoot-up
```

### 2. Acessar e configurar
- Abrir http://localhost:3001
- Criar conta admin
- Settings → Inboxes → Add Inbox → Website
- Copiar `websiteToken`

### 3. Integrar no React
```typescript
// frontend/src/App.tsx
import { ChatwootWidget } from './components/ChatwootWidget';

function App() {
  return (
    <>
      <ChatwootWidget websiteToken="SEU_TOKEN" />
      {/* resto da app */}
    </>
  );
}
```

## 📁 Arquivos criados

```
frontend/src/
├── components/
│   └── ChatwootWidget.tsx          # Componente principal
└── types/
    └── chatwoot.d.ts               # Tipos TypeScript

docs/
├── CHATWOOT_INTEGRATION.md         # Guia completo de integração
├── CHATWOOT_QUICKSTART.md          # Guia rápido
├── CHATWOOT_APP_EXAMPLE.tsx        # Exemplos práticos de uso
└── CHATWOOT_README.md              # Este arquivo

docker-compose.yml                   # Serviços: postgres, chatwoot, sidekiq
.env.example                         # Variáveis de ambiente
.env.local                          # Configuração local
Makefile                            # Comandos úteis
```

## 🛠️ Comandos Make

```bash
make chatwoot-up          # Subir Chatwoot
make chatwoot-down        # Parar Chatwoot
make chatwoot-logs        # Ver logs
make chatwoot-shell       # Rails console
make chatwoot-admin       # Criar admin via CLI
make chatwoot-secret      # Gerar SECRET_KEY_BASE
make chatwoot-status      # Status dos serviços
make chatwoot-backup      # Backup do banco
make chatwoot-reset       # Reset database (cuidado!)
```

## 📦 Serviços Docker

```yaml
postgres:3001      # PostgreSQL 15
chatwoot:3001      # Chatwoot app
chatwoot-sidekiq   # Background jobs
```

## 🔑 Credenciais padrão (dev)

```
# Chatwoot Admin (criar no primeiro acesso)
Email: admin@example.com
Password: [escolha uma senha]

# PostgreSQL
User: chatwoot
Password: chatwoot123
Database: chatwoot_development
```

## 🌐 URLs

- **Chatwoot**: http://localhost:3001
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## 📚 Documentação

Para mais detalhes:
- [CHATWOOT_QUICKSTART.md](./CHATWOOT_QUICKSTART.md) - Guia rápido
- [CHATWOOT_INTEGRATION.md](./CHATWOOT_INTEGRATION.md) - Guia completo
- [CHATWOOT_APP_EXAMPLE.tsx](./CHATWOOT_APP_EXAMPLE.tsx) - Exemplos de código

## ⚙️ Variáveis de ambiente

### Backend (.env)
```env
CHATWOOT_DB_NAME=chatwoot_production
CHATWOOT_DB_USER=chatwoot
CHATWOOT_DB_PASSWORD=chatwootpass
CHATWOOT_SECRET_KEY_BASE=your-secret-key
CHATWOOT_FRONTEND_URL=http://localhost:3001
```

### Frontend (.env)
```env
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=seu-website-token
VITE_CHATWOOT_BASE_URL=http://localhost:3001
```

## 🔐 Segurança - Produção

Antes de ir pra produção:

1. **Gerar SECRET_KEY_BASE seguro**
   ```bash
   make chatwoot-secret
   ```

2. **Atualizar URLs**
   ```env
   CHATWOOT_FRONTEND_URL=https://chat.seudominio.com
   ```

3. **Configurar SMTP** (emails)
   ```env
   SMTP_ADDRESS=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=seu-email@gmail.com
   SMTP_PASSWORD=sua-senha
   ```

4. **HTTPS obrigatório**

5. **Backup regular do PostgreSQL**
   ```bash
   make chatwoot-backup
   ```

## 🎨 Customização

### Posição do widget
```typescript
<ChatwootWidget
  websiteToken="token"
  position="left"  // ou "right"
/>
```

### Idioma
```typescript
<ChatwootWidget
  websiteToken="token"
  locale="pt_BR"  // ou "en", "es", etc
/>
```

### Identificar usuário
```typescript
<ChatwootWidget
  websiteToken="token"
  user={{
    id: user.id,
    email: user.email,
    name: user.name,
    phone_number: user.phone
  }}
/>
```

## 🐛 Troubleshooting

### Widget não aparece
```bash
# 1. Verificar se Chatwoot está rodando
make chatwoot-status

# 2. Ver logs
make chatwoot-logs

# 3. Verificar token no .env
cat frontend/.env | grep CHATWOOT
```

### Erro de conexão
- Verificar CHATWOOT_FRONTEND_URL
- Em dev usar http://localhost:3001
- Verificar CORS no console do browser

### Performance lenta
- Widget carrega assíncrono (não bloqueia)
- Verificar logs: `make chatwoot-logs`
- Verificar PostgreSQL: `docker-compose ps postgres`

## 📊 Monitoramento

```bash
# Status geral
make chatwoot-status

# Logs em tempo real
make chatwoot-logs

# Verificar banco
docker-compose exec postgres psql -U chatwoot -d chatwoot_production
```

## 🔄 Atualização

Para atualizar Chatwoot:
```bash
docker-compose pull chatwoot
docker-compose up -d chatwoot chatwoot-sidekiq
```

## 💾 Backup e Restore

```bash
# Backup
make chatwoot-backup

# Restore manual
docker-compose exec postgres psql -U chatwoot chatwoot_production < backup/chatwoot_YYYYMMDD_HHMMSS.sql
```

## 🤝 Suporte

- Documentação oficial: https://www.chatwoot.com/docs
- GitHub: https://github.com/chatwoot/chatwoot
- Comunidade: https://chatwoot.com/community

## ✅ Checklist de integração

- [ ] Chatwoot rodando (`make chatwoot-up`)
- [ ] Admin criado em http://localhost:3001
- [ ] Inbox Website configurado
- [ ] websiteToken copiado
- [ ] Token adicionado ao frontend/.env
- [ ] ChatwootWidget importado no App.tsx
- [ ] Widget aparecendo na tela
- [ ] Teste de mensagem funcionando
- [ ] Usuário identificado corretamente (se autenticado)
- [ ] SECRET_KEY_BASE gerado para produção
- [ ] Backup configurado
