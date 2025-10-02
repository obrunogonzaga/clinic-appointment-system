# Plano de Implementação — Criação Manual de Agendamentos

## Objetivo
- Permitir que usuários cadastrem agendamentos manualmente via interface web, mantendo consistência com os dados importados via planilha e garantindo validações de negócio já adotadas.

## Etapas Propostas

1. **Alinhamento e Descoberta**
   - Revisar com o time o fluxo desejado (quem pode criar, permissões futuras, comportamento esperado do status inicial).
   - Mapear todos os campos obrigatórios e opcionais utilizados hoje (`nome_marca`, `nome_unidade`, `nome_paciente`, `data_agendamento`, `hora_agendamento`, `tipo_consulta`, `status`, `telefone`, `carro`, `observacoes`, `driver_id`, `collector_id`, `numero_convenio`, `nome_convenio`, `carteira_convenio`).
   - Validar valores permitidos para status (lista definida na entidade `Appointment`) e quais opções devem aparecer no formulário.
   - Identificar fontes de dados para selects (`filterOptions`, `activeDrivers`, `activeCollectors`) e se campos como unidades/marcas precisam de auto completar ou lista fixa.

2. **Backend — Caso de Uso e Endpoint**
   - Adicionar método dedicado em `AppointmentService` para criar um agendamento único reutilizando validações da entidade (`Appointment`) e garantindo normalização (hora, telefone, status).
   - Garantir que o repositório Mongo implemente `create` para persitir um único registro (confirmar contrato atual e ajustar se necessário).
   - Expor rota `POST /appointments` em `appointments.py` utilizando `AppointmentCreateDTO` como input e `AppointmentResponseDTO` como output; incluir tratamento de erros amigáveis (400 para validações, 409 para duplicados, 500 para falhas internas).
   - Revisar dependências (injeção com `get_appointment_service`) e adicionar logs/metadados relevantes.
   - Cobrir com testes `pytest`: unidade do serviço (happy path, validação de status/hora/telefone) e teste de integração do endpoint simulando o fluxo completo.

3. **Frontend — Camada de Dados**
   - Criar tipo `AppointmentCreateRequest` espelhando `AppointmentCreateDTO` e avaliar defaults (ex.: `status` = `Confirmado`).
   - Estender `appointmentAPI` com método `createAppointment` (`POST /appointments`) e definir invalidações necessárias no `react-query` (`appointments`, `filterOptions`, `dashboardStats`).
   - Centralizar helpers de status/opções em `utils/appointmentViewModel` ou criar util dedicado para evitar duplicação entre formulário e filtros.
   - Garantir tratamento de erros da API com mensagens amigáveis e feedback consistente (toast/alerta).

4. **Frontend — UI/UX**
   - Adicionar botão "Adicionar Agendamento" no header da `AppointmentsPage`, ao lado do upload, considerando estados responsivos (mobile/desktop).
   - Implementar modal de formulário reutilizando padrões existentes (ver `PublicRegister` para referência de formulários com `react-hook-form` ou padrão usado no projeto).
   - Estruturar o formulário em seções lógicas: Dados principais, Contato, Logística (motorista/coletora/carro), Convênio, Observações.
   - Aplicar validações client-side alinhadas com o backend (formatos de data/hora, telefone, obrigatoriedade) e máscaras onde fizer sentido.
   - Preencher selects com dados vindos de `filterOptions`, `driversData`, `collectorsData`; considerar autocomplete para evitar listas extensas.
   - Exibir estado de loading enquanto a submissão é processada e fechar a modal automaticamente ao sucesso.

5. **Integração e Fluxo**
   - Após criação bem-sucedida, atualizar a listagem atual respeitando filtros ativos (usar `invalidateQueries` ou atualizar cache manualmente para experiência imediata).
   - Garantir que novas entradas apareçam corretamente em todas as visualizações (`cards`, `table`, `calendar`, `agenda`).
   - Atualizar KPIs e demais dashboards dependentes (invalidar queries relevantes ou atualizar dados localmente).

6. **Testes Frontend e QA**
   - Implementar testes unitários do formulário (validações, campos obrigatórios) utilizando React Testing Library.
   - Acrescentar testes de integração e2e (quando prático) cobrindo criação manual e exibição nas principais visualizações.
   - Realizar QA manual: cenários com campos mínimos, com dados completos, tratamento de erros da API, compatibilidade mobile.

7. **Documentação e Handoff**
   - Atualizar `docs/` com instruções de uso da nova funcionalidade (incluindo pré-requisitos e mensagens de erro comuns).
   - Registrar alterações relevantes no changelog/PROGRESS_AGENDAMENTOS.md e alinhar com o time de suporte/operacional.
   - Preparar passo-a-passo de validação pós-deploy (monitoramento de logs, métricas de criação manual, rollback plan).

