# Guia de Implementação RBAC - Sistema de Agendamento de Clínica

## Visão Geral

Implementação progressiva de controle de acesso (RBAC) com autenticação JWT, onde cada fase entrega um MVP funcional com interface utilizável.

### Stack Tecnológico
- **Backend**: FastAPI (Python 3.11), MongoDB, Docker
- **Frontend**: React 18 + TypeScript + Vite, Tailwind CSS, TanStack Query
- **Infraestrutura**: Docker Compose, variáveis de ambiente

---

## 🚀 Fase 1: MVP de Autenticação Básica

> **Valor entregue**: Sistema com login/logout funcional e proteção de rotas

### Backend
```python
# Modelo User simplificado
{
  "_id": ObjectId,
  "email": str (único, lowercase),
  "name": str,
  "password_hash": str (bcrypt),
  "is_admin": bool (default: false),  # Simplificado para MVP
  "is_active": bool (default: true),
  "created_at": datetime
}
```

**Endpoints**:
- `POST /auth/register` - Criar primeiro admin
- `POST /auth/login` - Login com email/senha
- `POST /auth/logout` - Logout
- `GET /auth/me` - Dados do usuário logado

### Frontend
**Páginas funcionais**:
1. **Login** (`/login`)
   - Formulário de email/senha
   - Redirect após sucesso
   
2. **Home protegida** (`/`)
   - Mostra nome do usuário
   - Botão de logout
   
3. **Registro inicial** (`/setup`)
   - Apenas se não houver admin
   - Cria primeiro administrador

### Resultado do MVP 1
- ✅ Usuários podem fazer login
- ✅ Rotas protegidas funcionando
- ✅ Interface básica mas funcional
- ✅ Sistema utilizável

---

## 🎯 Fase 2: MVP de Gerenciamento de Usuários

> **Valor entregue**: Administradores podem criar e gerenciar outros usuários

### Backend
**Novos endpoints**:
- `GET /users` - Listar usuários (admin only)
- `POST /users` - Criar usuário (admin only)
- `PATCH /users/{id}` - Ativar/desativar usuário
- `DELETE /users/{id}` - Remover usuário

### Frontend
**Nova página**:
1. **Gerenciar Usuários** (`/admin/users`)
   - Tabela com lista de usuários
   - Botão "Novo Usuário"
   - Modal de criação (email, nome, senha)
   - Ações: ativar/desativar, excluir
   - Badge mostrando se é admin

2. **Menu de navegação**
   - Link para gerenciar usuários (só aparece para admin)
   - Indicador visual de admin

### Resultado do MVP 2
- ✅ Admins criam novos usuários
- ✅ Gestão básica de acesso
- ✅ Interface administrativa funcional
- ✅ Valor imediato para clínica

---

## 🔐 Fase 3: MVP de Roles e Permissões

> **Valor entregue**: Diferentes níveis de acesso para diferentes funcionários

### Backend
**Evolução do modelo**:
```python
# Substituir is_admin por:
"roles": List[str] = []  # ["ADMIN", "MANAGER", "STAFF", "READONLY"]
```

**Proteção granular**:
- Appointments: STAFF+ pode criar/editar
- Reports: MANAGER+ pode visualizar
- Users: Apenas ADMIN

### Frontend
**Melhorias na UI**:
1. **Seletor de roles** no formulário de usuário
   - Checkboxes ou select múltiplo
   - Descrição de cada role

2. **Dashboard diferenciado** por role
   - ADMIN: vê tudo
   - MANAGER: vê agenda + relatórios
   - STAFF: vê apenas agenda
   - READONLY: apenas visualiza

3. **Indicadores visuais**
   - Badges coloridos por role
   - Menu adaptativo por permissão

### Resultado do MVP 3
- ✅ Controle fino de acesso
- ✅ Cada funcionário vê só o necessário
- ✅ Segurança melhorada
- ✅ Interface adaptativa por role

---

## 🔄 Fase 4: MVP de Tokens Seguros

> **Valor entregue**: Sessões mais seguras com refresh automático

### Backend
**Melhorias de segurança**:
- Access token: 15 minutos
- Refresh token: 7 dias
- Cookies HttpOnly, Secure, SameSite
- Endpoint `/auth/refresh`

