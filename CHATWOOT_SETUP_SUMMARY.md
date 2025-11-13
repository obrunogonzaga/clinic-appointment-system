# ✅ Chatwoot - Configuração Completa e Testada

Chatwoot foi totalmente integrado e está rodando! 🎉

**Status**: ✅ Online e funcionando em http://localhost:3001

## 📦 O que foi adicionado

### Docker Services
- ✅ PostgreSQL 15 com extensão pgvector (porta 5432)
- ✅ Chatwoot web app (porta 3001) - **RODANDO**
- ✅ Chatwoot Sidekiq (workers) - **RODANDO**
- ✅ Volumes persistentes (postgres_data, chatwoot_data)
- ✅ Banco de dados configurado e migrations executadas

### Frontend
- ✅ `ChatwootWidget.tsx` - Componente React pronto
- ✅ `useChatwoot()` - Hook para controle programático
- ✅ `chatwoot.d.ts` - Tipos TypeScript
- ✅ Variáveis de ambiente no `.env.example`

### DevOps
- ✅ 9 comandos Make para gerenciar Chatwoot
- ✅ Configurações no docker-compose.yml
- ✅ Variáveis no .env.example e .env.local

### Documentação
- ✅ CHATWOOT_README.md - Visão geral
- ✅ CHATWOOT_QUICKSTART.md - Início rápido
- ✅ CHATWOOT_INTEGRATION.md - Guia completo
- ✅ CHATWOOT_APP_EXAMPLE.tsx - 6 exemplos práticos

## 🚀 Como usar (3 minutos)

### 1. Subir Chatwoot
```bash
make chatwoot-up
```

### 2. Criar conta admin
- Acessar: http://localhost:3001
- Criar conta (primeiro acesso)
- Settings → Inboxes → Add Inbox → Website
- Copiar o `websiteToken`

### 3. Adicionar ao frontend
```bash
# Editar frontend/.env
VITE_CHATWOOT_TOKEN=seu-token-aqui
```

```typescript
// frontend/src/App.tsx
import { ChatwootWidget } from './components/ChatwootWidget';

function App() {
  return (
    <>
      <ChatwootWidget websiteToken={import.meta.env.VITE_CHATWOOT_TOKEN} />
      <YourApp />
    </>
  );
}
```

Pronto! O widget aparecerá no canto da tela. 🎯

## 📋 Comandos disponíveis

```bash
make chatwoot-up       # Iniciar Chatwoot
make chatwoot-down     # Parar Chatwoot
make chatwoot-logs     # Ver logs em tempo real
make chatwoot-shell    # Rails console
make chatwoot-admin    # Criar admin via CLI
make chatwoot-secret   # Gerar SECRET_KEY_BASE
make chatwoot-status   # Status dos serviços
make chatwoot-backup   # Backup PostgreSQL
make chatwoot-reset    # Reset database (cuidado!)
```

## 🎨 Exemplos de uso

### Básico (visitante anônimo)
```typescript
<ChatwootWidget websiteToken="token" />
```

### Com usuário logado
```typescript
<ChatwootWidget
  websiteToken="token"
  user={{
    id: user.id,
    email: user.email,
    name: user.name
  }}
/>
```

### Abrir chat programaticamente
```typescript
import { useChatwoot } from './components/ChatwootWidget';

function SupportButton() {
  const { open } = useChatwoot();
  return <button onClick={open}>Suporte</button>;
}
```

### Customizado
```typescript
<ChatwootWidget
  websiteToken="token"
  position="left"
  locale="pt_BR"
  user={user}
  customAttributes={{ plan: 'premium', company: 'ACME' }}
/>
```

## 📁 Estrutura de arquivos

