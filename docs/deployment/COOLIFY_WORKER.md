# Configuração do Worker ARQ no Coolify

Este guia descreve como configurar e fazer deploy do worker ARQ para processamento de background jobs no Coolify.

## Visão Geral

O worker ARQ é um processo separado responsável por:
- Processar jobs de normalização de endereços e documentos
- Executar tarefas em background sem bloquear o API
- Escalar horizontalmente conforme necessidade

## Pré-requisitos

- Redis configurado e rodando (veja [COOLIFY_REDIS.md](./COOLIFY_REDIS.md))
- Backend (API) já deployed no Coolify
- MongoDB configurado e acessível

## Arquitetura

```
┌──────────────┐         ┌───────────┐         ┌────────────────┐
│   Frontend   │ ─────▶  │  Backend  │ ─────▶  │  Redis Queue   │
└──────────────┘         │  (FastAPI)│         └────────────────┘
                         └───────────┘                 │
                                                       │
                                                       ▼
                                            ┌──────────────────┐
                                            │   ARQ Worker     │
                                            │  (Background)    │
                                            └──────────────────┘
                                                       │
                                                       ▼
                              ┌─────────────────────────────────────┐
                              │  OpenAI API / MongoDB / etc.        │
                              └─────────────────────────────────────┘
```

## Passos de Configuração

### 1. Adicionar Worker como novo Resource

No Coolify:

1. Acesse seu projeto **clinic-appointment**
2. Clique em **+ Add Resource**
3. Selecione **Docker Compose**
4. Escolha o mesmo repositório do backend

### 2. Configurar Docker Compose

O worker está definido no `docker-compose.yml` existente. No Coolify:

1. Use o arquivo `docker-compose.yml` do repositório
2. Certifique-se que está na branch correta (com o worker implementado)
3. No Coolify, selecione apenas o serviço **worker** para deploy

### 3. Configurar Variáveis de Ambiente

Configure as seguintes variáveis para o worker:

#### Variáveis Obrigatórias

```bash
# Database
MONGODB_URL=mongodb://<usuario>:<senha>@mongodb:27017/
DATABASE_NAME=clinic_db

# Redis
REDIS_URL=redis://clinic-redis:6379
REDIS_PASSWORD=<SUA_SENHA_REDIS>

# Environment
ENVIRONMENT=production
DEBUG=False

# OpenAI/OpenRouter (para normalização)
OPENAI_API_KEY=<SUA_CHAVE_API>
ADDRESS_NORMALIZATION_ENABLED=true
DOCUMENT_NORMALIZATION_ENABLED=true
```

#### Variáveis Opcionais

```bash
# Worker behavior (geralmente não precisa alterar)
ARQ_MAX_JOBS=10
ARQ_JOB_TIMEOUT=300
ARQ_KEEP_RESULT=3600

# Logging
LOG_LEVEL=INFO
```

### 4. Configurar Resources

Recomendações de recursos para o worker:

**Desenvolvimento/Staging:**
- CPU: 0.5 cores
- RAM: 512 MB
- Replicas: 1

**Produção:**
- CPU: 1 core
- RAM: 1 GB
- Replicas: 2-3 (para redundância)

### 5. Configurar Health Checks

No Coolify, configure health check:

```bash
# Command
ps aux | grep "python workers.py" | grep -v grep

# Interval: 30s
# Timeout: 10s
# Retries: 3
```

### 6. Deploy

1. Revise todas as configurações
2. Clique em **Deploy**
3. Monitore os logs para confirmar inicialização

## Verificação Pós-Deploy

### 1. Verificar Logs

Nos logs do worker, você deve ver:

```
============================================================
Starting ARQ Background Worker
============================================================
Tasks registered:
  - normalize_appointment
Redis: clinic-redis:6379
Max concurrent jobs: 10
Job timeout: 300 seconds
============================================================
```

### 2. Teste de Conexão

Execute no backend container:

```bash
# Python shell
python

>>> from src.application.services.task_service import TaskService
>>> import asyncio
>>> ts = TaskService()
>>> asyncio.run(ts.get_pool())
# Deve retornar um pool de conexão sem erro
```

### 3. Teste End-to-End

1. Importe um arquivo Excel com endereços através da API
2. Verifique que appointments são criados imediatamente
3. Monitore logs do worker para ver jobs sendo processados
4. Após alguns segundos, verifique se os campos `endereco_normalizado` e `documento_normalizado` foram preenchidos

