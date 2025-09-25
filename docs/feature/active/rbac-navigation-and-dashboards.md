# RBAC navigation and dashboards

## Contexto
- Organização da navegação atual não respeita claramente os papéis de acesso e apresenta um único dashboard genérico.
- Necessidade de separar visão operacional (colaboradores) da visão estratégica (admin) garantindo consistência de permissões.
- Exigência de aplicar RBAC tanto na UI (menus/botões) quanto nas rotas para evitar acessos diretos.

## Escopo
- Reestruturar o layout autenticado com sidebar agrupada, breadcrumbs e foco acessível.
- Criar guardas de rota baseadas em papéis (COLABORADOR/ADMIN) reutilizáveis na aplicação.
- Implementar dashboards distintos para operação e administração com KPIs, listas e placeholders de métricas.
- Atualizar roteamento `/dashboard` para redirecionar automaticamente conforme o papel autenticado.
- Cobrir cenários críticos com testes unitários de navegação/guards e ajustar infraestrutura de testes.

## Tarefas
- [x] Criar constantes de papel, utilitários de sessão e HOC `withRole`.
- [x] Refatorar `App.tsx` para usar layout com rotas aninhadas e guards.
- [x] Reescrever sidebar com grupos “Operação”, “Cadastros” e “Administração” com colapsáveis.
- [x] Desenvolver `OperationDashboardPage` e `AdminDashboardPage` com serviços mockados.
- [x] Implementar página 403 com redirect controlado e breadcrumbs globais.
- [x] Atualizar script de testes para compilar todos os arquivos `*.test.tsx` e adicionar novos cenários RBAC.

## Decisões
- Utilizado `withRole` baseado em HOC para manter compatibilidade com componentes existentes, evitando alteração profunda em `PrivateRoute`.
- Serviços de dashboard retornam mocks determinísticos via `dashboardService`, permitindo troca futura pela API real sem refatorar componentes.
- Breadcrumbs renderizados a partir do `pathname` para evitar dependência manual por página.
- Testes escritos com `node:test` e `react-dom/server` aproveitando infraestrutura existente sem adicionar bibliotecas externas.

## Checklist
- [x] RBAC aplicado na sidebar, rotas e botões críticos.
- [x] `/dashboard` redireciona dinamicamente conforme papel.
- [x] Dashboards possuem KPIs mínimos, listas/atalhos e estados vazios.
- [x] Página 403 acessível com foco e redirect.
- [x] Testes unitários atualizados e rodando via `npm run test`.

## Risks
- Serviços de dashboard usam mocks; integração futura precisa alinhar formatos de dados reais.
- Possível necessidade de ajustes nos filtros/atalhos quando endpoints definitivos estiverem disponíveis.
- Redirecionamento automático em `/403` depende de `window`, já protegido para SSR, porém deve ser reavaliado em ambientes sem browser.