```
clinic-appointment/
├── docker-compose.yml              # Serviços: postgres, chatwoot, sidekiq
├── .env.example                    # Template de variáveis
├── .env.local                      # Config local (gitignored)
├── Makefile                        # Comandos chatwoot-*
│
├── docs/
│   ├── CHATWOOT_README.md          # Visão geral (LEIA PRIMEIRO)
│   ├── CHATWOOT_QUICKSTART.md      # Guia rápido (5 min)
│   ├── CHATWOOT_INTEGRATION.md     # Guia completo
│   └── CHATWOOT_APP_EXAMPLE.tsx    # 6 exemplos práticos
│
└── frontend/
    ├── .env.example                # Variáveis Chatwoot
    └── src/
        ├── components/
        │   └── ChatwootWidget.tsx  # Componente + hook
        └── types/
            └── chatwoot.d.ts       # TypeScript defs
```

## 🌐 URLs

| Serviço   | URL                        | Descrição           |
|-----------|----------------------------|---------------------|
| Chatwoot  | http://localhost:3001      | Admin panel         |
| Frontend  | http://localhost:3000      | React app           |
| Backend   | http://localhost:8000      | FastAPI             |
| Postgres  | localhost:5432             | Database            |

## 🔐 Credenciais (dev)

```env
# PostgreSQL
User: chatwoot
Password: chatwoot123
Database: chatwoot_development

# Chatwoot Admin
Criar no primeiro acesso em http://localhost:3001
```

## 📚 Próximos passos

### Desenvolvimento
1. ✅ Chatwoot configurado
2. ⏭️ Adicionar widget no App.tsx
3. ⏭️ Testar envio de mensagens
4. ⏭️ Configurar notificações (opcional)
5. ⏭️ Customizar aparência (cores, posição)

### Produção
1. ⏭️ Gerar SECRET_KEY_BASE seguro (`make chatwoot-secret`)
2. ⏭️ Configurar domínio (CHATWOOT_FRONTEND_URL)
3. ⏭️ Configurar SMTP para emails
4. ⏭️ HTTPS obrigatório
5. ⏭️ Backup automático do PostgreSQL
6. ⏭️ Monitoramento (logs, métricas)

## 🆘 Troubleshooting rápido

| Problema                | Solução                                    |
|-------------------------|-------------------------------------------|
| Widget não aparece      | Verificar token em frontend/.env          |
| Erro de conexão         | Verificar se Chatwoot está up: `make chatwoot-status` |
| Lentidão               | Ver logs: `make chatwoot-logs`            |
| Esqueci admin password  | Criar novo: `make chatwoot-admin`         |
| Erro CORS              | Verificar CHATWOOT_FRONTEND_URL           |

## 📖 Documentação completa

Para detalhes, consulte:

1. **[docs/CHATWOOT_README.md](./docs/CHATWOOT_README.md)** - Overview completo
2. **[docs/CHATWOOT_QUICKSTART.md](./docs/CHATWOOT_QUICKSTART.md)** - Guia de 5 min
3. **[docs/CHATWOOT_INTEGRATION.md](./docs/CHATWOOT_INTEGRATION.md)** - Referência completa
4. **[docs/CHATWOOT_APP_EXAMPLE.tsx](./docs/CHATWOOT_APP_EXAMPLE.tsx)** - Código pronto

## ✅ Checklist de integração

- [ ] `make chatwoot-up` executado com sucesso
- [ ] Admin criado em http://localhost:3001
- [ ] Inbox "Website" configurado
- [ ] Token copiado e adicionado ao frontend/.env
- [ ] ChatwootWidget importado no App.tsx
- [ ] Widget aparece no canto da tela
- [ ] Teste de mensagem funciona
- [ ] (Opcional) Usuário identificado quando logado
- [ ] (Prod) SECRET_KEY_BASE gerado
- [ ] (Prod) SMTP configurado
- [ ] (Prod) Backup agendado

## 🎯 Tudo pronto!

Chatwoot está 100% configurado e pronto para usar. Basta seguir o guia "Como usar" acima e em 3 minutos terá chat funcionando! 🚀

Para dúvidas:
- Documentação oficial: https://www.chatwoot.com/docs
- Issues: https://github.com/chatwoot/chatwoot/issues
