# Plano de Implementação: Tags em Agendamentos

## Backend
- [x] Definir entidade `Tag` em `backend/src/domain` com atributos `id`, `name`, `color`, `is_active`, timestamps e exceções adequadas para conflitos/soft-delete.
- [x] Criar migração e modelos ORM em `infrastructure/persistence` incluindo relação muitos-para-muitos `AppointmentTag`, índices e cascatas.
- [x] Estender repositórios e serviços em `application` para CRUD completo, busca paginada, validação de nomes únicos e limite de tags por agendamento; adaptar casos de uso de criação/edição de agendamento para aceitar tags existentes ou novas.
- [x] Expor endpoints REST em `presentation` (`/tags` CRUD, `/appointments` com array de tags) com schemas Pydantic, normalização de nomes e políticas de permissão (admins gerenciam tags).
- [x] Cobrir regras de negócio com testes em `backend/tests` para validações, soft-delete, criação em lote e cenários de permissão.

## Frontend
- [x] Atualizar formulário de agendamento em `frontend/src/pages/appointments` para suportar multiseleção de tags, autocomplete, criação inline (quando permitido) e chips coloridos; alinhar `services/appointments`.
- [x] Implementar tela de gestão de tags em `frontend/src/pages/tags` com listagem, filtros, paginação e ações de criar/editar/excluir usando componentes reutilizáveis em `components/tags`.
- [x] Estender `services/tags` para CRUD, normalização de payloads e tratamento de erros; integrar com cache/global state (ex.: React Query) e sincronizar com o formulário de agendamento.
- [x] Ajustar roteamento e navegação (menu, breadcrumbs, guardas) para expor gestão de tags apenas a usuários autorizados.
- [x] Adicionar testes unitários e de página para seleção de tags e fluxos CRUD.

## UX/UI
- [x] Implementar autocomplete com pesquisa incremental, destaque de tags recentes/favoritas e criação rápida quando não encontradas.
- [x] Garantir visual consistente: seletor de cor com pré-visualização, contraste acessível e chips responsivos (colapso em mobile).
- [x] Aplicar limites claros (ex.: máximo 5 tags por agendamento) com contador e mensagens imediatas de feedback.
- [x] Tratar estados vazios/erros na gestão de tags com mensagens orientativas e CTAs para criar novas tags.

## Pontos de Atenção
- [x] Assegurar transações ao criar agendamento com novas tags, evitando duplicidade via locks ou validação atômica.
- [x] Validar permissões: apenas perfis autorizados podem criar/alterar/excluir tags; demais usuários apenas selecionam existentes.
- [x] Considerar performance: paginação, caching e debounce no autocomplete para suportar grandes volumes de tags.
- [x] Sanitizar entradas (trim, case-insensitive), validar formato de cor hex, impedir nomes duplicados e planejar migração para tags já existentes/inativas.
