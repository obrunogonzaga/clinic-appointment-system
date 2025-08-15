# 🌐 Frontend - Configuração no Render

## 🎯 Variáveis de Ambiente para Static Site

### 📋 Configure no Render Dashboard:

**Caminho:** `Render Dashboard → Services → Seu Frontend Static Site → Environment`

### 🔴 OBRIGATÓRIAS (Configure Primeiro):

```
Key: VITE_API_URL
Value: https://SEU-BACKEND-NAME.onrender.com

Key: VITE_ENVIRONMENT
Value: production

Key: VITE_API_VERSION
Value: v1
```

### 🟡 RECOMENDADAS (Configure Depois):

```
Key: VITE_APP_NAME
Value: Clinic Appointment System

Key: VITE_APP_VERSION
Value: 1.0.0

Key: VITE_MAX_UPLOAD_SIZE
Value: 10485760

Key: VITE_DEFAULT_PAGE_SIZE
Value: 50
```

---

## 🔧 Como Configurar no Render:

### 1. **Acesse o Static Site:**
```
Render Dashboard → Services → Seu Frontend Static Site
```

### 2. **Vá para Environment:**
```
Menu lateral → Environment
```

### 3. **Adicione cada variável:**
```
Click "Add Environment Variable"
Key: VITE_API_URL
Value: https://clinic-backend-abc123.onrender.com
Click "Add"
```

### 4. **Repita para todas as variáveis**

### 5. **Redeploy:**
```
Após adicionar todas as variáveis → Manual Deploy
```

---

## ⚠️ IMPORTANTE - Static Sites:

### **Diferenças do Backend:**
- ❌ **NÃO tem** "Import from .env"
- ✅ **TEM** que adicionar uma por uma
- ⚡ Variáveis aplicadas no **BUILD TIME**
- 🔄 **REDEPLOY** necessário após mudanças

### **Ordem de Deploy:**
1. **Backend** primeiro (para obter a URL)
2. **Frontend** depois (usando a URL do backend)

---

## 🔗 Exemplo Prático:

### **Se seu backend estiver em:**
```
https://clinic-backend-abc123.onrender.com
```

### **Configure assim:**
```
VITE_API_URL=https://clinic-backend-abc123.onrender.com
```

### **O frontend vai fazer requests para:**
```
https://clinic-backend-abc123.onrender.com/api/v1/appointments
https://clinic-backend-abc123.onrender.com/api/v1/drivers
etc...
```

---

## 📋 Checklist Frontend:

- [ ] Backend deployado e funcionando
- [ ] URL do backend copiada
- [ ] Variáveis VITE_* configuradas no Static Site
- [ ] Redeploy do frontend executado
- [ ] Teste: Frontend carrega sem erros de CORS
- [ ] Teste: Frontend consegue fazer requests para API

---

## 🆘 Troubleshooting:

### **❌ "Failed to fetch" / CORS errors:**
```bash
# Problema: Backend não está recebendo requests
# Soluções:
1. Verificar se VITE_API_URL está correta
2. Verificar se backend tem CORS configurado para frontend
3. Verificar se ambos os serviços estão online
```

### **❌ Frontend mostra dados de localhost:**
```bash
# Problema: Variáveis não foram aplicadas
# Soluções:
1. Verificar se variáveis estão no formato VITE_*
2. Fazer redeploy do frontend
3. Verificar se não há cache no navegador
```

### **❌ Build falha no Render:**
```bash
# Problema: Variáveis obrigatórias faltando
# Solução: Configurar pelo menos VITE_API_URL
```
