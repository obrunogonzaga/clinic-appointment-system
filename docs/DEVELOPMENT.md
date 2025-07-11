# Guia de Desenvolvimento

Este documento fornece informações detalhadas para desenvolvedores que trabalham no Sistema de Agendamento Clínico.

## 📋 Sumário

- [Configuração do Ambiente](#configuração-do-ambiente)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Desenvolvimento Backend](#desenvolvimento-backend)
- [Desenvolvimento Frontend](#desenvolvimento-frontend)
- [Banco de Dados](#banco-de-dados)
- [Testes](#testes)
- [Docker](#docker)
- [Debugging](#debugging)
- [Padrões e Convenções](#padrões-e-convenções)

## Configuração do Ambiente

### Requisitos

- **Docker & Docker Compose**: Para ambiente de desenvolvimento
- **Node.js 18+**: Para desenvolvimento local do frontend
- **Python 3.11+**: Para desenvolvimento local do backend
- **Git**: Controle de versão

### Configuração Inicial

1. **Clone e configure:**
   ```bash
   git clone https://github.com/bruno/clinic-appointment.git
   cd clinic-appointment
   make setup
   ```

2. **Inicie os serviços:**
   ```bash
   make up
   ```

3. **Verifique se tudo está funcionando:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081

## Arquitetura do Sistema

### Visão Geral

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │     Backend     │    │    Database     │
│   React + TS    │◄──►│  FastAPI + Py   │◄──►│    MongoDB      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend - Clean Architecture

```
src/
├── domain/           # Entidades e regras de negócio
├── application/      # Casos de uso e DTOs
├── infrastructure/   # Banco de dados, serviços externos
└── presentation/     # Controllers FastAPI
```

### Frontend - Estrutura Modular

```
src/
├── components/       # Componentes reutilizáveis
├── pages/           # Páginas da aplicação
├── hooks/           # Custom hooks
├── services/        # Integração com API
├── types/           # Definições TypeScript
└── utils/           # Utilitários
```

## Desenvolvimento Backend

### Configuração Local

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### Executando Localmente

```bash
# Com auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando o script
python src/main.py
```

### Estrutura de Arquivos

```python
# src/domain/entities/patient.py
@dataclass(frozen=True)
class Patient:
    id: PatientId
    name: str
    email: Email
    phone: PhoneNumber
    created_at: datetime

# src/application/use_cases/create_patient.py
class CreatePatientUseCase:
    def __init__(self, repository: PatientRepository):
        self._repository = repository
    
    async def execute(self, command: CreatePatientCommand) -> PatientDto:
        # Implementação do caso de uso
        pass

# src/presentation/controllers/patient_controller.py
@router.post("/patients", response_model=PatientResponse)
async def create_patient(request: CreatePatientRequest):
    # Implementação do controller
    pass
```

### Padrões Backend

- **Repository Pattern**: Abstração do acesso a dados
- **Use Case Pattern**: Lógica de negócio isolada
- **Dependency Injection**: Inversão de dependências
- **DTOs**: Transferência de dados entre camadas
- **Validation**: Pydantic para validação de entrada

### Comandos Úteis

```bash
# Testes
pytest -v
pytest --cov=src

# Linting
flake8 .
black .
isort .
mypy .

# Migrações (quando disponível)
python scripts/migrate.py
```

## Desenvolvimento Frontend

### Configuração Local

```bash
cd frontend
npm install
npm run dev
```

### Estrutura de Componentes

```typescript
// components/common/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  onClick,
  children
}) => {
  return (
    <button
      className={getButtonClasses(variant, size)}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

### Estado Global

```typescript
// stores/useAppStore.ts
interface AppState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
}))
```

### Integração com API

```typescript
// services/patientService.ts
class PatientService {
  async getPatients(filters?: PatientFilters): Promise<Patient[]> {
    const response = await api.get('/patients', { params: filters })
    return response.data
  }

  async createPatient(data: CreatePatientData): Promise<Patient> {
    const response = await api.post('/patients', data)
    return response.data
  }
}

export const patientService = new PatientService()
```

### Comandos Úteis

```bash
# Desenvolvimento
npm run dev
npm run build
npm run preview

# Testes
npm run test
npm run test:ui
npm run test:coverage

# Qualidade de código
npm run lint
npm run lint:fix
npm run type-check
```

## Banco de Dados

### MongoDB com Docker

```bash
# Conectar ao MongoDB
make shell-db

# Ou usar MongoDB Compass
# Connection string: mongodb://admin:changeme@localhost:27017/
```

### Estrutura de Dados

```javascript
// Exemplo de documento Patient
{
  _id: ObjectId("..."),
  name: "João Silva",
  email: "joao@example.com",
  phone: "11999999999",
  date_of_birth: ISODate("1990-01-01"),
  address: {
    street: "Rua das Flores, 123",
    city: "São Paulo",
    state: "SP",
    zip_code: "01234-567"
  },
  created_at: ISODate("2025-01-11T10:00:00Z"),
  updated_at: ISODate("2025-01-11T10:00:00Z")
}
```

### Índices Importantes

```javascript
// Pacientes
db.patients.createIndex({ "email": 1 }, { unique: true })
db.patients.createIndex({ "phone": 1 })
db.patients.createIndex({ "name": "text" })

// Agendamentos
db.appointments.createIndex({ "patient_id": 1 })
db.appointments.createIndex({ "scheduled_at": 1 })
db.appointments.createIndex({ "scheduled_at": 1, "status": 1 })
```

## Testes

### Backend (pytest)

```python
# tests/test_patient_service.py
@pytest.mark.asyncio
async def test_create_patient():
    # Arrange
    repository = Mock()
    service = PatientService(repository)
    
    # Act
    result = await service.create_patient(patient_data)
    
    # Assert
    assert result.name == "João Silva"
    repository.save.assert_called_once()
```

### Frontend (Vitest + RTL)

```typescript
// components/__tests__/Button.test.tsx
describe('Button', () => {
  it('should render with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('should call onClick when clicked', () => {
    const mockClick = vi.fn()
    render(<Button onClick={mockClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(mockClick).toHaveBeenCalledOnce()
  })
})
```

### E2E (Playwright - futuro)

```typescript
// e2e/patient-management.spec.ts
test('should create a new patient', async ({ page }) => {
  await page.goto('/patients')
  await page.click('[data-testid="add-patient-button"]')
  
  await page.fill('[name="name"]', 'João Silva')
  await page.fill('[name="email"]', 'joao@example.com')
  await page.click('[type="submit"]')
  
  await expect(page.locator('text=João Silva')).toBeVisible()
})
```

## Docker

### Desenvolvimento

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Apenas serviços específicos
docker-compose up mongodb backend

# Logs de um serviço
docker-compose logs -f backend

# Shell em um container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Produção

```bash
# Build para produção
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Debugging

### VS Code

O projeto inclui configurações do VS Code para debugging:

- **Python: FastAPI** - Debug do backend
- **Python: Pytest** - Debug de testes
- **Attach to Docker Backend** - Debug via Docker

### Debugging Backend

```python
# Adicionar breakpoint
import pdb; pdb.set_trace()

# Ou usar logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Debugging Frontend

```typescript
// Console debugging
console.log('Debug:', data)

// React DevTools
// Instalar extensão do navegador
```

## Padrões e Convenções

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(backend): adicionar endpoint de criação de pacientes
fix(frontend): corrigir validação do formulário
docs: atualizar guia de desenvolvimento
```

### Branches

```
main              # Produção
develop           # Desenvolvimento
feature/xxx       # Novas funcionalidades
fix/xxx           # Correções
hotfix/xxx        # Correções urgentes
```

### Code Review

- Todo PR deve ter pelo menos 1 aprovação
- Testes devem passar
- Coverage não pode diminuir
- Linting deve passar
- Documentação deve estar atualizada

### Performance

#### Backend
- Use async/await para operações IO
- Implemente paginação para listas
- Use índices apropriados no MongoDB
- Cache resultados quando possível

#### Frontend
- Use React.memo para componentes pesados
- Implemente lazy loading para rotas
- Otimize imagens e assets
- Use React Query para cache de API

## Comandos de Desenvolvimento Rápido

```bash
# Setup completo
make setup && make up

# Desenvolvimento backend apenas
make up mongodb
cd backend && uvicorn src.main:app --reload

# Desenvolvimento frontend apenas
cd frontend && npm run dev

# Testes completos
make test

# Linting completo
make lint

# Limpeza
make clean
```

## Troubleshooting

### Problemas Comuns

1. **Porta em uso**:
   ```bash
   lsof -ti:3000 | xargs kill -9  # Mata processo na porta 3000
   ```

2. **Docker sem espaço**:
   ```bash
   docker system prune -a
   ```

3. **Dependências desatualizadas**:
   ```bash
   make clean
   make setup
   ```

4. **Banco de dados corrompido**:
   ```bash
   docker-compose down -v  # Remove volumes
   make up
   ```

Para mais informações, consulte:
- [README.md](../README.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Documentação da API](http://localhost:8000/docs)