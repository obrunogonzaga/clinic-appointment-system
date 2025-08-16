# Implementation Plan - MVP Clinic Appointment System

**Projeto**: Sistema de Agendamento de Consultas - MVP  
**Versão**: 2.0 (Simplificado)  
**Última Atualização**: 2025-01-14  
**Status**: Em Implementação

## 🎯 Objetivo do MVP

Criar um sistema funcional mínimo que permita:
1. **Upload de arquivo Excel** com dados de agendamentos
2. **Visualização dos dados** em tabela interativa
3. **Persistência** no banco de dados MongoDB
4. **Filtros básicos** por unidade e marca

## 📋 Plano de Implementação Simplificado

### Fase 1: Backend Essencial (2-3 dias)

| ID | Tarefa | Prioridade | Status | Notas |
|----|--------|------------|--------|-------|
| **MVP-BE-01** | Criar entidades básicas (Appointment) | 🔴 Alta | ✅ Concluído | Apenas campos essenciais do Excel |
| **MVP-BE-02** | Criar repositório MongoDB para Appointment | 🔴 Alta | ✅ Concluído | CRUD básico |
| **MVP-BE-03** | Endpoint de upload de Excel | 🔴 Alta | ✅ Concluído | POST /api/v1/appointments/upload |
| **MVP-BE-04** | Parser do Excel com pandas | 🔴 Alta | ✅ Concluído | Validação básica dos dados |
| **MVP-BE-05** | Endpoint de listagem com filtros | 🔴 Alta | ✅ Concluído | GET /api/v1/appointments |
| **MVP-BE-06** | Testes básicos dos endpoints | 🟡 Média | ❌ Pendente | Coverage mínimo 70% |

### Fase 2: Frontend Essencial (2-3 dias)

| ID | Tarefa | Prioridade | Status | Notas |
|----|--------|------------|--------|-------|
| **MVP-FE-01** | Setup React + TypeScript + Vite | 🔴 Alta | ✅ Concluído | Estrutura básica |
| **MVP-FE-02** | Página de upload de arquivo | 🔴 Alta | ✅ Concluído | Drag & drop ou botão |
| **MVP-FE-03** | Componente de tabela de dados | 🔴 Alta | ✅ Concluído | TanStack Table |
| **MVP-FE-04** | Filtros por unidade e marca | 🔴 Alta | ✅ Concluído | Dropdowns simples |
| **MVP-FE-05** | Integração com API backend | 🔴 Alta | ✅ Concluído | Axios ou Fetch |
| **MVP-FE-06** | Loading states e mensagens | 🟡 Média | ✅ Concluído | UX básica |

### Fase 3: Integração e Deploy (1-2 dias)

| ID | Tarefa | Prioridade | Status | Notas |
|----|--------|------------|--------|-------|
| **MVP-INT-01** | Testar fluxo completo E2E | 🔴 Alta | ❌ Pendente | Upload → Visualização |
| **MVP-INT-02** | Docker compose atualizado | 🟡 Média | ❌ Pendente | Frontend + Backend + MongoDB |
| **MVP-INT-03** | README com instruções | 🟡 Média | ❌ Pendente | Como rodar o projeto |

## 🗂️ Estrutura de Dados Simplificada

### Entidade Appointment (MVP)
```typescript
interface Appointment {
  id: string;
  nomeUnidade: string;        // Nome da Unidade
  nomeMarca: string;          // Nome da Marca
  nomePaciente: string;       // Nome do Paciente
  dataAgendamento: Date;      // Data do Agendamento
  horaAgendamento: string;    // Hora do Agendamento
  tipoConsulta?: string;      // Tipo de Consulta
  status?: string;            // Status (Confirmado, Cancelado, etc)
  telefone?: string;          // Telefone de Contato
  carro?: string;             // Informações do carro utilizado
  createdAt: Date;
  updatedAt: Date;
}
```

## 🛠️ Stack Técnica Simplificada

### Backend
- **FastAPI** - Framework web
- **MongoDB** - Banco de dados
- **Pandas** - Processamento de Excel
- **Pydantic** - Validação de dados

### Frontend
- **React 18** - UI Library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TanStack Table** - Tabela de dados
- **Tailwind CSS** - Estilização

## 📁 Estrutura de Pastas MVP

```
clinic-appointment/
├── backend/
│   ├── src/
│   │   ├── domain/
│   │   │   └── appointment.py       # Entidade
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   │       └── appointment_repository.py
│   │   ├── application/
│   │   │   └── services/
│   │   │       └── excel_service.py # Parser Excel
│   │   └── presentation/
│   │       └── api/
│   │           └── v1/
│   │               └── appointments.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   └── AppointmentTable.tsx
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   └── services/
│   │       └── api.ts
│   └── tests/
└── docker-compose.yml
```

## ✅ Critérios de Sucesso do MVP

1. ✅ Upload de arquivo Excel funciona sem erros
2. ✅ Dados são salvos corretamente no MongoDB
3. ✅ Tabela exibe todos os registros importados
4. ✅ Filtros por unidade e marca funcionam
5. ✅ Interface responsiva e intuitiva
6. ✅ Testes básicos passando (>70% coverage)

## 🚀 Próximos Passos (Pós-MVP)

Após o MVP estar funcional, adicionar:
- Autenticação de usuários
- Edição/exclusão de agendamentos
- Geração de relatórios PDF
- Dashboard com métricas
- Notificações
- API completa RESTful

## 📊 Progresso Atual

### Status Geral
- **Total de Tarefas**: 15
- **Concluídas**: 0 (0%)
- **Em Progresso**: 0 (0%)
- **Pendentes**: 15 (100%)

### Tempo Estimado
- **Backend**: 2-3 dias
- **Frontend**: 2-3 dias
- **Integração**: 1-2 dias
- **Total**: ~1 semana com 1 desenvolvedor

---

## 📝 Changelog

### 2025-01-14
- **Criado**: Novo plano simplificado focado em MVP
- **Removido**: 70% das tarefas não essenciais do plano original
- **Foco**: Upload de Excel, visualização e persistência de dados
- **Simplificado**: Arquitetura para entrega rápida mantendo qualidade

---

## 💡 Notas Importantes

1. **Prioridade no Upload**: O core do MVP é conseguir fazer upload e visualizar dados
2. **Sem Autenticação**: MVP não terá login para simplificar
3. **UI Simples**: Foco em funcionalidade, não em beleza
4. **Testes Essenciais**: Apenas testes dos fluxos principais
5. **Deploy Local**: Docker compose para rodar localmente primeiro

Este plano visa entregar valor rapidamente com as funcionalidades mais importantes primeiro.