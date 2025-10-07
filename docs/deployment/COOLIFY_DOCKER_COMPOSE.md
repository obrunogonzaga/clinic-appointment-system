# Deploy completo no Coolify com Docker Compose

Este guia resume como usar o arquivo `docker-compose.coolify.yml` para publicar **backend**, **frontend**, **jobs ARQ** e serviços de suporte (MongoDB, Redis, MinIO) em um único recurso do Coolify.

## Visão geral

- O compose usa as imagens de produção e remove os bind mounts para garantir builds imutáveis.
- Todos os serviços compartilham a rede `clinic-coolify-network`, permitindo que Coolify exponha somente o que for necessário (normalmente backend e frontend).
- Variáveis sensíveis são carregadas via `env_file` (`.env.coolify`). Use `./.env.coolify.example` como referência e aplique os valores diretamente no Coolify (o arquivo real está .gitignore).

## Pré-requisitos

1. Repositório conectado ao Coolify com acesso à branch que contém `docker-compose.coolify.yml`.
2. Secrets para MongoDB, Redis, MinIO/Cloudflare R2, JWT e demais integrações salvos no Coolify.
3. (Opcional) Serviços externos existentes (ex.: Mongo Atlas). Neste caso, remova/ignore os serviços `mongodb`, `redis` ou `minio` e ajuste as URLs de conexão.

## Estrutura do compose

```
docker-compose.coolify.yml
├─ mongodb            # Banco local opcional
├─ redis              # Fila/cache
├─ minio              # Armazenamento S3 compatível
├─ backend            # API FastAPI (produção)
├─ worker             # Processador ARQ (usa mesma imagem do backend)
└─ frontend           # Build estático hospedado por Nginx
```

- Volumes persistentes: `clinic-mongodb-data`, `clinic-redis-data`, `clinic-minio-data`.
- Health checks configurados para MongoDB, Redis, MinIO e API; o worker herda a política de restart do Docker.

## Configuração das variáveis

1. Preencha um arquivo local `.env.coolify` (já listado no `.gitignore`) usando `.env.coolify.example` como base e copie o conteúdo para a aba **Environment Variables** do recurso Coolify:
   - Banco: `MONGODB_URL`, `DATABASE_NAME`, `MONGO_INITDB_*`.
   - Redis: `REDIS_URL`, `REDIS_PASSWORD`.
   - Backend/Worker: `ENVIRONMENT=production`, `DEBUG=false`, `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `FRONTEND_URL`, toggles de normalização e credenciais do OpenRouter.
   - Armazenamento: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `S3_ENDPOINT` ou credenciais do R2.
   - Frontend: `BACKEND_URL` (usado pelo Nginx para proxy das chamadas).
2. Remova qualquer variável que não precisar (Coolify aceita comentários iniciando com `#`).
3. Se utilizar services externos (ex.: Mongo Atlas), mantenha apenas `MONGODB_URL`/`DATABASE_NAME` e desmarque os serviços correspondentes na tela de deploy.

## Passo a passo de deploy

1. No painel do Coolify, clique em **Add Resource → Docker Compose**.
2. Aponte para o repositório e branch corretos e informe `docker-compose.coolify.yml` como arquivo.
3. Na etapa “Services”, selecione os serviços desejados (mínimo: `backend`, `frontend`, `worker`; selecione `mongodb`, `redis`, `minio` apenas se forem gerenciados pelo Compose).
4. Defina CPU/RAM individual por serviço conforme a necessidade (padrão sugerido: backend 0.5 CPU/512 MB, worker 0.5 CPU/512 MB, frontend 0.25 CPU/256 MB).
5. Configure os health checks:
   - Backend: HTTP `GET /health` na porta 8000.
   - Worker: comando `ps aux | grep "python workers.py" | grep -v grep` (opcional, para alertas).
6. Exponha os serviços que precisam de acesso externo:
   - Backend: porta 8000 (ou configure um domínio/API no Coolify).
   - Frontend: porta 80 (HTTP).
   - MinIO: exponha 9000/9001 somente se precisar do console público.
7. Clique em **Deploy** e acompanhe os logs. O primeiro deploy baixa imagens, builda backend/frontend e inicializa as migrations (MongoDB não requer migração manual).

## Pós-deploy e monitoramento

- Verifique a API em `/health` e o frontend na URL configurada.
- Confirme no Redis que os workers estão consumindo jobs (fila `arq:*`).
- Configure alertas no Coolify para reinícios frequentes ou memória >90%.
- Para atualizar, basta enviar mudanças para a branch monitorada e acionar **Redeploy**.

## Escalonamento

- Horizontal: aumente `replicas` do serviço `worker` diretamente no Coolify quando houver fila grande.
- Vertical: ajuste CPU/RAM na aba de recursos dos serviços afetados.
- Manter compose único simplifica o deploy, mas todos os serviços serão reconstruídos juntos; para rollbacks granulares, use as versões anteriores gerenciadas pelo Coolify.

## Recursos adicionais

- [BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md) — visão detalhada dos fluxos assíncronos.
- [COOLIFY_WORKER.md](./COOLIFY_WORKER.md) — guia com troubleshooting e tuning do ARQ (aplica-se mesmo usando o compose unificado).
- [COOLIFY_REDIS.md](./COOLIFY_REDIS.md) — dicas extras para hardening do Redis em produção.
