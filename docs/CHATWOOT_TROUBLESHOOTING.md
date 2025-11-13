# Chatwoot - Troubleshooting

## Problema resolvido: extensão pgvector

### Erro
```
ERROR:  extension "vector" is not available
DETAIL:  Could not open extension control file "/usr/local/share/postgresql/extension/vector.control"
```

### Causa
Chatwoot requer extensão `pgvector` no PostgreSQL para funcionalidades de AI/embeddings.

### Solução
Trocar imagem do PostgreSQL de `postgres:15-alpine` para `pgvector/pgvector:pg15`:

```yaml
postgres:
  image: pgvector/pgvector:pg15  # ← imagem com pgvector
  # resto da config...
```

### Passos para corrigir

```bash
# 1. Parar serviços
docker-compose stop chatwoot chatwoot-sidekiq postgres

# 2. Remover containers e volume
docker-compose rm -f chatwoot chatwoot-sidekiq postgres
docker volume rm clinic-chatwoot-postgres-data

# 3. Atualizar docker-compose.yml (usar pgvector/pgvector:pg15)

# 4. Recriar serviços
docker-compose up -d postgres chatwoot chatwoot-sidekiq

# 5. Executar setup do banco (uma vez)
docker-compose run --rm chatwoot bundle exec rails db:chatwoot_prepare

# 6. Iniciar Chatwoot
docker-compose up -d chatwoot
```

## Verificar se está rodando

```bash
# Status dos containers
docker-compose ps chatwoot

# Logs do Puma server
docker-compose logs chatwoot | grep "Puma\|Listening"

# Deve mostrar:
# * Listening on http://0.0.0.0:3000

# Testar acesso
curl -I http://localhost:3001
# Deve retornar: HTTP/1.1 302 Found
```

## Outros problemas comuns

### Container em loop de restart
**Causa**: Banco não inicializado ou comando incorreto

**Solução**:
```bash
# Executar setup do banco
docker-compose run --rm chatwoot bundle exec rails db:chatwoot_prepare

# Verificar comando no docker-compose.yml:
command: bundle exec rails server -b 0.0.0.0 -p 3000
```

### Widget não aparece no frontend
**Causa**: Token incorreto ou Chatwoot não acessível

**Solução**:
1. Verificar Chatwoot rodando: `docker-compose ps chatwoot`
2. Verificar token no frontend/.env
3. Verificar CHATWOOT_FRONTEND_URL em .env
4. Console do browser (F12) para erros

### Erro de conexão PostgreSQL
**Causa**: Banco não pronto ou credenciais erradas

**Solução**:
```bash
# Verificar saúde do PostgreSQL
docker-compose ps postgres

# Deve mostrar: (healthy)

# Testar conexão
docker-compose exec postgres psql -U chatwoot -d chatwoot_production -c "SELECT 1;"
```

### Sidekiq não processa jobs
**Causa**: Redis não conectado

**Solução**:
```bash
# Verificar Redis
docker-compose ps redis

# Logs do Sidekiq
docker-compose logs chatwoot-sidekiq | tail -20
```

### Performance lenta
**Soluções**:
- Aumentar recursos Docker (CPU/RAM)
- Verificar logs: `docker-compose logs chatwoot`
- Limpar cache: `docker-compose exec chatwoot bundle exec rails cache:clear`

### Espaço em disco cheio
**Solução**:
```bash
# Limpar imagens antigas
docker image prune -a

# Limpar volumes não usados
docker volume prune

# Backup e remover logs antigos
docker-compose exec chatwoot sh -c "find /app/log -name '*.log' -mtime +7 -delete"
```

## Comandos úteis debug

```bash
# Shell no container
docker-compose exec chatwoot sh

# Rails console
docker-compose exec chatwoot bundle exec rails console

# Verificar variáveis de ambiente
docker-compose exec chatwoot env | grep -E "POSTGRES|REDIS|SECRET"

# Resetar tudo (CUIDADO!)
docker-compose down -v
docker-compose up -d
```

## Logs importantes

```bash
# Tudo
docker-compose logs -f

# Apenas Chatwoot
docker-compose logs -f chatwoot

# Apenas erros
docker-compose logs chatwoot | grep -i error

# Últimas 50 linhas
docker-compose logs chatwoot --tail=50
```

## Health check

Script para verificar saúde geral:

```bash
#!/bin/bash
echo "=== Chatwoot Health Check ==="

echo -n "PostgreSQL: "
docker-compose ps postgres | grep -q "healthy" && echo "✅ OK" || echo "❌ FAIL"

echo -n "Redis: "
docker-compose ps redis | grep -q "healthy" && echo "✅ OK" || echo "❌ FAIL"

echo -n "Chatwoot: "
docker-compose ps chatwoot | grep -q "Up" && echo "✅ OK" || echo "❌ FAIL"

echo -n "Sidekiq: "
docker-compose ps chatwoot-sidekiq | grep -q "Up" && echo "✅ OK" || echo "❌ FAIL"

echo -n "HTTP Response: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "302\|200" && echo "✅ OK" || echo "❌ FAIL"
```

Salvar como `chatwoot-health.sh` e executar: `bash chatwoot-health.sh`

## Suporte

Se problemas persistirem:
1. Verificar logs: `docker-compose logs chatwoot --tail=100`
2. Issues Chatwoot: https://github.com/chatwoot/chatwoot/issues
3. Docs oficiais: https://www.chatwoot.com/docs/self-hosted
