# ✅ Chatwoot - Pronto para Produção

Chatwoot está configurado para deploy em produção via Coolify! 🚀

## 📁 Arquivos Modificados para Produção

### Docker Compose
- ✅ **docker-compose.coolify.yml** - Adicionado:
  - `postgres` (PostgreSQL 15 com pgvector)
  - `chatwoot` (Chatwoot app na porta 3000)
  - `chatwoot-sidekiq` (Workers para jobs assíncronos)
  - Volumes `postgres_data` e `chatwoot_data`

### Variáveis de Ambiente
- ✅ **.env.coolify.example** - Adicionadas variáveis:
  - PostgreSQL credentials
  - Chatwoot configuration
  - SMTP settings (opcional)
  - Todas com valores de exemplo

### Documentação
- ✅ **docs/CHATWOOT_DEPLOY_COOLIFY.md** - Guia completo de deploy

## 🚀 Deploy em 9 Passos

### 1. Gerar SECRET_KEY_BASE
```bash
docker run --rm chatwoot/chatwoot:latest bundle exec rake secret
```

### 2. Configurar variáveis no Coolify

Copiar de `.env.coolify.example` e substituir valores:

```bash
# Obrigatórios
POSTGRES_PASSWORD=senha-forte-aqui
CHATWOOT_DB_PASSWORD=mesma-senha-acima
CHATWOOT_SECRET_KEY_BASE=secret-gerada-no-passo-1
CHATWOOT_FRONTEND_URL=https://chat.seudominio.com
```

### 3. Configurar DNS

No Coolify:
- Domain: `chat.seudominio.com`
- Service: `chatwoot`
- Port: `3000`
- SSL: Enabled

### 4. Deploy
```bash
git add .
git commit -m "feat: add chatwoot to production"
git push origin main
```

### 5. Executar setup do banco (primeira vez)
```bash
# Via painel Coolify -> Service chatwoot -> Terminal
bundle exec rails db:chatwoot_prepare
```

### 6. Criar admin
```bash
bundle exec rails runner "User.create!(email: 'admin@seudominio.com', password: 'SenhaForte123!', name: 'Admin', role: 'administrator')"
```

### 7. Acessar Chatwoot
```
https://chat.seudominio.com
```

### 8. Configurar Inbox Website
- Settings → Inboxes → Add Inbox → Website
- Copiar `websiteToken`

### 9. Adicionar token no frontend

No Coolify, serviço **frontend**, adicionar:
```bash
VITE_CHATWOOT_TOKEN=token-copiado
VITE_CHATWOOT_BASE_URL=https://chat.seudominio.com
```

Redeploy frontend.

## ✅ Checklist de Deploy

### Antes do Deploy
- [ ] SECRET_KEY_BASE gerada (127+ chars)
- [ ] Senhas fortes definidas
- [ ] DNS configurado
- [ ] Variáveis de ambiente no Coolify
- [ ] SMTP configurado (opcional)

### Durante Deploy
- [ ] Push para repositório
- [ ] Coolify detectou mudanças
- [ ] Build bem-sucedido
- [ ] Containers iniciados
- [ ] `db:chatwoot_prepare` executado
- [ ] Admin criado

### Após Deploy
- [ ] Chatwoot acessível via HTTPS
- [ ] Login funcionando
- [ ] Inbox Website configurado
- [ ] Token adicionado ao frontend
- [ ] Widget aparecendo no frontend
- [ ] Mensagem de teste enviada com sucesso

## 🔐 Segurança

### ⚠️ NUNCA commitar:
- Senhas reais
- SECRET_KEY_BASE de produção
- Tokens de API
- Credenciais SMTP

### ✅ Usar:
- Secrets do Coolify
- Variáveis de ambiente
- .env.coolify (git ignored)

## 📊 Serviços em Produção

| Serviço | Porta | Healthcheck | Logs |
|---------|-------|-------------|------|
| postgres | 5432 | ✅ pg_isready | Coolify UI |
| chatwoot | 3000 | ✅ /api endpoint | Coolify UI |
| chatwoot-sidekiq | - | ✅ Auto | Coolify UI |

## 🔄 Volumes Persistentes

- `clinic-chatwoot-postgres-data` - Banco de dados
- `clinic-chatwoot-data` - Uploads e storage

**Backup**: Configure backup automático do PostgreSQL!

## 🛠️ Troubleshooting Rápido

### Container reiniciando
```bash
# Ver logs
docker logs <container-chatwoot>

# Verificar SECRET_KEY_BASE
# Verificar PostgreSQL healthy
```

### Widget 404
```bash
# Verificar inbox criado
# Verificar token correto
# Limpar cache browser
```

### Emails não enviam
```bash
# Verificar SMTP configurado
# Testar via Rails console
```

## 📚 Documentação Completa

- **[CHATWOOT_DEPLOY_COOLIFY.md](./docs/CHATWOOT_DEPLOY_COOLIFY.md)** - Guia completo
- **[CHATWOOT_TROUBLESHOOTING.md](./docs/CHATWOOT_TROUBLESHOOTING.md)** - Solução de problemas
- **[CHATWOOT_README.md](./docs/CHATWOOT_README.md)** - Overview geral

## 🎯 Próximos Passos

1. Fazer deploy conforme guia acima
2. Testar widget em produção
3. Configurar notificações
4. Configurar backup automático
5. Configurar monitoring (opcional)

## 📈 Monitoramento (Opcional)

### Healthcheck endpoints
- Chatwoot API: `https://chat.seudominio.com/api`
- PostgreSQL: Via comando `pg_isready`

### Métricas
- Uptime Robot ou similar
- Logs no Coolify
- Backup alerts

## ✅ Tudo Pronto!

Chatwoot está configurado para produção. Basta seguir os 9 passos acima e terá chat de suporte funcionando em 15-20 minutos! 🎉

**Dúvidas?** Consulte [CHATWOOT_DEPLOY_COOLIFY.md](./docs/CHATWOOT_DEPLOY_COOLIFY.md)
