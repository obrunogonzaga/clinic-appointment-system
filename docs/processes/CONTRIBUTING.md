# Guia de Contribuição

Obrigado por seu interesse em contribuir com o Sistema de Agendamento Clínico! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Sumário

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente de Desenvolvimento](#configuração-do-ambiente-de-desenvolvimento)
- [Processo de Pull Request](#processo-de-pull-request)
- [Padrões de Código](#padrões-de-código)
- [Testes](#testes)
- [Documentação](#documentação)

## Código de Conduta

Este projeto segue nosso [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, você deve seguir este código.

## Como Contribuir

### 🐛 Reportando Bugs

1. Verifique se o bug já foi reportado nas [Issues](https://github.com/bruno/clinic-appointment/issues)
2. Se não foi reportado, crie uma nova issue usando o template de bug report
3. Inclua informações detalhadas sobre como reproduzir o bug
4. Adicione logs relevantes, screenshots ou outros materiais de apoio

### ✨ Sugerindo Funcionalidades

1. Verifique se a funcionalidade já foi sugerida nas [Issues](https://github.com/bruno/clinic-appointment/issues)
2. Se não foi sugerida, crie uma nova issue usando o template de feature request
3. Descreva claramente o problema que a funcionalidade resolveria
4. Explique como você imagina que a funcionalidade funcionaria

### 🔧 Contribuindo com Código

1. Faça fork do repositório
2. Crie uma branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Implemente suas mudanças
4. Adicione testes para suas mudanças
5. Execute os testes para garantir que tudo funciona
6. Commit suas mudanças usando [Conventional Commits](#conventional-commits)
7. Push para sua branch (`git push origin feature/nova-funcionalidade`)
8. Abra um Pull Request

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Docker e Docker Compose
- Git
- Node.js 18+ (para desenvolvimento local do frontend)
- Python 3.11+ (para desenvolvimento local do backend)

### Configuração Inicial

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/bruno/clinic-appointment.git
   cd clinic-appointment
   ```

2. **Configure o ambiente:**
   ```bash
   make setup
   ```

3. **Inicie os serviços:**
   ```bash
   make up
   ```

4. **Instale pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

### Desenvolvimento Local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Processo de Pull Request

### Antes de Criar um PR

1. Certifique-se de que sua branch está atualizada com a main
2. Execute todos os testes
3. Execute linting e formatação
4. Verifique se a documentação está atualizada

### Criando um PR

1. Use o template de PR fornecido
2. Preencha todas as seções relevantes
3. Vincule issues relacionadas
4. Marque todas as caixas de verificação aplicáveis
5. Adicione reviewers se necessário

### Critérios para Aprovação

- [ ] Todos os testes passam
- [ ] Cobertura de testes mantida ou melhorada
- [ ] Código segue os padrões estabelecidos
- [ ] Documentação atualizada
- [ ] PR aprovado por pelo menos um maintainer

## Padrões de Código

### Conventional Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

**Tipos:**
- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: mudanças na documentação
- `style`: formatação, ponto e vírgula faltando, etc.
- `refactor`: refatoração de código
- `perf`: melhoria de performance
- `test`: adição ou correção de testes
- `build`: mudanças no sistema de build
- `ci`: mudanças na configuração de CI
- `chore`: outras mudanças

**Exemplos:**
```
feat(backend): adicionar endpoint de criação de pacientes
fix(frontend): corrigir bug no formulário de agendamento
docs: atualizar README com instruções de instalação
```

### Backend (Python)

- **Formatação:** Black (line-length=88)
- **Linting:** Flake8
- **Ordenação de imports:** isort
- **Type checking:** mypy
- **Arquitetura:** Clean Architecture
- **Padrões:** PEP 8, Google Style docstrings

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class PatientCreateRequest(BaseModel):
    """Request model for creating a new patient."""
    
    name: str
    email: str
    phone: str
    date_of_birth: Optional[datetime] = None


async def create_patient(
    patient_data: PatientCreateRequest,
    repository: PatientRepository
) -> Patient:
    """Create a new patient in the system.
    
    Args:
        patient_data: Patient information
        repository: Patient repository instance
        
    Returns:
        Created patient instance
        
    Raises:
        ValidationError: If patient data is invalid
    """
    # Implementation here
    pass
```

### Frontend (TypeScript/React)

- **Formatação:** Prettier
- **Linting:** ESLint
- **Estilo:** Functional components com hooks
- **State:** Zustand + React Query
- **Styling:** Tailwind CSS

```typescript
interface PatientFormProps {
  onSubmit: (data: PatientFormData) => Promise<void>
  initialData?: Partial<PatientFormData>
  isLoading?: boolean
}

export const PatientForm: React.FC<PatientFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<PatientFormData>(
    initialData || getDefaultFormData()
  )

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData)
  }, [formData, onSubmit])

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Form content */}
    </form>
  )
}
```

## Testes

### Backend

- **Framework:** pytest
- **Coverage mínima:** 80%
- **Tipos:** Unit, Integration, E2E

```python
import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_create_patient():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/patients",
            json={
                "name": "João Silva",
                "email": "joao@example.com",
                "phone": "11999999999"
            }
        )
    
    assert response.status_code == 201
    assert response.json()["name"] == "João Silva"
```

### Frontend

- **Framework:** Vitest + React Testing Library
- **Coverage mínima:** 70%

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PatientForm } from './PatientForm'

describe('PatientForm', () => {
  it('should submit form with valid data', async () => {
    const mockOnSubmit = vi.fn()
    
    render(<PatientForm onSubmit={mockOnSubmit} />)
    
    fireEvent.change(screen.getByLabelText(/nome/i), {
      target: { value: 'João Silva' }
    })
    fireEvent.click(screen.getByRole('button', { name: /salvar/i }))
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'João Silva',
        // ... outros campos
      })
    })
  })
})
```

## Documentação

### Documentação de Código

- **Backend:** Google Style docstrings
- **Frontend:** JSDoc comments
- **API:** OpenAPI/Swagger (automático)

### Documentação de Usuário

- Mantenha o README.md atualizado
- Documente mudanças breaking no CHANGELOG.md
- Adicione exemplos de uso quando relevante

## Comandos Úteis

```bash
# Desenvolvimento
make up                 # Iniciar todos os serviços
make down              # Parar todos os serviços
make logs              # Ver logs de todos os serviços
make shell-backend     # Abrir shell no container do backend
make shell-frontend    # Abrir shell no container do frontend

# Testes
make test              # Executar todos os testes
make test-backend      # Executar testes do backend
make test-frontend     # Executar testes do frontend

# Qualidade de código
make lint              # Executar linting em todo o código
make format            # Formatar todo o código
make type-check        # Verificar tipos (TypeScript + mypy)

# Limpeza
make clean             # Limpar arquivos gerados
```

## Suporte

Se você precisar de ajuda:

1. Consulte a [documentação](../README.md)
2. Procure nas [Issues existentes](https://github.com/bruno/clinic-appointment/issues)
3. Crie uma nova issue com a tag `question`
4. Entre em contato com os maintainers

## Reconhecimentos

Obrigado por contribuir para tornar o Sistema de Agendamento Clínico melhor! 🎉