### Frontend
**UX transparente**:
1. **Interceptor automático**
   - Refresh silencioso quando token expira
   - Usuário não precisa relogar frequentemente

2. **Indicador de sessão**
   - "Sessão expira em X minutos"
   - Auto-logout após inatividade

### Resultado do MVP 4
- ✅ Maior segurança sem impactar UX
- ✅ Sessões persistentes mas seguras
- ✅ Proteção contra XSS/CSRF

---

## 👤 Fase 5: MVP de Perfil de Usuário

> **Valor entregue**: Usuários gerenciam próprias informações

### Frontend
**Novas páginas**:
1. **Meu Perfil** (`/profile`)
   - Editar nome
   - Trocar senha
   - Ver suas permissões
   - Histórico de acesso

2. **Recuperar Senha** (`/forgot-password`)
   - Solicitar reset por email
   - Token temporário

### Backend
**Novos endpoints**:
- `PATCH /auth/me` - Atualizar próprio perfil
- `POST /auth/change-password` - Trocar própria senha
- `POST /auth/forgot-password` - Solicitar reset
- `POST /auth/reset-password` - Resetar com token

### Resultado do MVP 5
- ✅ Autonomia para usuários
- ✅ Menos suporte para TI
- ✅ Melhor experiência

---

## 📊 Fase 6: MVP de Auditoria e Logs

> **Valor entregue**: Rastreabilidade e compliance

### Backend
**Log de ações**:
```python
# Coleção: audit_logs
{
  "user_id": ObjectId,
  "action": str,  # "LOGIN", "CREATE_USER", etc
  "resource": str,
  "timestamp": datetime,
  "ip_address": str,
  "user_agent": str
}
```

### Frontend
**Página de Auditoria** (`/admin/audit`)
- Filtros por usuário, ação, data
- Exportar relatório
- Alertas de ações suspeitas

### Resultado do MVP 6
- ✅ Compliance com regulamentações
- ✅ Detectar uso indevido
- ✅ Histórico completo

---

## 📋 Checklist por Fase

### Para cada MVP verificar:
- [ ] Feature funciona end-to-end
- [ ] UI é intuitiva e responsiva
- [ ] Testes básicos passando
- [ ] Documentação atualizada
- [ ] Deploy funcionando
- [ ] Usuário final consegue usar

---

## 🎨 Componentes de UI Reutilizáveis

### Criar desde a Fase 1:
```typescript
// components/ui/
- Button.tsx
- Input.tsx
- Card.tsx
- Modal.tsx
- Table.tsx
- Badge.tsx
- Alert.tsx
- LoadingSpinner.tsx
```

### Layout padrão:
```typescript
// layouts/AuthLayout.tsx
- Header com user menu
- Sidebar com navegação
- Container principal
- Footer
```

---

## 🚦 Fluxo de Implementação

### Dia 1-2: Fase 1
- Backend de auth básico
- Tela de login
- Proteção de rotas
- **Resultado**: Sistema com login funcionando

### Dia 3-4: Fase 2
- CRUD de usuários
- Interface admin
- **Resultado**: Admins gerenciando usuários

### Dia 5-6: Fase 3
- Sistema de roles
- Menus adaptativos
- **Resultado**: Permissões granulares

### Semana 2: Fases 4-6
- Melhorias incrementais
- Cada fase adiciona valor
- Sistema evoluindo com uso

---

## 📝 Prompts para Claude Code por Fase

### 🚀 Prompt Fase 1: MVP de Autenticação Básica

