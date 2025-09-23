# Progresso - Gerenciamento de Agendamentos

## Checklist
- [x] Varredura de arquitetura e anotações no PROGRESS_AGENDAMENTOS.md
- [x] Botão “Importar Excel” + Modal com dropzone
- [x] Drag & drop global (overlay)
- [x] Checkbox “Substituir…” e integração com fluxo de upload existente
- [x] Barra de filtros + atalhos de data + busca nome/CPF
- [x] KPIs (Total/Confirmados/Pendentes+Cancelados)
- [x] Toggle Cards/Lista
- [x] Cards: mostrar CPF e Plano
- [x] Tabela: colunas CPF e Plano
- [x] A11y (focus, ESC, aria, tab trap)
- [x] Testes smoke/interação (abrir modal, trocar views, aplicar filtro)
- [x] Atualização do PROGRESS_AGENDAMENTOS.md com evidências

## Arquitetura & Convenções (anotações iniciais)
- Frontend em React + Vite, TypeScript, TailwindCSS; estado remoto via TanStack Query; formulários e componentes com Heroicons.
- Página de agendamentos (`frontend/src/pages/AppointmentsPage.tsx`) consome serviços expostos em `services/api.ts` e reutiliza componentes em `components/Appointment*`.
- Upload atual usa `FileUpload` com `react-dropzone`; filtros ficam em `AppointmentFilters`; visualizações disponíveis: cards, calendário e agenda.
- Design system central em `components/ui` (Modal, Badge, Table, etc.); preferir estes componentes antes de criar novos.
- Tipos compartilhados residem em `src/types`; utilidades de formatação em `src/utils` (ex.: `dateUtils`, `statusColors`).

## Plano de trabalho
1. Substituir dropzone inline por botão primário que aciona modal e mover dropzone para dentro do modal com reutilização do serviço existente.
2. Implementar overlay global de drag & drop e checkbox de substituição mantendo headers/rota atuais.
3. Compactar barra de filtros adicionando atalhos de data rápidos e campo de busca local por nome/CPF.
4. Calcular KPIs locais com base nos agendamentos filtrados e exibir cards responsivos.
5. Introduzir toggle Cards/Lista preservando paginação/ações e expor CPF/Plano em ambas visualizações via adaptador.
6. Reforçar acessibilidade (focus trap, ESC, aria) e cobrir com testes smoke/interação; atualizar este arquivo com evidências.

## Decisões & Pendências
- Busca por nome/CPF operando apenas no front-end; API permanece inalterada.
- Adaptador `toAppointmentViewModel` criado para mascarar CPF e montar rótulo do plano com campos existentes.
- Toggle ampliado para incluir visualização em tabela, mantendo calendário/agenda originais.
- Modal agora usa `Modal` do design system com trap de foco; revisar contrastes e aria após testes.
- Testes automatizados rodam via `npm test` usando `esbuild` + `node:test` (sem dependências extras).
- Pendente: registrar evidências finais (prints/resultados) e capturar status do lint com falsos positivos herdados.
- Layout ajustado para botões/atalhos arredondados, KPIs minimalistas e tabela mais próxima do mock fornecido.

## Testes manuais (planejados)
1. Abrir "Gerenciamento de Agendamentos" → clicar em “Importar Excel” → modal deve focar o botão primário → selecionar arquivo válido e enviar (fluxo atual).
2. Arrastar arquivo sobre a página → overlay global aparece → soltar para iniciar upload e receber feedback.
3. Aplicar filtros (unidade/marca/status/data) e atalhos rápidos → resultados atualizam conforme esperado.
4. Usar busca por nome/CPF → lista/cards filtram localmente.
5. Alternar entre Cards ↔ Lista ↔ outras visualizações existentes → campos de CPF/Plano visíveis.
6. Validar acessibilidade: fechar modal com ESC, foco contido no modal e restaurado ao fechar.

## Notas de Acessibilidade
- Garantir foco inicial no primeiro elemento interativo do modal e trap de tab até o fechamento.
- Overlay de dropzone com texto e contraste adequados; só fica visível enquanto há `dragenter` com arquivos.
- Toggle com `aria-pressed`, checkbox e controles de filtros com `label` explícito.
- Modal impede scroll de fundo, fecha com ESC e devolve foco ao elemento anterior.

## Evidências & Links
- PR: _pendente_
- Commits: _pendente_
- Capturas: _pendente_
- Testes: `npm test` (ok - smoke suite)
- Lint: `npm run lint` (falhou em pendências pré-existentes fora do escopo desta feature)
