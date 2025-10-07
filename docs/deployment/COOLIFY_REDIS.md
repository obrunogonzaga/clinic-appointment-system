# Configuração de Redis no Coolify

Este guia descreve como configurar um serviço Redis no Coolify para uso com o sistema de background jobs do clinic-appointment.

## Visão Geral

O Redis é necessário para:
- Armazenamento de filas de jobs (via ARQ)
- Cache de resultados
- Gerenciamento de estado de workers

## Pré-requisitos

- Acesso ao painel do Coolify
- Permissões para criar databases no projeto

## Passos de Configuração

### 1. Criar Database Redis no Coolify

1. Acesse o painel do Coolify
2. Navegue até seu projeto: `clinic-appointment`
3. Vá para a seção **Databases**
4. Clique em **+ Add Database**
5. Selecione **Redis**

### 2. Configurar o Redis

Configure o Redis com as seguintes especificações:

**Configurações Básicas:**
- **Nome**: `clinic-redis`
- **Versão**: `7-alpine` (recomendado por ser leve e seguro)
- **Porta**: `6379` (padrão)

**Configurações Avançadas:**

```yaml
# Persistence (AOF - Append Only File)
appendonly: yes
appendfilename: "appendonly.aof"
appendfsync: everysec

# Memory Policy
maxmemory-policy: allkeys-lru

# Security
requirepass: <SUA_SENHA_FORTE>
```

**Importante**: Anote a senha configurada para uso nas variáveis de ambiente.

### 3. Configurar Variáveis de Ambiente

No painel do Coolify, configure as seguintes variáveis de ambiente para o backend e worker:

#### Para o Backend (clinic-backend)

Adicione ou atualize as variáveis:

```bash
REDIS_URL=redis://clinic-redis:6379
REDIS_PASSWORD=<SUA_SENHA_AQUI>
```

#### Para o Worker (clinic-worker)

As mesmas variáveis do backend:

```bash
REDIS_URL=redis://clinic-redis:6379
REDIS_PASSWORD=<SUA_SENHA_AQUI>
```

### 4. Configurar Network

Certifique-se de que backend e worker estão na mesma rede Docker que o Redis:

1. No Coolify, vá para a configuração de rede do projeto
2. Adicione `clinic-redis` à mesma rede dos outros serviços
3. Ou use a rede padrão do projeto que já conecta todos os serviços

### 5. Testar Conexão

Após deployment, teste a conexão com Redis:

```bash
# Via Coolify Console (Backend ou Worker)
redis-cli -h clinic-redis -p 6379 -a <SUA_SENHA> ping
# Deve retornar: PONG
```

## Monitoramento

### Verificar Status

No painel do Coolify:
1. Vá para **Databases** > **clinic-redis**
2. Verifique se o status está **Running**
3. Monitore logs para erros

### Comandos Úteis

Via Coolify Console:

```bash
# Verificar informação do servidor
redis-cli -h clinic-redis -p 6379 -a <SENHA> INFO

# Verificar memória usada
redis-cli -h clinic-redis -p 6379 -a <SENHA> INFO memory

# Listar keys (usar com cuidado em produção)
redis-cli -h clinic-redis -p 6379 -a <SENHA> KEYS "arq:*"

# Verificar jobs na fila
redis-cli -h clinic-redis -p 6379 -a <SENHA> LLEN "arq:queue:default"
```

## Troubleshooting

### Backend não consegue conectar ao Redis

**Sintoma**: Logs mostram "Connection refused" ou "Connection timeout"

**Solução**:
1. Verifique se Redis está rodando: vá ao painel do Coolify
2. Confirme que `REDIS_URL` está correto (deve ser `redis://clinic-redis:6379`)
3. Verifique se todos os serviços estão na mesma rede Docker
4. Teste conectividade: `ping clinic-redis` dentro do container do backend

### Autenticação falhando

**Sintoma**: "NOAUTH Authentication required" ou "invalid password"

**Solução**:
1. Verifique se `REDIS_PASSWORD` está configurado corretamente
2. Confirme que a senha no Redis match com a variável de ambiente
3. Se mudou a senha, reinicie backend e worker

### Memória cheia

**Sintoma**: "OOM command not allowed when used memory > 'maxmemory'"

**Solução**:
1. Aumente o limite de memória do Redis no Coolify
2. Configure `maxmemory-policy: allkeys-lru` para evict keys antigas
3. Limpe jobs antigos manualmente se necessário

### Jobs não sendo processados

**Sintoma**: Jobs ficam na fila mas não são executados

**Solução**:
1. Verifique se o worker está rodando (veja COOLIFY_WORKER.md)
2. Confirme que worker consegue conectar ao Redis
3. Verifique logs do worker para erros

## Backup e Recuperação

### Backup Manual

```bash
# Via Coolify Console (Redis container)
redis-cli -h localhost -p 6379 -a <SENHA> SAVE
# Arquivo será salvo em /data/dump.rdb
```

### Backup Automático

Configure no Coolify:
1. **Databases** > **clinic-redis** > **Backups**
2. Ative backups automáticos
3. Configure frequência (recomendado: diária)
4. Defina retenção (recomendado: 7 dias)

### Restaurar Backup

1. Pare o Redis no Coolify
2. Substitua o arquivo `/data/dump.rdb` pelo backup
3. Inicie o Redis novamente

## Segurança

### Checklist de Segurança

- [x] Senha forte configurada (`requirepass`)
- [x] Redis não exposto publicamente (apenas rede interna)
- [x] TLS/SSL configurado (se necessário)
- [x] Backups automáticos ativos
- [x] Monitoramento de uso de memória
- [x] Logs sendo coletados

### Recomendações

1. **Nunca** exponha Redis publicamente sem TLS
2. Use senhas fortes (mínimo 32 caracteres, alfanuméricos)
3. Rotacione senhas periodicamente
4. Monitore logs para tentativas de conexão não autorizadas

## Recursos Adicionais

- [Redis Official Docs](https://redis.io/docs/)
- [Coolify Docs - Databases](https://coolify.io/docs/databases)
- [ARQ Documentation](https://arq-docs.helpmanual.io/)

## Próximos Passos

Após configurar o Redis, prossiga para:
- [COOLIFY_WORKER.md](./COOLIFY_WORKER.md) - Configurar o worker ARQ
- [BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md) - Entender o sistema de jobs
