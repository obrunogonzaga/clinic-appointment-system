# Sistema de Background Jobs - Documentação Técnica

Este documento explica o funcionamento do sistema de background jobs para normalização de dados de agendamentos.

## Visão Geral

O sistema utiliza ARQ (Async Redis Queue) para processar tarefas de normalização de forma assíncrona, permitindo que importações de Excel sejam rápidas mesmo quando há muitos dados para processar.

## Arquitetura

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React + TypeScript)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│                    (FastAPI + Python)                        │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  AppointmentService                                   │  │
│  │  - create_appointment()                               │  │
│  │  - import_appointments_from_excel()                   │  │
│  │  └─▶ _enqueue_normalization() ───┐                   │  │
│  └──────────────────────────────────│───────────────────┘  │
│                                     │                        │
│  ┌──────────────────────────────────▼───────────────────┐  │
│  │  TaskService                                          │  │
│  │  - enqueue_normalization(appointment_id)             │  │
│  │  - get_job_status(job_id)                            │  │
│  └──────────────────────────────────┬───────────────────┘  │
└────────────────────────────────────┬┴──────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────┐
                          │      Redis       │
                          │   (Message Queue)│
                          └────────┬─────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      ARQ Worker                              │
│                    (Background Process)                      │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  normalize_appointment(appointment_id)                │  │
│  │  1. Fetch appointment from MongoDB                    │  │
│  │  2. Call OpenAI for address normalization            │  │
│  │  3. Call OpenAI for document normalization           │  │
│  │  4. Update appointment with normalized data          │  │
│  │  5. Update normalization_status field                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │       MongoDB          │
                      │  (Appointments Updated)│
                      └────────────────────────┘
```

## Fluxo de Dados

### 1. Importação de Excel

```
1. User uploads Excel file
   ↓
2. ExcelParserService parses file (sync)
   → Creates Appointment entities
   → NO normalization at this stage
   ↓
3. AppointmentService saves appointments to MongoDB
   ↓
4. For each appointment:
   AppointmentService._enqueue_normalization()
   → TaskService.enqueue_normalization(appointment_id)
   → Job added to Redis queue
   → appointment.normalization_status = "pending"
   ↓
5. Response sent to frontend immediately
   → Import complete in < 3 seconds
```

### 2. Background Processing

```
ARQ Worker (running continuously):
   ↓
1. Pick job from Redis queue
   ↓
2. normalize_appointment(appointment_id) executed
   ↓
3. Update appointment.normalization_status = "processing"
   ↓
4. If endereco_completo exists:
   → Call OpenAI API for address normalization
   → Save to appointment.endereco_normalizado
   ↓
5. If documento_completo exists:
   → Call OpenAI API for document parsing
   → Save to appointment.documento_normalizado
   → Extract CPF and RG
   ↓
6. Update appointment:
   → normalization_status = "completed" (or "failed")
   → normalization_error = error message (if failed)
   ↓
7. Job result saved to Redis (kept for 1 hour)
```

## Entidades e Campos

### Appointment Entity

Novos campos adicionados para tracking:

```python
class NormalizationStatus(str, Enum):
    PENDING = "pending"       # Job enqueued, waiting to be processed
    PROCESSING = "processing" # Currently being normalized
    COMPLETED = "completed"   # Successfully normalized
    FAILED = "failed"         # Normalization failed
    SKIPPED = "skipped"       # No data to normalize or disabled

class Appointment(Entity):
    # ... existing fields ...

    # Background normalization tracking
    normalization_status: NormalizationStatus = NormalizationStatus.PENDING
    normalization_job_id: Optional[str] = None  # ARQ job ID
    normalization_error: Optional[str] = None   # Error message if failed

    # Normalized data (populated by worker)
    endereco_normalizado: Optional[Dict] = None
    documento_normalizado: Optional[Dict] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
```

## APIs e Endpoints

### Job Status Monitoring

```http
GET /api/v1/jobs/{job_id}/status
Authorization: Bearer <token>

Response:
{
  "success": true,
  "message": "Status do job obtido com sucesso",
  "job": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "complete",        // queued, in_progress, complete, failed
    "enqueue_time": "2025-01-01T10:00:00Z",
    "start_time": "2025-01-01T10:00:05Z",
    "finish_time": "2025-01-01T10:00:15Z",
    "result": {
      "success": true,
      "appointment_id": "...",
      "fields_normalized": ["endereco_normalizado", "documento_normalizado"]
    }
  }
}
```

## Configuração

### Variáveis de Ambiente

#### Backend

```bash
# Redis connection
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your-password-here

# Normalization features
ADDRESS_NORMALIZATION_ENABLED=true
DOCUMENT_NORMALIZATION_ENABLED=true

# OpenAI/OpenRouter API
OPENAI_API_KEY=your-api-key-here
```

#### Worker

```bash
# Same as backend, plus:
ARQ_MAX_JOBS=10          # Max concurrent jobs per worker
ARQ_JOB_TIMEOUT=300      # Job timeout in seconds (5 min)
ARQ_KEEP_RESULT=3600     # Keep job results for 1 hour
```

### Worker Settings (workers/config.py)

```python
class WorkerSettings:
    max_jobs = 10           # Max concurrent jobs
    job_timeout = 300       # 5 minutes timeout
    keep_result = 3600      # Keep results for 1 hour
    max_tries = 3           # Retry failed jobs up to 3 times