```markdown
Implemente um sistema de autenticação básico para o repositório clinic-appointment-system com as seguintes especificações:

**Backend (FastAPI + MongoDB):**

1. Modelo User em MongoDB:
   - _id, email (único, lowercase), name, password_hash (bcrypt)
   - is_admin (boolean, default false), is_active (boolean, default true)
   - created_at (datetime)
   - Criar índice único em email

2. Endpoints de autenticação:
   - POST /auth/register - Criar primeiro admin (só funciona se não houver nenhum admin)
   - POST /auth/login - Recebe email/senha, retorna JWT em cookie HttpOnly
   - POST /auth/logout - Limpa cookie de autenticação
   - GET /auth/me - Retorna dados do usuário autenticado

3. Configuração:
   - JWT com python-jose, secret em .env (JWT_SECRET_KEY)
   - Token expira em 24h (por enquanto)
   - Cookie com httponly=True, samesite="lax"
   - Dependency get_current_user() para proteger rotas
   - Hash de senha com passlib[bcrypt]

**Frontend (React + TypeScript + Tailwind):**

1. Páginas:
   - /login - Formulário de email/senha, redirect para / após sucesso
   - /setup - Criar primeiro admin (só aparece se não houver admin)
   - / (home) - Mostra "Olá, {nome}!" e botão de logout

2. Componentes:
   - AuthProvider com Context API
   - PrivateRoute que redireciona para /login
   - useAuth() hook para acessar user/login/logout
   - Formulários com estados de loading e erros

3. Configuração:
   - Axios com baseURL e credentials: 'include'
   - Interceptor para tratar 401
   - Tipos TypeScript para User e AuthContext

**Extras:**
- Docker-compose com as novas variáveis
- .env.example atualizado
- Testes básicos com pytest
- README com instruções de setup

Mantenha o código simples e focado nesta fase. Use as bibliotecas já existentes no projeto quando possível.
```

### 🎯 Prompt Fase 2: MVP de Gerenciamento de Usuários

```markdown
Expanda o sistema de autenticação existente para incluir gerenciamento completo de usuários:

**Backend - Novos Endpoints (apenas admin):**

1. GET /users
   - Listar todos usuários com paginação (limit/offset)
   - Retornar: id, email, name, is_admin, is_active, created_at
   - Ordenar por created_at desc

2. POST /users
   - Criar novo usuário (admin define senha inicial)
   - Campos: email, name, password, is_admin
   - Validar email único

3. PATCH /users/{user_id}
   - Atualizar: name, is_admin, is_active
   - Não permitir usuário desativar a si mesmo
   - Não permitir remover último admin

4. DELETE /users/{user_id}
   - Soft delete (is_active = false)
   - Mesmas restrições do PATCH

**Frontend - Página de Administração:**

1. Rota /admin/users (apenas para admin):
   - Tabela responsiva com usuários
   - Colunas: Email, Nome, Admin (badge), Status, Criado em, Ações
   - Botão "Novo Usuário" abre modal

2. Modal de Criar/Editar:
   - Campos: email, nome, senha (só na criação), checkbox admin
   - Validação em tempo real
   - Loading state durante submit

3. Recursos da tabela:
   - Busca por email/nome
   - Paginação
   - Ações: Editar, Ativar/Desativar, Excluir (com confirmação)
   - Toast de sucesso/erro

4. Menu de navegação:
   - Adicionar link "Usuários" (só aparece para admin)
   - Indicador visual se é admin (badge ou ícone)

**Componentes UI reutilizáveis:**
- Table com sort e pagination
- Modal genérico
- ConfirmDialog
- Badge para status
- SearchInput com debounce

Use TanStack Query para cache e mutations. Mantenha consistência visual com Tailwind.
```

### 🔐 Prompt Fase 3: MVP de Roles e Permissões

```markdown
Evolua o sistema de is_admin para roles granulares:

**Backend - Sistema de Roles:**

1. Atualizar modelo User:
   - Remover is_admin
   - Adicionar roles: List[str] = []
   - Roles disponíveis: ADMIN, MANAGER, STAFF, READONLY

2. Criar dependency require_roles:
   ```python
   def require_roles(*allowed_roles):
       def verify(user = Depends(get_current_user)):
           if not any(role in user.roles for role in allowed_roles):
               raise HTTPException(403, "Insufficient permissions")
       return verify
   ```

3. Proteger endpoints existentes:
   - /users/* - require_roles("ADMIN")
   - /appointments/create - require_roles("ADMIN", "MANAGER", "STAFF")
   - /appointments/view - require_roles("ADMIN", "MANAGER", "STAFF", "READONLY")
   - /reports - require_roles("ADMIN", "MANAGER")

4. Migration script:
   - Converter is_admin=true para roles=["ADMIN"]
   - Outros usuários recebem roles=["STAFF"]

**Frontend - Interface Adaptativa:**

1. Atualizar formulário de usuário:
   - Substituir checkbox admin por seletor múltiplo de roles
   - Mostrar descrição de cada role em tooltip
   - Ícones diferentes por role

2. Dashboard adaptativo por role:
   - ADMIN: Cards com total usuários, appointments, relatórios
   - MANAGER: Cards de appointments, relatórios, sem usuários  
   - STAFF: Apenas appointments do dia
   - READONLY: Visualização sem ações

3. Menu dinâmico:
   ```typescript
   const menuItems = [
     { label: 'Dashboard', path: '/', roles: ['*'] },
     { label: 'Appointments', path: '/appointments', roles: ['ADMIN', 'MANAGER', 'STAFF'] },
     { label: 'Reports', path: '/reports', roles: ['ADMIN', 'MANAGER'] },
     { label: 'Users', path: '/admin/users', roles: ['ADMIN'] }
   ]
   ```

4. Componente RoleGuard:
   - Oculta elementos baseado em roles
   - Mostra mensagem de permissão negada
   - Redireciona se necessário

**Visual:**
- Badges coloridos por role (Admin=vermelho, Manager=azul, Staff=verde, Readonly=cinza)
- Ícones: Admin=Shield, Manager=Briefcase, Staff=Users, Readonly=Eye

Mantenha compatibilidade com dados existentes durante migração.
```