## Monitoramento

### Métricas Importantes

No painel do Coolify e logs do worker, monitore:

1. **CPU Usage**: Deve ficar < 80% em operação normal
2. **Memory Usage**: Deve ser estável (sem leaks)
3. **Job Processing Rate**: Jobs/minuto processados
4. **Error Rate**: % de jobs falhando

### Comandos de Monitoramento

Via Coolify Console (worker container):

```bash
# Ver jobs pendentes
redis-cli -h clinic-redis -p 6379 -a <SENHA> LLEN "arq:queue:default"

# Ver informações de jobs
redis-cli -h clinic-redis -p 6379 -a <SENHA> KEYS "arq:job:*"

# Ver últimos logs
tail -f /proc/1/fd/1
```

### Alarmes Recomendados

Configure alarmes para:
- Worker parado/crashando (> 5 minutos sem heartbeat)
- Fila de jobs muito grande (> 100 pendentes)
- Taxa de erro alta (> 10%)
- Uso de memória alto (> 90%)

## Escalonamento

### Escalonamento Horizontal

Para aumentar throughput:

1. No Coolify, aumente o número de **Replicas**
2. Cada replica processará jobs independentemente
3. Recomendado: 1 worker para cada 50-100 jobs/hora

### Escalonamento Vertical

Para jobs mais pesados:

1. Aumente CPU e RAM do container
2. Útil se jobs individuais são lentos
3. Configure `ARQ_MAX_JOBS` para aproveitar recursos extras

## Troubleshooting

### Worker não processa jobs

**Sintoma**: Jobs ficam na fila mas não são executados

**Diagnóstico**:
```bash
# Verificar se worker está rodando
ps aux | grep "python workers.py"

# Verificar logs
docker logs <worker-container-id>

# Verificar conexão com Redis
redis-cli -h clinic-redis -p 6379 -a <SENHA> ping
```

**Soluções**:
1. Reinicie o worker no Coolify
2. Verifique variáveis de ambiente
3. Confirme que Redis está acessível

### Jobs falhando com timeout

**Sintoma**: Jobs marcados como failed após 300s

**Solução**:
1. Aumente `ARQ_JOB_TIMEOUT` para jobs mais demorados
2. Ou otimize a lógica de normalização
3. Verifique se OpenAI API está respondendo devagar

### Memory leak

**Sintoma**: Uso de memória aumenta continuamente

**Solução**:
1. Configure restart policy no Coolify
2. Monitore e reporte issue se persistir
3. Temporariamente: reinicie worker periodicamente

### Erro de conexão ao MongoDB/OpenAI

**Sintoma**: Jobs falhando com "Connection refused" ou "timeout"

**Solução**:
1. Verifique network configuration
2. Teste conexões manualmente
3. Confirme que APIs keys estão corretas

## Rollback

Se houver problema após deploy:

1. No Coolify, vá para **Deployments**
2. Clique em **Rollback** para versão anterior
3. Ou pause o worker temporariamente enquanto investiga

## Manutenção

### Limpeza de Jobs Antigos

Execute periodicamente (via cron ou manualmente):

```bash
# Limpar jobs completados com mais de 7 dias
redis-cli -h clinic-redis -p 6379 -a <SENHA> --scan --pattern "arq:result:*" | \
  xargs redis-cli -h clinic-redis -p 6379 -a <SENHA> DEL
```

### Atualização do Worker

1. Faça merge das mudanças no repositório
2. No Coolify, trigger novo deploy
3. Worker será atualizado com zero downtime (se múltiplas replicas)

## Boas Práticas

### Performance

- [ ] Use múltiplas replicas em produção
- [ ] Configure `ARQ_MAX_JOBS` baseado em carga real
- [ ] Monitor throughput e ajuste replicas conforme necessário

### Confiabilidade

- [ ] Configure health checks
- [ ] Ative restart automático (Coolify faz isso por padrão)
- [ ] Monitore logs para erros recorrentes
- [ ] Configure alarmes para métricas críticas

### Segurança

- [ ] Nunca exponha worker publicamente
- [ ] Use variáveis de ambiente para secrets
- [ ] Rotacione API keys periodicamente
- [ ] Limite acesso ao Redis apenas para backend/worker

## Próximos Passos

Após configurar o worker:
- Leia [BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md) para entender o funcionamento detalhado
- Configure monitoramento e alarmes
- Teste importação em produção
- Ajuste recursos baseado em uso real
