# Integração com Cal.com (Self-hosted)

## Contexto Atual
- **Agendamentos**: manipulação via FastAPI (`backend/src/presentation/api/v1/endpoints/appointments.py`) com importação de planilhas e cadastro manual.
- **Serviço de domínio**: `AppointmentService` coordena validações, sincronização de clientes e normalização em background (`backend/src/application/services/appointment_service.py`).
- **Persistência**: MongoDB através do `AppointmentRepository`, que já garante filtros e índices para status, tags e logística (`backend/src/infrastructure/repositories/appointment_repository.py`).
- **Frontend**: página `AppointmentsPage` controla filtros, KPIs, modais e sincronização com React Query (`frontend/src/pages/AppointmentsPage.tsx`).

## Objetivos de Integração
- Receber e processar automaticamente eventos do Cal.com (criação, atualização, cancelamento).
- Permitir autoagendamento via widget Cal.com dentro da aplicação, preservando experiência e autenticação existentes.
- Manter consistência bidirecional: alterações feitas internamente devem refletir no Cal.com quando aplicável.
- Registrar origem dos agendamentos e preservar metadados necessários (CPF, convênio, unidade, etc.).

## Mapeamento de Dados
- `booking.uid` → novo campo `calcom_booking_id` (idempotência e reconciliação).
- `booking.startTime`/`endTime` (UTC) → `data_agendamento` + `hora_agendamento` (após conversão de fuso).
- `booking.attendee.name/email/phone` → `nome_paciente`, e contatos para normalização.
- `eventType.team` ou campos customizados → `nome_unidade`, `nome_marca`.
- Inputs customizados (p.ex. CPF, convênio) → `cpf`, `nome_convenio`, `numero_convenio`.
- Tags/labels Cal.com → `tags` (`max_tags_per_appointment` respeitado).

## Backend
- Criar módulo `calcom_integration` com:
  - DTOs Pydantic para payloads de webhook.
  - Verificação HMAC do webhook (`CALCOM_WEBHOOK_SECRET`).
  - Serviço `CalComService`/`CalComClient` para chamadas REST/GraphQL (token de API).
  - Métodos de upsert em `AppointmentService` baseados em `calcom_booking_id` e atualização seletiva de campos.
- Expor rota `/api/v1/calcom/webhook` protegida (assinatura + rate limiting) e registrar no router público.
- Adicionar jobs periódicos (ARQ) para reconciliação com a API Cal.com (backfill de eventos perdidos).
- Ajustar DTOs de resposta para incluir origem e link Cal.com quando existir.

## Frontend
- Nova seção/rota para autoagendamento incorporando iframe/SDK do Cal.com, com pré-preenchimento opcional (e-mail, CPF) a partir do usuário logado.
- Destacar origem `Cal.com` na listagem (badges) e incluir ação “Abrir no Cal.com”.
- Tratar feedback em tempo real (polling ou webhooks via websocket) para refletir status confirmados/cancelados.
- Garantir que os filtros e KPIs considerem o novo campo de origem.

## Infraestrutura & DevOps
- Provisionar Cal.com self-host (docker-compose oficial) com Postgres + Redis.
- Configurar domínios/subdomínios, HTTPS e reverse proxy para expor o widget e webhooks de forma segura.
- Armazenar segredos (`CALCOM_WEBHOOK_SECRET`, `CALCOM_API_TOKEN`) nas variáveis de ambiente do backend e pipelines.
- Atualizar `render*.env`/`docker-compose` com containers e credenciais necessárias.

## Testes & Observabilidade
- Testes unitários: mocks para webhooks Cal.com, conversão de fuso e mapemento de campos.
- Testes de integração: fluxo de criação/cancelamento passando pelo FastAPI e ARQ.
- Frontend: testes de renderização do widget e sinalização da origem.
- Monitoramento: métricas de sucesso/falha de webhooks, logs estruturados e alertas para reconciliação.

## Riscos Conhecidos
- Divergência de timezone causando conflitos de agenda.
- Campos obrigatórios (CPF/convênio) ausentes no Cal.com exigem validações e custom fields obrigatórios.
- Webhooks perdidos exigem reconciliação periódica e persistência de histórico.
- Rate limits da API Cal.com em fluxos de sincronização massiva.

## Próximos Passos
1. Validar com stakeholders os campos obrigatórios e desenhar o mapeamento final Cal.com ↔ domínio.
2. Subir ambiente Cal.com local, configurar webhooks e tokens, validar payloads reais.
3. Implementar webhook + reconciliação, adicionar widget no frontend, executar `make test-backend` e `npm test` cobrindo novos fluxos.
