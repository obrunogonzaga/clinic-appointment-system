# Documentação do Projeto - Clinic Appointment

Esta pasta contém toda a documentação do sistema de agendamento de consultas clínicas.

## 📁 Estrutura Organizacional

```
docs/
├── README.md                    # Este arquivo
├── PROJECT_OVERVIEW.md          # Visão geral do projeto
│
├── deployment/                  # Documentação de deploy e infraestrutura
│   ├── BACKGROUND_JOBS.md      # Configuração de jobs em background
│   ├── COOLIFY_REDIS.md        # Setup do Redis no Coolify
│   └── COOLIFY_WORKER.md       # Configuração de workers no Coolify
│
├── feature/                     # Documentação de features
│   ├── active/                 # Features em desenvolvimento
│   │   ├── rbac-navigation-and-dashboards.md
│   │   └── split-schedule-views.md
│   ├── completed/              # Features completadas
│   │   ├── APPOINTMENT_IMPLEMENTATION_GUIDE.md
│   │   ├── APPOINTMENT_MANUAL_CREATION_PLAN.md
│   │   └── APPOINTMENT_SCREEN_IMPROVEMENT_PLAN.md
│   └── planned/                # Features planejadas
│       └── calcom-integration-plan.md
│
├── guides/                      # Guias e tutoriais
│   ├── deployment-environment-config.md  # Configuração de ambientes
│   ├── DEVELOPMENT.md          # Guia de desenvolvimento
│   ├── rbac-implementation-guide.md  # Guia de implementação RBAC
│   ├── RENDER_DEPLOYMENT_GUIDE.md    # Guia de deploy no Render
│   └── RENDER_ENV_VARS_GUIDE.md      # Guia de variáveis de ambiente
│
├── plans/                       # Planos e estratégias
│   ├── branch-protection-rules.md    # Regras de proteção de branches
│   ├── logistics_packages_plan.md    # Plano de pacotes e logística
│   └── tag-management-plan.md        # Plano de gerenciamento de tags
│
├── processes/                   # Processos e políticas
│   ├── CODE_OF_CONDUCT.md      # Código de conduta
│   └── CONTRIBUTING.md         # Guia de contribuição
│
├── resources/                   # Recursos e arquivos auxiliares
│   └── sample-sheets/          # Planilhas de exemplo para importação
│       ├── Relatório de agendamento (80).xls
│       ├── Relatorio de agendamento - 2025-09-26.xlsx
│       └── Relatório de agendamento.xlsx
│
└── templates/                   # Templates e modelos
    └── pdf/                    # Templates de PDF
        └── Template Rota Domiciliar.pdf
```

## 📖 Guia Rápido

### Para Desenvolvedores
- **Começando**: Leia `PROJECT_OVERVIEW.md` e `guides/DEVELOPMENT.md`
- **Contribuindo**: Consulte `processes/CONTRIBUTING.md`
- **RBAC**: Veja `guides/rbac-implementation-guide.md`

### Para DevOps
- **Deploy Render**: `guides/RENDER_DEPLOYMENT_GUIDE.md`
- **Variáveis de Ambiente**: `guides/RENDER_ENV_VARS_GUIDE.md` e `guides/deployment-environment-config.md`
- **Background Jobs**: `deployment/BACKGROUND_JOBS.md`
- **Coolify Setup**: Arquivos em `deployment/`

### Para Product Owners
- **Visão Geral**: `PROJECT_OVERVIEW.md`
- **Features Ativas**: Documentos em `feature/active/`
- **Features Completadas**: Documentos em `feature/completed/`
- **Roadmap**: Documentos em `feature/planned/`

### Para Gestão de Projeto
- **Proteção de Branches**: `plans/branch-protection-rules.md`
- **Gerenciamento de Tags**: `plans/tag-management-plan.md`
- **Pacotes e Logística**: `plans/logistics_packages_plan.md`

## 🔍 Documentos Principais

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| Visão Geral do Projeto | Arquitetura e objetivos | `PROJECT_OVERVIEW.md` |
| Guia de Desenvolvimento | Setup e comandos | `guides/DEVELOPMENT.md` |
| Guia de Deploy (Render) | Deploy em produção | `guides/RENDER_DEPLOYMENT_GUIDE.md` |
| Guia de Contribuição | Como contribuir | `processes/CONTRIBUTING.md` |
| Features Ativas | Desenvolvimento atual | `feature/active/` |
| Implementação RBAC | Controle de acesso | `guides/rbac-implementation-guide.md` |

## 📝 Convenções

- **Nomes de Arquivos**: Use snake_case ou kebab-case, sempre em maiúsculas para documentos principais (README.md, CONTRIBUTING.md)
- **Idioma**: Toda documentação em Português (PT-BR)
- **Formatação**: Markdown com formatação GitHub Flavored
- **Versionamento**: Documente mudanças significativas com data

## 🔄 Atualizações

Esta estrutura foi reorganizada em 02/10/2025 para melhorar a navegabilidade e manutenção da documentação.

Para sugestões de melhoria na estrutura da documentação, abra uma issue ou consulte `processes/CONTRIBUTING.md`.
