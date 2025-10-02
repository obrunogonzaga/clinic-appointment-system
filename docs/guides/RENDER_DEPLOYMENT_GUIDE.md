# 🚀 Guia de Deploy no Render

**Guia completo para fazer deploy da aplicação Clinic Appointment no Render**

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Configuração do Backend](#configuração-do-backend)
- [Configuração do Frontend](#configuração-do-frontend)
- [Configuração do MongoDB](#configuração-do-mongodb)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy Automático](#deploy-automático)
- [Monitoramento](#monitoramento)

---

## 🔧 Pré-requisitos

### 1. **Conta no Render**
- Criar conta em [render.com](https://render.com)
- Conectar com repositório GitHub

### 2. **MongoDB Atlas** (Recomendado)
- Criar conta em [MongoDB Atlas](https://cloud.mongodb.com)
- Criar cluster gratuito
- Configurar IP whitelist (0.0.0.0/0 para desenvolvimento)

### 3. **Repositório GitHub**
- Código no GitHub público ou privado
- Branch principal com código atualizado

---

## 🐍 Configuração do Backend

### 1. **Criar Web Service no Render**

#### **Configurações Básicas:**
```yaml
Service Type: Web Service
Repository: seu-username/clinic-appointment
Branch: main (ou sua branch principal)
Root Directory: backend
```

#### **Build & Deploy:**
```bash
# Build Command:
pip install -r requirements.txt

# Start Command:
uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2
```

### 2. **Configurações de Runtime**
```yaml
Runtime: Python 3.11
Instance Type: Free (para desenvolvimento)
Auto-Deploy: Yes
```

---

## 🌐 Configuração do Frontend

### 1. **Criar Static Site no Render**

#### **Configurações Básicas:**
```yaml
Service Type: Static Site
Repository: seu-username/clinic-appointment
Branch: main
Root Directory: frontend
```

#### **Build & Deploy:**
```bash
# Build Command:
npm install && npm run build

# Publish Directory:
dist
```

### 2. **Arquivo de Redirecionamento**
Criar arquivo `frontend/public/_redirects`:
```
/*    /index.html   200
```

---

## 🗄️ Configuração do MongoDB

### 1. **MongoDB Atlas Setup**

#### **Criar Cluster:**
1. Login no MongoDB Atlas
2. Create Project → "clinic-appointment-prod"
3. Build Database → Free Shared Cluster
4. Escolher região mais próxima
5. Create User → Salvar username/password
6. Network Access → Add IP (0.0.0.0/0)

#### **Connection String:**
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/clinic_db?retryWrites=true&w=majority
```

### 2. **Configuração de Segurança**
```yaml
Database Access:
  - Username: clinic_admin
  - Password: [gerar senha forte]
  - Role: Atlas admin

Network Access:
  - IP: 0.0.0.0/0 (Allow access from anywhere)
  - Comment: "Render deployment"
```

---

## 🔐 Variáveis de Ambiente

### **Backend Environment Variables:**

#### **Configuração no Render Dashboard:**

**Aplicação:**
```bash
APP_NAME=Clinic Appointment System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production
```

**Servidor:**
```bash
HOST=0.0.0.0
PORT=8000
RELOAD=False
```

**Database:**
```bash
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net
DATABASE_NAME=clinic_db
```

**Segurança:**
```bash
SECRET_KEY=[gerar chave aleatória de 64 caracteres]
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
```

**CORS:**
```bash
CORS_ORIGINS=["https://seu-frontend.onrender.com","http://localhost:3000"]
```

**Upload:**
```bash
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=["xlsx","xls","csv"]
```

**Logs:**
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### **Como adicionar no Render:**
1. Dashboard → Seu Backend Service
2. Environment → Add Environment Variable
3. Adicionar cada variável individualmente

### **Frontend Environment Variables:**

```bash
# No Render, Static Sites
VITE_API_URL=https://seu-backend.onrender.com
VITE_API_VERSION=v1
VITE_ENVIRONMENT=production
```

---

## ⚙️ Configuração Avançada

### 1. **Backend Health Check**
Verificar se já existe endpoint de health:

```python
# src/main.py ou similar
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

### 2. **Configuração de Produção**
Criar arquivo `backend/render.yaml` (opcional):

```yaml
services:
  - type: web
    name: clinic-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
```

### 3. **Scripts de Deploy**
Criar `backend/scripts/deploy.sh`:

```bash
#!/bin/bash
echo "🚀 Starting production deployment..."
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔍 Running health checks..."
python -c "import src.main; print('✅ App imports successfully')"

echo "🏃 Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2
```

---

## 🔗 URLs e Links

### **Após Deploy Bem-sucedido:**

#### **Backend:**
```
URL: https://clinic-backend-xxxx.onrender.com
API Docs: https://clinic-backend-xxxx.onrender.com/docs
Health: https://clinic-backend-xxxx.onrender.com/health
```

#### **Frontend:**
```
URL: https://clinic-frontend-xxxx.onrender.com
```

### **Configuração DNS (Opcional):**
- Backend: api.seudominio.com
- Frontend: app.seudominio.com

---

## 🚦 Deploy Automático

### **GitHub Actions (Opcional)**
Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Backend
        uses: bountyhill/render-action@0.6.0
        with:
          render-token: ${{ secrets.RENDER_API_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          service-id: ${{ secrets.RENDER_BACKEND_SERVICE_ID }}
          
      - name: Deploy Frontend  
        uses: bountyhill/render-action@0.6.0
        with:
          render-token: ${{ secrets.RENDER_API_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          service-id: ${{ secrets.RENDER_FRONTEND_SERVICE_ID }}
```

---

## 📊 Monitoramento

### **Logs no Render:**
```bash
# Via Dashboard
Render Dashboard → Service → Logs

# Via CLI (se configurado)
render logs --service-id=srv-xxxxx --follow
```

### **Métricas:**
- **CPU/Memory Usage:** Render Dashboard
- **Response Time:** Integrar com New Relic (gratuito)
- **Uptime:** Render built-in monitoring

---

## 🆘 Troubleshooting

### **Problemas Comuns:**

#### **Backend não inicia:**
```bash
# Verificar logs do Render
# Comum: Missing environment variables
# Solução: Verificar todas as env vars obrigatórias
```

#### **Conexão com MongoDB falha:**
```bash
# Verificar:
1. Connection string correto
2. IP whitelist configurado
3. Username/password corretos
4. Database name correto
```

#### **CORS errors no frontend:**
```bash
# Verificar:
1. CORS_ORIGINS inclui URL do frontend
2. Frontend está fazendo requests para URL correta do backend
```

#### **Frontend não carrega:**
```bash
# Verificar:
1. Build command executou com sucesso
2. Publish directory está correto (dist)
3. _redirects file existe
```

---

## 🔐 Segurança em Produção

### **Essencial:**
```bash
✅ SECRET_KEY único e forte (64+ caracteres)
✅ DEBUG=False
✅ ENVIRONMENT=production  
✅ MongoDB user com permissões mínimas
✅ CORS restrito às origens necessárias
✅ HTTPS forçado (Render faz automaticamente)
```

### **Recomendado:**
```bash
🔒 Rate limiting configurado
🔒 Logs estruturados
🔒 Backup automático do MongoDB
🔒 Monitoring e alertas
🔒 Domínio personalizado com SSL
```

---

## 📝 Checklist de Deploy

### **Pré-Deploy:**
- [ ] Código testado localmente
- [ ] Variáveis de ambiente configuradas
- [ ] MongoDB Atlas configurado
- [ ] Secrets seguros gerados

### **Deploy:**
- [ ] Backend service criado no Render
- [ ] Frontend static site criado no Render  
- [ ] Environment variables configuradas
- [ ] DNS configurado (se aplicável)

### **Pós-Deploy:**
- [ ] Health check funcionando
- [ ] Frontend carregando corretamente
- [ ] API endpoints respondendo
- [ ] Upload de arquivos funcionando
- [ ] Logs sendo gerados corretamente

---

**🎉 Parabéns! Sua aplicação está rodando em produção!**

Para suporte: [Render Documentation](https://render.com/docs) | [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
