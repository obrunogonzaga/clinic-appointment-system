# Deploy Chatwoot no Coolify

Guia para fazer deploy do Chatwoot em produção usando Coolify.

## 📋 Pré-requisitos

- Coolify configurado e rodando
- Projeto já configurado no Coolify
- Acesso ao painel do Coolify
- DNS configurado para subdomínio do Chatwoot (ex: `chat.seudominio.com`)

## 🚀 Passos para Deploy

### 1. Gerar SECRET_KEY_BASE

**Importante**: NUNCA use a secret de desenvolvimento em produção!

```bash
# Localmente, gerar nova secret
docker run --rm chatwoot/chatwoot:latest bundle exec rake secret

# Copiar output (deve ter 127+ caracteres)
```

Exemplo de output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1
```

### 2. Configurar variáveis de ambiente no Coolify

No painel do Coolify, adicionar as seguintes variáveis:

```bash
# PostgreSQL
POSTGRES_DB=chatwoot_production
POSTGRES_USER=chatwoot
POSTGRES_PASSWORD=sua-senha-forte-aqui  # ⚠️ TROCAR!

# Chatwoot Database
CHATWOOT_DB_NAME=chatwoot_production
CHATWOOT_DB_USER=chatwoot
CHATWOOT_DB_PASSWORD=sua-senha-forte-aqui  # ⚠️ Mesma do POSTGRES_PASSWORD

# Chatwoot App
CHATWOOT_SECRET_KEY_BASE=secret-gerada-no-passo-1  # ⚠️ TROCAR!
CHATWOOT_FRONTEND_URL=https://chat.seudominio.com  # ⚠️ Seu domínio!

# Rails
RAILS_ENV=production
INSTALLATION_ENV=docker
ACTIVE_STORAGE_SERVICE=local
RAILS_LOG_TO_STDOUT=true
USE_INBOX_AVATAR_FOR_BOT=true
```

### 3. Configurar SMTP (Opcional mas recomendado)

Para notificações por email:

```bash
# Email settings
MAILER_SENDER_EMAIL=noreply@seudominio.com
SMTP_ADDRESS=smtp.gmail.com  # ou seu provedor
SMTP_PORT=587
SMTP_DOMAIN=seudominio.com
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app  # App password do Gmail
SMTP_AUTHENTICATION=plain
SMTP_ENABLE_STARTTLS_AUTO=true
```

### 4. Configurar DNS no Coolify

1. No painel do Coolify, ir em **Domains**
2. Adicionar domínio para o serviço `chatwoot`:
   - Domain: `chat.seudominio.com`
   - Service: `chatwoot`
   - Port: `3000`
3. Habilitar SSL (Let's Encrypt automático)

### 5. Deploy inicial

```bash
# Fazer push para branch configurado no Coolify
git add .
git commit -m "feat: add chatwoot to production"
git push origin main  # ou branch configurado
```

Coolify vai:
1. Detectar mudanças
2. Build das imagens
3. Iniciar serviços na ordem correta

### 6. Executar setup do banco (PRIMEIRA VEZ APENAS)

Após deploy, executar uma vez:

```bash
# Via painel Coolify -> Service chatwoot -> Terminal
bundle exec rails db:chatwoot_prepare

# Ou via SSH no servidor
docker exec -it <container-chatwoot> bundle exec rails db:chatwoot_prepare
```

Aguardar conclusão (1-2 minutos).

### 7. Criar usuário admin

```bash
# Via painel Coolify -> Service chatwoot -> Terminal
bundle exec rails runner "User.create!(email: 'admin@seudominio.com', password: 'SenhaForte123!', name: 'Admin', role: 'administrator')"
```

### 8. Acessar Chatwoot

1. Abrir: `https://chat.seudominio.com`
2. Login com credenciais criadas no passo 7
3. Configurar inbox Website:
   - Settings → Inboxes → Add Inbox → Website
   - Copiar `websiteToken`

### 9. Configurar Frontend

No Coolify, adicionar variável de ambiente para o serviço **frontend**:

```bash
VITE_CHATWOOT_ENABLED=true
VITE_CHATWOOT_TOKEN=token-copiado-do-passo-8
VITE_CHATWOOT_BASE_URL=https://chat.seudominio.com
```

Fazer redeploy do frontend.

