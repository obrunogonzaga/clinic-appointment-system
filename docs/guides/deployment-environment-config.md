# Configuração de Ambiente para Deploy

Este documento explica como configurar as variáveis de ambiente para diferentes ambientes (local, staging, produção).

## Variáveis Principais

### Backend (FastAPI)

**CORS_ORIGINS**: Lista de domínios permitidos para requisições CORS
- Formato: JSON array ou lista separada por vírgulas
- Exemplos:
  - JSON: `["http://localhost:3000", "https://clinica.widia.io"]`
  - Vírgulas: `http://localhost:3000,https://clinica.widia.io`

**JWT_SECRET_KEY**: Chave secreta para JWT (deve ser única por ambiente)

### Frontend (React)

**API_URL**: URL do backend API para este ambiente

## Configuração por Ambiente

### 1. Local (Desenvolvimento)

**Backend (.env):**
```bash
JWT_SECRET_KEY=local-jwt-secret-key
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Frontend (.env ou docker-compose):**
```bash
API_URL=http://localhost:8000
```

### 2. Staging

**Backend:**
```bash
JWT_SECRET_KEY=staging-jwt-secret-key-change-this
CORS_ORIGINS=["https://staging.clinica.widia.io", "https://staging-api.widia.io"]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Frontend:**
```bash
API_URL=https://staging-api.widia.io
```

### 3. Produção

**Backend:**
```bash
JWT_SECRET_KEY=production-jwt-secret-key-super-secure
CORS_ORIGINS=["https://clinica.widia.io", "https://api.widia.io"]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Frontend:**
```bash
API_URL=https://api.widia.io
```

## Como Aplicar

### Docker Compose
No arquivo `docker-compose.yml` ou `docker-compose.prod.yml`:

```yaml
services:
  backend:
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
  
  frontend:
    environment:
      - API_URL=${API_URL}
```

### Plataformas de Deploy (ex: Railway, Heroku, etc.)
Configure as variáveis de ambiente na interface da plataforma ou via CLI:

```bash
# Exemplo para Railway
railway variables set JWT_SECRET_KEY="your-secret-key"
railway variables set CORS_ORIGINS="https://clinica.widia.io,https://api.widia.io"
railway variables set API_URL="https://api.widia.io"
```

## Verificação

### Backend
Acesse: `https://api.widia.io/api/v1/` 
Deve retornar JSON com endpoints disponíveis

### Frontend
Verifique no console do navegador se o config.js foi carregado:
```javascript
console.log(window.ENV.API_URL);
```

## Troubleshooting

### Erro de CORS
- Verifique se o domínio do frontend está na lista `CORS_ORIGINS`
- Certifique-se de usar `https://` em produção

### Frontend não conecta com Backend
- Verifique se `API_URL` está correto
- Confirme que o `config.js` foi gerado com a URL correta
- Verifique os logs do container do frontend

### JWT não funciona
- Certifique-se de que `JWT_SECRET_KEY` é a mesma entre deploys
- Verifique se os cookies estão sendo enviados corretamente