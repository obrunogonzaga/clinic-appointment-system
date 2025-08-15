# ⚡ CONFIGURAÇÃO RÁPIDA RENDER

## 🎯 Copie e Cole Estas Variáveis:

### 📋 No Render Dashboard → Environment

```
Key: ENVIRONMENT
Value: production

Key: DEBUG  
Value: False

Key: SECRET_KEY
Value: $Fo+eoH=EcT+w4_tMSy=T)-RPFW6m-d5O!Vw4pK1sE*A(0XulZ^ufdV@Rr0zHeXq

Key: DATABASE_NAME
Value: clinic_db

Key: LOG_LEVEL
Value: INFO
```

## 🔗 Variáveis que VOCÊ precisa substituir:

```
Key: MONGODB_URL
Value: [SUA CONNECTION STRING DO MONGODB ATLAS]
Exemplo: mongodb+srv://clinicuser:suasenha@cluster0.abc123.mongodb.net

Key: CORS_ORIGINS  
Value: ["https://SEU-FRONTEND-NAME.onrender.com"]
Exemplo: ["https://clinic-frontend-xyz.onrender.com"]
```

## 📝 Como Adicionar:

1. **Render Dashboard** → **Services** → **Seu Backend Service**
2. **Environment** (menu lateral)
3. **Add Environment Variable**
4. Cole cada **Key** e **Value** acima
5. **Save Changes** após cada uma

## ⚠️ IMPORTANTE:

- Use a SECRET_KEY exata de cima (com todos os caracteres especiais)
- Substitua MONGODB_URL pela sua connection string real
- Substitua CORS_ORIGINS pela URL real do seu frontend
- Certifique-se de que DEBUG=False (não True!)

## 🎯 Resultado Final:

Suas 7 variáveis configuradas = Backend funcionando! 🚀