## ✅ Verificação

### Testar serviços

```bash
# API health
curl https://chat.seudominio.com/api
# Deve retornar: {"version":"4.5.2",...}

# PostgreSQL
docker exec <container-postgres> psql -U chatwoot -d chatwoot_production -c "SELECT 1;"

# Redis
docker exec <container-redis> redis-cli ping
```

### Logs

```bash
# Via Coolify UI: Service → Logs

# Ou via Docker
docker logs <container-chatwoot> --tail=50
docker logs <container-chatwoot-sidekiq> --tail=50
```

## 🔧 Troubleshooting

### Chatwoot não inicia

**Problema**: Container reiniciando constantemente

**Solução**:
1. Verificar logs: `docker logs <container-chatwoot>`
2. Verificar SECRET_KEY_BASE tem 127+ chars
3. Verificar PostgreSQL está healthy: `docker ps`

### Erro "web widget does not exist"

**Problema**: Widget retorna 404

**Solução**:
1. Verificar inbox foi criado no painel Chatwoot
2. Verificar token está correto
3. Verificar CHATWOOT_FRONTEND_URL está correto
4. Limpar cache do browser

### PostgreSQL connection refused

**Problema**: Chatwoot não conecta ao banco

**Solução**:
1. Verificar CHATWOOT_DB_PASSWORD = POSTGRES_PASSWORD
2. Verificar PostgreSQL container está rodando
3. Verificar healthcheck do postgres: `docker ps`

### Emails não enviam

**Problema**: Notificações não chegam

**Solução**:
1. Verificar SMTP configurado corretamente
2. Testar SMTP com comando Rails:
```bash
docker exec <chatwoot> bundle exec rails runner "ActionMailer::Base.mail(from: ENV['MAILER_SENDER_EMAIL'], to: 'test@example.com', subject: 'Test', body: 'Test').deliver_now"
```

### Performance lenta

**Soluções**:
- Aumentar recursos no Coolify (CPU/RAM)
- Verificar Redis funcionando
- Verificar Sidekiq processando jobs:
```bash
docker logs <chatwoot-sidekiq> --tail=20
```

## 🔐 Segurança - Checklist

- [ ] SECRET_KEY_BASE única e com 127+ caracteres
- [ ] POSTGRES_PASSWORD forte e diferente de dev
- [ ] CHATWOOT_FRONTEND_URL usa HTTPS
- [ ] SSL/TLS habilitado no Coolify
- [ ] Firewall configurado (apenas 80, 443 abertos)
- [ ] Backup automático do PostgreSQL configurado
- [ ] SMTP usa credenciais app-specific (não senha real)
- [ ] CORS configurado apenas para domínio específico

## 📊 Monitoramento

### Healthchecks

Todos os serviços têm healthchecks:
- `postgres`: `pg_isready`
- `chatwoot`: `curl /api`
- `chatwoot-sidekiq`: monitora automaticamente

### Backup PostgreSQL

Configurar cron job no servidor:

```bash
# Crontab
0 2 * * * docker exec <postgres-container> pg_dump -U chatwoot chatwoot_production | gzip > /backup/chatwoot_$(date +\%Y\%m\%d).sql.gz

# Manter últimos 30 dias
0 3 * * * find /backup/chatwoot_*.sql.gz -mtime +30 -delete
```

### Logs

Configurar rotação de logs no Coolify para evitar disco cheio.

## 🔄 Atualizações

Para atualizar Chatwoot:

```bash
# 1. Pull nova imagem
docker pull chatwoot/chatwoot:latest

# 2. Via Coolify: Redeploy services
# chatwoot
# chatwoot-sidekiq

# 3. Verificar migrations
docker exec <chatwoot> bundle exec rails db:migrate

# 4. Restart
docker restart <chatwoot> <chatwoot-sidekiq>
```

## 📚 Recursos

- Documentação Chatwoot: https://www.chatwoot.com/docs/self-hosted
- Issues: https://github.com/chatwoot/chatwoot/issues
- Comunidade: https://chatwoot.com/community

## 🆘 Suporte

Se problemas persistirem:
1. Verificar logs de todos os serviços
2. Verificar variáveis de ambiente
3. Consultar docs Chatwoot oficial
4. Abrir issue no repositório do projeto
