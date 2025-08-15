# 🔧 Variáveis de Ambiente para Render - Guia Prático

**Configure essas variáveis no Render Dashboard → Environment**

## 🔴 OBRIGATÓRIAS (Configure Primeiro)

### 1. **Ambiente e Debug**
```bash
# Nome da variável: ENVIRONMENT
# Valor: production
ENVIRONMENT=production

# Nome da variável: DEBUG  
# Valor: False
DEBUG=False
```

### 2. **Segurança - SECRET_KEY**
```bash
# Nome da variável: SECRET_KEY
# Valor: Use o gerador de chave que criamos
SECRET_KEY=I$&Y45YjpoZgrB8IH(6xmy6(*d!^LuzlY^8HRws-G8=t#UyYbW8=#FyLH14Y+6am

# ⚠️ GERE UMA NOVA chave executando:
# python3 scripts/generate-secret-key.py
```

### 3. **MongoDB (MongoDB Atlas)**
```bash
# Nome da variável: MONGODB_URL
# Valor: Sua connection string do MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net

# Nome da variável: DATABASE_NAME
# Valor: clinic_db
DATABASE_NAME=clinic_db
```

### 4. **CORS - Frontend URL**
```bash
# Nome da variável: CORS_ORIGINS
# Valor: URL do seu frontend no Render (JSON array como string)
CORS_ORIGINS=["https://seu-frontend-name.onrender.com"]

# 📝 SUBSTITUA "seu-frontend-name" pelo nome real do seu frontend no Render
```

## 🟡 RECOMENDADAS (Configure Depois)

### 5. **Aplicação Info**
```bash
# Nome da variável: APP_NAME
# Valor: Clinic Appointment System
APP_NAME=Clinic Appointment System

# Nome da variável: APP_VERSION
# Valor: 1.0.0
APP_VERSION=1.0.0
```

### 6. **Tokens e Autenticação**
```bash
# Nome da variável: ACCESS_TOKEN_EXPIRE_MINUTES
# Valor: 60
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Nome da variável: REFRESH_TOKEN_EXPIRE_DAYS
# Valor: 7
REFRESH_TOKEN_EXPIRE_DAYS=7

# Nome da variável: ALGORITHM
# Valor: HS256
ALGORITHM=HS256
```

### 7. **Upload de Arquivos**
```bash
# Nome da variável: MAX_UPLOAD_SIZE
# Valor: 10485760
MAX_UPLOAD_SIZE=10485760

# Nome da variável: ALLOWED_EXTENSIONS
# Valor: ["xlsx","xls","csv"]
ALLOWED_EXTENSIONS=["xlsx","xls","csv"]
```

### 8. **Logs**
```bash
# Nome da variável: LOG_LEVEL
# Valor: INFO
LOG_LEVEL=INFO

# Nome da variável: LOG_FORMAT
# Valor: json
LOG_FORMAT=json
```

## 🟢 OPCIONAIS (Configure Se Precisar)

### 9. **Email (Se usar notificações por email)**
```bash
# Nome da variável: EMAIL_HOST
# Valor: smtp.gmail.com
EMAIL_HOST=smtp.gmail.com

# Nome da variável: EMAIL_PORT
# Valor: 587
EMAIL_PORT=587

# Nome da variável: EMAIL_USERNAME
# Valor: seu_email@gmail.com
EMAIL_USERNAME=seu_email@gmail.com

# Nome da variável: EMAIL_PASSWORD
# Valor: sua_senha_de_app_do_gmail
EMAIL_PASSWORD=sua_senha_de_app

# Nome da variável: EMAIL_FROM
# Valor: noreply@seudominio.com
EMAIL_FROM=noreply@clinicapp.com

# Nome da variável: EMAIL_USE_TLS
# Valor: True
EMAIL_USE_TLS=True
```

### 10. **Rate Limiting**
```bash
# Nome da variável: RATE_LIMIT_REQUESTS
# Valor: 100
RATE_LIMIT_REQUESTS=100

# Nome da variável: RATE_LIMIT_WINDOW_SECONDS
# Valor: 60
RATE_LIMIT_WINDOW_SECONDS=60
```

## 🚨 IMPORTANTES - NÃO CONFIGURE ESSAS:

```bash
# ❌ NÃO configure essas - o Render gerencia automaticamente:
# PORT - Render define automaticamente
# HOST - Sempre 0.0.0.0 no Render
# RELOAD - Sempre False em produção
```

---

## 📋 CHECKLIST RÁPIDO

### ✅ **Mínimo Absoluto (4 variáveis):**
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`  
- [ ] `SECRET_KEY=sua_chave_gerada`
- [ ] `MONGODB_URL=sua_connection_string`

### ✅ **Recomendado (+ 3 variáveis):**
- [ ] `DATABASE_NAME=clinic_db`
- [ ] `CORS_ORIGINS=["https://seu-frontend.onrender.com"]`
- [ ] `LOG_LEVEL=INFO`

### ✅ **Completo (+ 5 variáveis):**
- [ ] `APP_NAME=Clinic Appointment System`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- [ ] `MAX_UPLOAD_SIZE=10485760`
- [ ] `ALLOWED_EXTENSIONS=["xlsx","xls","csv"]`
- [ ] `LOG_FORMAT=json`

---

## 🔗 Como Configurar no Render Dashboard

### 1. **Acesse seu Backend Service**
```
Render Dashboard → Services → Seu Backend Service
```

### 2. **Vá para Environment**
```
Menu lateral → Environment
```

### 3. **Adicione cada variável**
```
Click "Add Environment Variable"
Key: ENVIRONMENT
Value: production
Click "Save Changes"
```

### 4. **Repita para todas as variáveis**
```
Uma variável por vez, seguindo a lista acima
```

---

## 📝 Exemplo Prático - MongoDB Atlas

### **Se sua connection string for:**
```
mongodb+srv://clinic_user:minha_senha_123@cluster0.abc123.mongodb.net
```

### **Configure assim:**
```bash
MONGODB_URL=mongodb+srv://clinic_user:minha_senha_123@cluster0.abc123.mongodb.net
DATABASE_NAME=clinic_db
```

---

## 🔧 Frontend Environment Variables

### **Para o Frontend (Static Site):**
```bash
# Nome da variável: VITE_API_URL
# Valor: URL do seu backend no Render
VITE_API_URL=https://seu-backend-name.onrender.com

# Nome da variável: VITE_ENVIRONMENT
# Valor: production  
VITE_ENVIRONMENT=production
```

---

## ⚠️ ERROS COMUNS

### **❌ Erro: "CORS policy"**
```bash
# Problema: CORS_ORIGINS incorreto
# Solução: Verificar URL exata do frontend
CORS_ORIGINS=["https://clinic-frontend-abc123.onrender.com"]
```

### **❌ Erro: "Database connection failed"**
```bash
# Problema: MONGODB_URL incorreta
# Solução: Verificar connection string no MongoDB Atlas
# Verificar se IP 0.0.0.0/0 está liberado
```

### **❌ Erro: "Invalid token"**
```bash
# Problema: SECRET_KEY muito simples
# Solução: Usar a chave gerada pelo script
SECRET_KEY=I$&Y45YjpoZgrB8IH(6xmy6(*d!^LuzlY^8HRws-G8=t#UyYbW8=#FyLH14Y+6am
```
