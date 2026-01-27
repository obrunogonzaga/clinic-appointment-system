# Clinic Appointment Scheduling System

Sistema de agendamento de consultas para clínicas médicas desenvolvido com React, FastAPI e MongoDB.

## 🏥 Sobre o Projeto

Este sistema foi desenvolvido para otimizar o processo de agendamento de consultas em clínicas médicas, oferecendo:

- 📅 Gestão completa de agendamentos
- 📊 Importação de dados via Excel
- 📄 Geração de relatórios em PDF
- 👥 Controle de acesso baseado em funções (RBAC)
- 🔍 Filtros avançados e busca inteligente

## 🚀 Tecnologias

### Backend
- **Python 3.11** com **FastAPI**
- **MongoDB 6.0** para persistência de dados
- **JWT** para autenticação
- **Clean Architecture** para organização do código

### Frontend
- **React 18** com **TypeScript**
- **Vite** para build rápido
- **Tailwind CSS** para estilização
- **TanStack Query** para gerenciamento de estado

### DevOps
- **Docker** e **Docker Compose**
- **GitHub Actions** para CI/CD
- **Prometheus** e **Grafana** para monitoramento

## 📋 Pré-requisitos

- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento local)
- Python 3.11+ (para desenvolvimento local)
- Git

## 📈 Módulo de Extração de Investimentos

Este repositório agora inclui um MVP completo para extração de posições financeiras a partir de PDFs dos bancos Itaú, XP, Bradesco e BTG. O pacote contempla:

- Micro-serviço FastAPI (`/extractor`) com parsers específicos por banco.
- Workflow n8n (`/orchestrator/workflow-n8n.json`) para orquestrar a leitura dos PDFs, chamada ao micro-serviço e gravação dos CSV/XLSX.
- Arquivo `docker-compose.yml` pronto para subir os serviços locais (n8n, Postgres e o micro-serviço de extração).

### Como executar o MVP de extração

1. Certifique-se de possuir as pastas `./input_pdfs` e `./output` na raiz (já incluídas no repositório).
2. Suba o ambiente com:

   ```bash
   docker-compose up -d
   ```

3. Acesse `http://localhost:5678/`, importe o workflow localizado em `/orchestrator/workflow-n8n.json` e execute o nó Manual Trigger.
4. Coloque os relatórios PDF desejados em `./input_pdfs` antes de executar o workflow.
5. Os resultados serão gravados em `./output/posicoes.csv` e `./output/posicoes.xlsx`. Em caso de erros, os detalhes aparecem em `./output/errors/`.

Mais detalhes sobre o micro-serviço estão em `/extractor/README.md` e sobre o fluxo no `/orchestrator/README.md`.

## 🛠️ Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/clinic-appointment.git
cd clinic-appointment
```

### 2. Configure as variáveis de ambiente

```bash
# Copie os arquivos de exemplo
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 3. Inicie com Docker

```bash
# Construa e inicie todos os serviços
docker-compose up --build

# Ou em modo detached
docker-compose up -d
```

### 4. Acesse a aplicação

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB Express: http://localhost:8081

## 🔧 Desenvolvimento Local

### Backend

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o servidor
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Execute o servidor de desenvolvimento
npm run dev
```

## 📚 Documentação

- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [Arquitetura do Sistema](.claude/ARCHITECTURE.md)
- [Plano de Implementação](IMPLEMENTATION_PLAN.md)
- [API Documentation](http://localhost:8000/docs)

## 🧪 Testes

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

### End-to-End
```bash
cd tests
npm run e2e
```

## 📦 Build para Produção

```bash
# Build das imagens Docker
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contribuindo

Leia nosso [Guia de Contribuição](docs/CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de submissão de pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- Bruno - Desenvolvedor Principal

## 📞 Suporte

Para suporte, envie um email para suporte@clinicapp.com.br ou abra uma issue no GitHub.

---

Desenvolvido com ❤️ para melhorar o atendimento em clínicas médicas brasileiras.