### 🔄 Prompt Fase 4: MVP de Tokens Seguros

```markdown
Implemente refresh tokens para maior segurança mantendo boa UX:

**Backend - Dual Token System:**

1. Configuração de tokens:
   - Access token: 15 minutos (no cookie httponly "access_token")
   - Refresh token: 7 dias (no cookie httponly "refresh_token")
   - Ambos com Secure=true (em produção), SameSite=lax

2. Atualizar endpoints:
   - POST /auth/login - Retorna ambos tokens
   - POST /auth/refresh - Usa refresh para gerar novo access
   - POST /auth/logout - Limpa ambos cookies
   - GET /auth/me - Continua usando access token

3. Estrutura dos tokens:
   ```python
   # Access token payload
   {"sub": user_id, "email": email, "roles": roles, "type": "access"}
   
   # Refresh token payload  
   {"sub": user_id, "type": "refresh"}
   ```

4. Validação:
   - Refresh token só funciona em /auth/refresh
   - Access token em todas outras rotas
   - Verificar tipo do token

**Frontend - Refresh Automático:**

1. Interceptor Axios:
   ```typescript
   // Response interceptor
   axios.interceptors.response.use(
     response => response,
     async error => {
       if (error.response?.status === 401 && !error.config._retry) {
         error.config._retry = true
         await axios.post('/auth/refresh')
         return axios(error.config)
       }
       return Promise.reject(error)
     }
   )
   ```

2. Hook useTokenRefresh:
   - Refresh proativo 1 minuto antes de expirar
   - Usa setTimeout baseado no exp do token
   - Cancela ao fazer logout

3. Indicador de sessão (opcional):
   - Componente SessionIndicator no header
   - Mostra "Sessão expira em X minutos"
   - Atualiza a cada minuto

4. Auto-logout:
   - Após 30 minutos de inatividade
   - Mostrar modal de aviso antes
   - Resetar timer em qualquer interação

**Variáveis .env:**
```
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=10080
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=different-secret-key
```

Garanta que o fluxo seja transparente - usuário não deve precisar relogar frequentemente.
```

### 👤 Prompt Fase 5: MVP de Perfil de Usuário