```

## Monitoramento

### Status dos Jobs

Verifique status de normalização:

```sql
-- MongoDB query
db.appointments.find({
  normalization_status: "pending"
}).count()

-- Por status
db.appointments.aggregate([
  {
    $group: {
      _id: "$normalization_status",
      count: { $sum: 1 }
    }
  }
])
```

### Métricas Redis

```bash
# Jobs na fila
redis-cli LLEN "arq:queue:default"

# Jobs em processamento
redis-cli KEYS "arq:job:*:processing"

# Jobs completados (últimos resultados)
redis-cli KEYS "arq:result:*"
```

### Logs do Worker

```bash
# Logs mostram:
[2025-01-01 10:00:15] INFO Starting normalization for appointment 550e8400...
[2025-01-01 10:00:16] INFO Normalizing address for appointment 550e8400...
[2025-01-01 10:00:18] INFO Address normalized for appointment 550e8400...
[2025-01-01 10:00:19] INFO Normalizing documents for appointment 550e8400...
[2025-01-01 10:00:21] INFO Documents normalized for appointment 550e8400...
[2025-01-01 10:00:21] INFO Normalization completed successfully for 550e8400
```

## Tratamento de Erros

### Retry Policy

Jobs falhados são automaticamente retried:

1. Primeira falha: retry após 60 segundos
2. Segunda falha: retry após 120 segundos
3. Terceira falha: marcado como `failed` permanentemente

### Tipos de Erro

#### Timeout

```python
# Se job exceder ARQ_JOB_TIMEOUT (300s)
→ Status: failed
→ Error: "Job timeout exceeded"
→ Não retried automaticamente
```

#### API Error (OpenAI)

```python
# Se OpenAI API falhar
→ Retry: sim (até 3 vezes)
→ Backoff: exponential (60s, 120s)
→ Final status: failed se todas as tentativas falharem
```

#### Network Error

```python
# Se Redis/MongoDB inacessível
→ Retry: sim
→ Defer: 60 seconds
→ Status: failed após max_tries
```

## Performance

### Benchmarks

Ambiente de teste: 1 worker, 1 core CPU, 1GB RAM

| Cenário | Throughput | Latência Média |
|---------|------------|----------------|
| Normalização de endereço | 20-30 jobs/min | 2-3s por job |
| Normalização de documento | 20-30 jobs/min | 2-3s por job |
| Ambos (endereço + documento) | 15-20 jobs/min | 4-6s por job |

### Otimizações

#### Horizontal Scaling

```yaml
# docker-compose.yml
worker:
  replicas: 3  # 3 workers paralelos
  # Throughput: 3x
```

#### Batch Processing

Para importações muito grandes:

```python
# Enfileirar em lotes
BATCH_SIZE = 50
for batch in chunks(appointments, BATCH_SIZE):
    await asyncio.gather(*[
        task_service.enqueue_normalization(apt.id)
        for apt in batch
    ])
    await asyncio.sleep(1)  # Evita sobrecarga
```

## Troubleshooting

### Jobs não processados

**Problema**: Jobs ficam em `pending` indefinidamente

**Diagnóstico**:
```bash
# Verificar worker rodando
ps aux | grep "python workers.py"

# Verificar conexão Redis
redis-cli -h redis -p 6379 PING
```

**Solução**: Reiniciar worker

### Jobs falhando consistentemente

**Problema**: Muitos jobs com status `failed`

**Diagnóstico**:
```bash
# Ver erros nos logs
docker logs worker-container

# Verificar appointments com erro
db.appointments.find({
  normalization_status: "failed"
}).limit(10)
```

**Soluções**:
1. Verificar OpenAI API key
2. Verificar rate limits da API
3. Aumentar timeout se necessário

### Memory leak

**Problema**: Worker usando cada vez mais RAM

**Diagnóstico**:
```bash
# Monitor de memória
docker stats worker-container
```

**Solução**: Configurar restart policy para reiniciar worker periodicamente

## Manutenção

### Limpeza Regular

Execute mensalmente:

```bash
# Limpar jobs antigos do Redis
redis-cli --scan --pattern "arq:result:*" | xargs redis-cli DEL

# Reprocessar jobs falhados (se necessário)
db.appointments.updateMany(
  { normalization_status: "failed" },
  { $set: { normalization_status: "pending", normalization_job_id: null } }
)
```

### Monitoring Dashboard

Métricas recomendadas:

1. **Queue Size**: Número de jobs pendentes
2. **Processing Rate**: Jobs/minuto
3. **Error Rate**: % de jobs falhados
4. **Average Latency**: Tempo médio de processamento
5. **Worker Health**: CPU, RAM, status

## Recursos Adicionais

- [ARQ Documentation](https://arq-docs.helpmanual.io/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## Changelog

| Data | Versão | Mudanças |
|------|--------|----------|
| 2025-10-01 | 1.0.0 | Implementação inicial do sistema de background jobs |
