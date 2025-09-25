# Estudo Técnico – Separação de Agendamentos (Atual vs Histórico)

## Contexto
Atualmente todos os agendamentos são exibidos em uma única tela/tabela, o que dificulta a visualização e o gerenciamento.
A proposta é dividir em duas visões distintas:
- **Visão Atual**: registros de hoje em diante.
- **Visão Histórica**: registros anteriores a hoje (D-1 para trás).

Essa segmentação precisa considerar tanto a camada de dados quanto a experiência de uso, garantindo que apenas os registros pertinentes a cada visão sejam carregados e manipulados.

## Objetivo
Melhorar a usabilidade e o controle sobre os agendamentos, reduzindo risco de alterações indevidas em registros antigos.

A divisão deve permitir que o usuário trabalhe nos agendamentos do dia em diante com todas as ações disponíveis (criação, importação, alteração de status) e, ao mesmo tempo, consulte o histórico em um modo somente leitura.

## Opção Técnica Escolhida
**Opção 2 – Query Segmentada no Back-end**

- Implementar endpoints distintos ou parâmetros de filtro de data para trazer dois conjuntos de dados:
  - `current` → agendamentos >= hoje.
  - `history` → agendamentos < hoje.
- Benefícios:
  - Evita trazer todos os registros de uma vez.
  - Melhora a performance.
  - Facilita controle de regras de negócio em cada visão.
  - Permite que o front-end utilize contratos simples para alternar entre as duas visões.

## Plano de Implementação
1. **Back-end**
   - Criar/ajustar endpoints com parâmetro `scope = [current | history]`.
   - Adicionar lógica de filtro por data diretamente na query, calculando o limite do dia vigente no servidor.
   - Retornar dados já segmentados para o front-end e manter a paginação em cada escopo.
   - Propagar o escopo para as camadas de serviço e repositório, garantindo que os contadores (paginação) utilizem os mesmos filtros de data.
   - Preparar testes automatizados cobrindo os dois escopos e cenários inválidos.

2. **Front-end**
   - Criar abas/tabs para separar "Agendamentos Atuais" e "Histórico", reutilizando os componentes existentes.
   - Exibir botões de ação (adicionar, importar, alterar status) **apenas** na visão atual.
   - Desabilitar ações na visão histórica e sinalizar ao usuário que se trata de uma visualização somente leitura.
   - Integrar com o novo parâmetro `scope` da API ao trocar de aba e ajustar o estado local/global para manter as listas independentes.

3. **Validação de Importação**
   - Pré-processar planilha de importação.
   - Caso haja registros no passado → bloquear importação desses itens, exibir toast com resumo e permitir download do relatório detalhado quando necessário.
   - Garantir que o serviço de importação devolva informações estruturadas (linhas impactadas, mensagens) para que o front-end componha o feedback ao usuário.

4. **Controle de Ações**
   - Implementar toggle de permissões baseado em data:
     - Datas >= hoje → habilitar ações.
     - Datas < hoje → somente leitura.
   - Replicar as regras no back-end (validação extra em updates/importação) para evitar inconsistências em chamadas diretas à API.
   - Documentar os comportamentos esperados por visão para suporte e QA.

5. **Observabilidade e Rollout**
   - Incluir métricas/logs diferenciando acessos às visões "current" e "history" para avaliar adoção.
   - Disponibilizar feature flag para ativar gradualmente a nova navegação, caso necessário.
   - Planejar fallback simples (ex.: retorno ao endpoint único) durante o período de estabilização.

## Próximos Passos
- Implementar a segmentação por `scope` no endpoint atual de listagem de agendamentos (em andamento).
- Atualizar os testes automatizados do back-end para cobrir a nova filtragem por escopo.
- Ajustar a tela de agendamentos para consumir os dados segmentados e refletir as regras de permissão.
- Evoluir o fluxo de importação com a validação de datas passadas, conectando com a camada de UI para exibir o resumo de inconsistências.