```markdown
Adicione funcionalidades de auto-gestão para usuários:

**Backend - Endpoints de Perfil:**

1. PATCH /auth/me
   - Usuário atualiza próprio nome
   - Validar e sanitizar input

2. POST /auth/change-password
   - Recebe senha atual e nova
   - Validar senha atual antes de trocar
   - Requisitos: min 8 chars, 1 maiúscula, 1 número

3. POST /auth/forgot-password
   - Recebe email, gera token de 6 dígitos
   - Salva token com expiração (1 hora)
   - Por ora, apenas loga o token (email virá depois)

4. POST /auth/reset-password
   - Recebe email, token e nova senha
   - Valida token e expiração
   - Reseta senha e invalida token

**Frontend - Páginas de Perfil:**

1. /profile - Meu Perfil:
   - Seções: Informações Pessoais, Segurança, Permissões
   - Editar nome inline com ícone de lápis
   - Botão "Alterar Senha" abre modal
   - Lista roles do usuário com descrições
   - Mostrar "Membro desde" e "Último acesso"

2. Modal Alterar Senha:
   - Campo senha atual (com toggle show/hide)
   - Nova senha e confirmação
   - Indicador de força da senha
   - Requisitos em checklist

3. /forgot-password - Recuperar Senha:
   - Input de email
   - Mensagem de sucesso genérica
   - Link para voltar ao login

4. /reset-password - Resetar Senha:
   - Inputs: email, código de 6 dígitos, nova senha
   - Validação em tempo real
   - Redirect para login após sucesso

**Componentes:**
- PasswordStrengthMeter
- PasswordRequirements 
- EditableField
- ProfileSection

**UX Details:**
- Toast de sucesso ao salvar
- Confirmação antes de trocar senha
- Copiar código de reset facilmente
- Máscara no input de código (XXX-XXX)

Foque na experiência do usuário - deve ser intuitivo e seguro.
```

### 📊 Prompt Fase 6: MVP de Auditoria e Logs

```markdown
Implemente sistema de auditoria para compliance e segurança:

**Backend - Sistema de Logs:**

1. Modelo AuditLog:
   ```python
   {
     "_id": ObjectId,
     "user_id": ObjectId,
     "user_email": str,  # Desnormalizado para performance
     "action": str,      # LOGIN, LOGOUT, CREATE_USER, etc
     "resource": str,    # users, appointments, auth
     "resource_id": Optional[str],
     "changes": Optional[dict],  # Para updates
     "ip_address": str,
     "user_agent": str,
     "timestamp": datetime,
     "success": bool
   }
   ```

2. Middleware de Auditoria:
   - Decorator @audit_log para endpoints
   - Captura automaticamente user, IP, user-agent
   - Registra sucessos e falhas

3. Eventos para auditar:
   - AUTH: login, logout, failed_login, password_change
   - USERS: create, update, delete, activate, deactivate
   - ACCESS: permission_denied, invalid_token

4. GET /admin/audit-logs:
   - Filtros: user_id, action, resource, date_range
   - Paginação e ordenação
   - Agregações: logins por dia, ações por usuário

**Frontend - Dashboard de Auditoria:**

1. /admin/audit - Página principal:
   - Filtros no topo: usuário, ação, período
   - Tabela com: Quando, Quem, O quê, Recurso, IP, Status
   - Cores por tipo: AUTH=azul, USERS=verde, ACCESS=vermelho

2. Recursos da tabela:
   - Expandir linha para ver detalhes
   - Export CSV dos resultados
   - Atualização em tempo real (polling 30s)

3. Cards de resumo:
   - Total de logins hoje
   - Tentativas falhas (últimas 24h)
   - Usuários ativos (últimos 7 dias)
   - Ações suspeitas (múltiplas falhas)

4. Alertas automáticos:
   - Badge no menu se houver ações suspeitas
   - Destaque em vermelho para falhas consecutivas
   - Tooltip com detalhes ao passar mouse

**Visualizações:**
- Gráfico de linha: Logins por dia (últimos 30 dias)
- Gráfico de pizza: Ações por tipo
- Heatmap: Atividade por hora do dia

**Performance:**
- Índices em user_id, action, timestamp
- Reter logs por 90 dias (configurável)
- Agregações cacheadas para dashboard

Use Recharts para gráficos. Mantenha a consulta rápida mesmo com muitos logs.
```

---

## 🎯 Métricas de Sucesso por Fase

### Fase 1
- Usuários conseguem logar? ✓
- Sessão persiste? ✓
- Logout funciona? ✓

### Fase 2
- Admin cria usuários? ✓
- Lista aparece correta? ✓
- Ações funcionam? ✓

### Fase 3
- Roles restringem acesso? ✓
- UI adapta por role? ✓
- Sem bugs de permissão? ✓

E assim por diante...

---

## 🛠️ Stack de Implementação

### Dependências Backend
```bash
# Fase 1
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Fase 3+
pip install emails  # Para envio futuro
```

### Dependências Frontend  
```bash
# Fase 1
npm install axios js-cookie @types/js-cookie

# Fase 2
npm install @tanstack/react-query @tanstack/react-table

# Fase 6
npm install recharts date-fns
```