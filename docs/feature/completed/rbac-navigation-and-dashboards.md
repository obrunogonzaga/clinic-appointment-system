# Contexto
- Navegação atual não usa RBAC e expõe menus/telas de administração para qualquer usuário logado.
- Dashboard único mistura visão operacional com demandas estratégicas e não atende necessidades distintas de colaboradores e administradores.
- Ausência de guardas nas rotas permite acesso direto via URL a telas sensíveis.

# Escopo
- Reorganizar rotas e navegação lateral agrupando itens por contexto (Operação, Cadastros, Administração).
- Implementar controle de acesso por papel (COLABORADOR, ADMIN) em rotas, menu e redirecionamentos.
- Criar dashboards dedicados para operação e administração com KPIs e placeholders conectáveis a serviços futuros.
- Atualizar testes e documentação garantindo que fluxo colaborador/admin esteja coberto.

# Tarefas
- [x] Definir constantes de papel, utilitários de sessão e guard `withRole`.
- [x] Reestruturar `App` com layout novo, rotas nomeadas e redirecionamento `/dashboard` por papel.
- [x] Refatorar sidebar para usar grupos colapsáveis com RBAC aplicado.
- [x] Construir Dashboard Operacional com filtros rápidos, KPIs, próximos agendamentos e atalhos.
- [x] Construir Dashboard Administrativo com visão estratégica (KPIs, tendência, top unidades, utilização, alertas).
- [x] Criar tela 403 amigável com redirect automático.
- [x] Atualizar serviços (DashboardService) para fornecer dados e fallback seguro.
- [x] Escrever testes unitários para RBAC na navegação e atualizar script de testes.
- [x] Documentar decisões e riscos.

# Decisões
- Adotado `APP_ROUTES` como fonte única de rotas, breadcrumbs e metadados de navegação.
- `withRole` redireciona para `/403` mantendo histórico original em `location.state` e `ForbiddenPage` faz redirect automático para `/dashboard` após 4s.
- Serviço de dashboard tenta buscar dados reais e faz fallback controlado quando API não responde, permitindo troca futura da fonte.
- Sidebar mantém estado de grupos colapsados independente do estado global da barra lateral, melhorando UX em telas menores.
- Script de testes usa `esbuild` com múltiplos entrypoints para compilar novos testes de RBAC.

# Checklist
- [x] Rotas protegidas com RBAC e redirect default por papel.
- [x] Sidebar exibe itens conforme papel e oculta Administração para colaboradores.
- [x] Dashboards possuem conteúdo mínimo solicitado com placeholders amigáveis para estados vazios.
- [x] Tela 403 acessível, com foco e redirect automático.
- [x] Testes unitários de navegação + smoke existentes passam.
- [x] Documentação atualizada.

# Risks
- Dados mockados podem divergir das métricas reais até integração com APIs específicas de analytics.
- Novos caminhos (`/dashboard/operacao`, `/dashboard/admin`) precisam ser adotados por deep links ou favoritos de usuários internos.
- Mudança no script de testes exige que novos testes sejam listados no bundle; futuras adições devem atualizar entrypoints ou migrar para glob dinâmico.
- Possível necessidade de ajustar filtros da API de agendamentos para suportar períodos semanais assim que endpoint aceitar intervalos.
