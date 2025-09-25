# Contexto
- Reorganizar navegação por papéis (COLABORADOR e ADMIN) com RBAC aplicado na UI e nas rotas.
- Substituir o dashboard único por visões separadas para operação e administração.
- Impedir que rotas administrativas sejam acessadas por usuários sem permissão, inclusive via URL direta.

# Escopo
- Implementação de guardas de rota e filtros de navegação por papel.
- Criação dos dashboards Operacional e Administrativo com KPIs, listas e placeholders para métricas.
- Redirecionamentos automáticos de `/dashboard` conforme o papel autenticado.
- Atualização da sidebar com grupos colapsáveis e breadcrumbs.
- Cobertura de testes unitários e de fluxo para garantir o RBAC.

# Tarefas
1. Criar constantes de papel e utilitários de resolução de perfil.
2. Implementar HOC `withRole` e componente de fallback 403 com redirecionamento.
3. Reestruturar layout autenticado, navegação agrupada e breadcrumbs.
4. Adicionar dashboards específicos para operação e administração com serviços de dados.
5. Atualizar rotas protegidas e redirecionamentos.
6. Implementar testes (sidebar por papel, bloqueio de rotas e snapshots).
7. Documentar decisões e riscos nesta ficha.

# Decisões
- **RBAC no front-end**: uso de HOC `withRole` integrado ao `PrivateRoute`, emitindo telemetria para bloqueios.
- **Navegação**: Sidebar dinâmica filtrada por papel, com grupos "Operação", "Cadastros" e "Administração".
- **Dashboards**: Serviços agregadores utilizando endpoints existentes (appointments, drivers, collectors, cars) com fallback seguro.
- **Acessibilidade**: foco programático em headings, botões com `aria-pressed`, feedbacks 403 e loaders com `role` apropriado.
- **Redirecionamento**: `/dashboard` utiliza `DashboardRedirect` baseado no papel resolvido do usuário.

# Checklist
- [x] Guardas de rota e navegação respeitando RBAC.
- [x] Dashboards separados com KPIs mínimos e placeholders amigáveis.
- [x] Sidebar agrupada com estados colapsáveis e breadcrumbs.
- [x] Bloqueio + redirect 403 ao acessar rotas sem permissão.
- [x] Testes unitários/e2e de navegação atualizados e snapshots.
- [x] Documentação desta ficha preenchida.

# Risks
- **Carga de dados**: agregações no front podem precisar de paginação maior; monitorar performance e considerar endpoints dedicados.
- **Sincronização de papéis**: divergências entre `user.role` e `is_admin` exigem validação contínua até padronização no backend.
- **Telemetria**: eventos client-side dependem de `window.analytics`; necessário revisar integração real em produção.
- **Acessos legacy**: rotas antigas que não passam pelo novo layout podem exigir guardas adicionais quando surgirem novas features.

