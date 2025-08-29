# CONTRATO DE PRESTAÇÃO DE SERVIÇOS - SISTEMA DE AGENDAMENTO DE CONSULTAS

## PARTES CONTRATANTES

**CONTRATANTE:** Fabiano Oliveira  
**CPF:** [000.000.000-00]

**CONTRATADO:** Bruno Gonzaga Santos  
**CPF:** 054.766.949-60

## OBJETO DO CONTRATO

Este contrato tem por objeto o desenvolvimento, implantação e manutenção de um **Sistema de Agendamento de Consultas** via web, dividido em fases progressivas de implementação.

## DESENVOLVIMENTO POR FASES

### FASE 1 - SISTEMA BASE (PENDENTE: DEPLOY EM SERVIDOR DEFINITIVO)

#### Funcionalidades Entregues:

**1. Painel de Controle**
- Tela inicial com resumo das operações
- Contadores de agendamentos (total, confirmados, cancelados)
- Contadores de motoristas e coletoras cadastrados
- Atalhos para principais funções do sistema

**2. Gestão de Agendamentos**
- Importação de planilhas Excel com dados dos pacientes
- Sistema detecta e corrige erros automaticamente
- Visualização em formato de lista ou calendário mensal
- Busca por unidade de saúde, data ou profissional
- Mudança de status (confirmar, cancelar, reagendar)
- Atribuição de motorista e coletora para cada coleta

**3. Cadastro de Motoristas**
- Registro completo com nome, documento, telefone
- Controle se está ativo ou inativo
- Visualização dos agendamentos de cada motorista
- Edição e exclusão de cadastros

**4. Cadastro de Coletoras**
- Registro de profissionais de coleta
- Controle de disponibilidade
- Histórico de atendimentos
- Gestão completa dos dados

**5. Sistema de Rotas**
- Criação automática de rotas para motoristas
- Integração com Google Maps e Waze
- Visualização otimizada para celular
- Lista de endereços organizados por proximidade

**6. Recursos Técnicos Incluídos**
- Sistema funcionando via navegador web
- Adaptado para computador, tablet e celular
- Banco de dados para armazenar informações
- Processamento de planilhas de até 10MB

**Etapa Final da Fase 1:**
- Deploy em servidor definitivo (prazo: até 5 dias após aprovação do cliente)
- Configuração de domínio personalizado (opcional)
- Testes finais em ambiente de produção

**Opções de Acesso:**
- **Gratuito:** Acesso via IP ou endereço genérico (ex: sistema123.servidor.com)
- **Domínio Personalizado:** Cliente fornece domínio próprio (ex: sistema.minhaempresa.com.br)
  - Configuração: R$ 29,99 no primeiro ano
  - Renovação: R$ 59,90 nos anos seguintes
  - *Custo do registro do domínio por conta do cliente*

### FASE 2 - SEGURANÇA E DOCUMENTOS (A IMPLEMENTAR)

**Prazo estimado:** 30 dias após aprovação

#### Funcionalidades Previstas:

**1. Sistema de Login**
- Acesso com usuário e senha
- Diferentes níveis de permissão (administrador, operador, visualizador)
- Recuperação de senha por e-mail
- Registro de atividades por usuário

**2. Gestão de Documentos**
- Upload de documentos dos pacientes (PDF, imagens)
- Anexar exames e laudos aos agendamentos
- Organização por paciente e data
- Visualização e download de arquivos
- Armazenamento seguro com backup

**3. Tela de Configurações**
- Painel para administradores configurarem chave OpenRouter
- Gestão de configurações avançadas do sistema
- Controle de acesso por perfil de usuário
- Interface para ajustes técnicos e integrações

**4. Melhorias de Segurança**
- Criptografia de dados sensíveis
- Backup automático diário
- Histórico de todas as alterações
- Proteção contra acessos não autorizados

**Investimento Fase 2:** R$ [valor a definir]

### FASE 3 - INTEGRAÇÃO HABLA (A IMPLEMENTAR)

