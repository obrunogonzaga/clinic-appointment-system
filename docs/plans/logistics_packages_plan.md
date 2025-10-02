# Plano de Pacotes Logísticos

## Visão Geral
- Introduzir uma entidade de **pacote logístico** que agrupa carro, motorista e coletora em uma única combinação reutilizável.
- Permitir que agendamentos novos ou existentes selecionem um pacote para preencher automaticamente os campos logísticos.
- Disponibilizar uma tela administrativa simples para cadastrar e acompanhar os pacotes.

## Trilhas de Trabalho
1. **Back-end**
   - [x] Modelar entidade, repositório e serviço para pacotes logísticos.
   - [x] Expor endpoints REST para CRUD básico e listagem de ativos.
   - [x] Ajustar o serviço de agendamentos para aceitar `logistics_package_id` e preencher trio automaticamente.
2. **Front-end**
   - [x] Disponibilizar cadastro e listagem de pacotes logísticos.
   - [x] Permitir seleção de pacote na criação de agendamentos.
   - [x] Permitir seleção/alteração de pacote nos detalhes do agendamento, mantendo possibilidade de personalização manual.
3. **Experiência do Usuário**
   - [x] Exibir nome do pacote e trio designado em cartões/tabelas de agendamento.
   - [ ] Construir painel de disponibilidade cruzando agenda e pacotes (próxima etapa).

## Progresso
- Entidade, serviço e API REST implementados no back-end, com validações de integridade dos vínculos.
- Tela de "Pacotes Logísticos" disponível no menu principal para criação, edição de status e visualização.
- Fluxos de criação e edição de agendamento recebem o pacote e preenchem automaticamente motorista, coletora e carro.
- Próxima prioridade: evoluir o painel de disponibilidade para suportar a visualização combinada (em aberto neste plano).
