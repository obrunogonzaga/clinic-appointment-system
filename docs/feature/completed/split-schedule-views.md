# Estudo Técnico – Separação de Agendamentos (Atual vs Histórico)

## Contexto
Atualmente todos os agendamentos são exibidos em uma única tela/tabela, o que dificulta a visualização e o gerenciamento. O volume crescente de registros e o fato de ações críticas (cadastro manual, upload de planilhas, alteração de status) ficarem disponíveis para qualquer linha aumentam o risco operacional.
A proposta é dividir em duas visões distintas:
- **Visão Atual**: registros de hoje em diante.
- **Visão Histórica**: registros anteriores a hoje (D-1 para trás).

## Objetivo
Melhorar a usabilidade e o controle sobre os agendamentos, reduzindo risco de alterações indevidas em registros antigos. A segmentação também simplifica o raciocínio para suporte e facilita analisar métricas por contexto temporal.

## Opção Técnica Escolhida
**Opção 2 – Query Segmentada no Back-end**
- Implementar endpoints distintos ou parâmetros de filtro de data para trazer dois conjuntos de dados:
  - `current` → agendamentos >= hoje.
  - `history` → agendamentos < hoje.
- Benefícios:
  - Evita trazer todos os registros de uma vez, reduzindo payload e processamento no front-end.
  - Melhora a performance e abre espaço para paginações diferenciadas por contexto.
  - Facilita controle de regras de negócio em cada visão (p. ex. bloqueios no histórico).
  - Padroniza o contrato entre front-end e back-end, permitindo que futuras integrações reutilizem o mesmo critério temporal.

## Plano de Implementação
1. **Back-end**
   - Criar/ajustar endpoints com parâmetro `scope = [current | history]`.
   - Adicionar lógica de filtro por data diretamente na query, usando o início do dia UTC como corte.
   - Incluir validação para combinar filtros de data adicionais (`data_inicio`, `data_fim`) com o `scope`, retornando mensagens claras em casos conflitantes.
   - Retornar dados já segmentados para o front-end, mantendo paginação e metadados consistentes.
   - Registrar casos de importação com datas inválidas no log para facilitar troubleshooting.

2. **Front-end**
   - Criar abas/tabs para separar "Agendamentos Atuais" e "Histórico" utilizando estado compartilhado com o hook de busca.
   - Ajustar `AppointmentFilter` para enviar o parâmetro `scope` e invalidar o cache de queries ao alternar entre abas.
   - Exibir botões de ação (adicionar, importar, alterar status) **apenas** na visão atual, mantendo indicadores visuais da restrição na aba histórica.
   - Desabilitar ações na visão histórica e sinalizar o modo somente leitura nos componentes reutilizados (cards, tabela, agenda e calendário).
   - Mostrar toast resumindo inconsistências de importação (linhas com datas passadas) e oferecer link para baixar relatório completo caso necessário.

3. **Validação de Importação**
   - Pré-processar planilha de importação no serviço de domínio, separando linhas com `data_agendamento` anterior ao corte atual.
   - Caso haja registros no passado → bloquear importação desses itens, exibir toast com resumo e manter o arquivo sem persistência parcial.
   - Relatar no retorno do serviço o total de linhas rejeitadas por data para auditoria.

4. **Controle de Ações**
   - Implementar toggle de permissões baseado em data:
     - Datas >= hoje → habilitar ações.
     - Datas < hoje → somente leitura.
   - Replicar a regra no back-end (p. ex. evitar `PATCH` em registros históricos) para garantir consistência mesmo em chamadas diretas à API.
   - Documentar a política de bloqueio no manual de operações para alinhamento com equipes de atendimento.