**Prazo estimado:** A definir conforme complexidade

#### Funcionalidades Previstas:

**1. Integração com Sistema Habla**
- Conectar com o sistema Habla existente do cliente
- Definir quais dados serão sincronizados entre sistemas
- Estabelecer frequência de atualização (manual ou automática)

**2. Customizações Específicas**
- Ajustes conforme necessidades particulares do cliente
- Mapeamento de campos e dados específicos
- Adaptações no fluxo de trabalho atual

*Detalhamento e investimento a serem definidos após análise técnica do sistema Habla e reunião de requisitos com o cliente*

## PLANO DE MANUTENÇÃO

**Período Promocional (3 primeiros meses):** R$ 150,00/mês
**Valor regular (a partir do 4º mês):** R$ 300,00/mês

**Inclui:**
✓ Hospedagem completa do sistema
✓ Backup semanal automático  
✓ Correção de eventuais problemas
✓ Pequenos ajustes (até 2h/mês)
✓ Suporte por WhatsApp em horário comercial

*Valor promocional exclusivo para primeiro contrato*

### Serviços Não Inclusos na Manutenção:
- Desenvolvimento de novas funcionalidades grandes
- Alterações estruturais no sistema
- Integrações com novos sistemas
- Treinamento presencial
- Suporte fora do horário comercial (sob demanda)

## RESPONSABILIDADES DO CONTRATANTE

1. **Fornecer chave de API da OpenRouter** para funcionamento do sistema de correção automática de endereços
2. Disponibilizar informações necessárias para o desenvolvimento
3. Validar e aprovar as entregas de cada fase
4. Efetuar os pagamentos conforme acordado
5. Designar responsável para acompanhamento do projeto

## RESPONSABILIDADES DO CONTRATADO

1. Desenvolver o sistema conforme especificado
2. Realizar testes antes de cada entrega
3. Fornecer documentação de uso
4. Prestar suporte técnico conforme contratado
5. Manter sigilo sobre informações da empresa

## FORMA DE PAGAMENTO

### Todas as Fases:
- **Pagamento integral na entrega e aprovação** de cada fase
- Sem pagamentos antecipados ou parciais

### Manutenção:
- Pagamento mensal até dia 10 de cada mês
- **Início da cobrança:** mês seguinte ao mês da primeira entrega (Fase 1)

## PRAZO DE GARANTIA

- 90 dias de garantia para correção de problemas da Fase 1
- 60 dias de garantia para cada nova fase implementada
- Garantia não cobre alterações solicitadas ou mau uso

## PROPRIEDADE E CONFIDENCIALIDADE

1. O código-fonte será de propriedade do CONTRATANTE após pagamento integral
2. O CONTRATADO manterá sigilo sobre dados e informações do CONTRATANTE
3. O CONTRATANTE autoriza o CONTRATADO a incluir o projeto em portfólio

## RESCISÃO

- Qualquer parte pode rescindir com 30 dias de aviso prévio
- Pagamento proporcional aos serviços prestados
- Entrega de todos os códigos e documentações

## OBSERVAÇÕES IMPORTANTES

1. **Fase 1 pendente:** migração para servidor definitivo e banco de dados de produção (atualmente em ambiente provisório)
2. Todo o sistema está em **português brasileiro**
3. **Funciona em qualquer navegador** moderno
4. Cliente precisa ter **conta na OpenRouter** para usar correção de endereços
5. **Treinamento inicial** de 2 horas incluído para até 5 usuários

## ASSINATURA E APROVAÇÃO

Este contrato pode ser formalizado através de:

1. **Assinatura física** em uma via
2. **E-mail** com confirmação expressa de ambas as partes
3. **WhatsApp** com mensagem de aceite dos termos

**Data da formalização:** ___/___/2024

**CONTRATANTE:**  
Nome: _______________________________  
Documento: _________________________

**CONTRATADO:**  
Nome: _______________________________  
Documento: _________________________