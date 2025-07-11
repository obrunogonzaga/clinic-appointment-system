# Pull Request

## 📋 Descrição

<!-- Descreva brevemente as mudanças feitas neste PR -->

## 🔗 Issue Relacionada

<!-- Link para a issue que este PR resolve -->
Closes #(issue number)

## 🧪 Tipo de Mudança

<!-- Marque as opções relevantes -->

- [ ] 🐛 Bug fix (mudança que corrige um problema)
- [ ] ✨ Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] 💥 Breaking change (correção ou funcionalidade que causaria falha em funcionalidade existente)
- [ ] 📝 Documentação (mudanças apenas na documentação)
- [ ] 🎨 Refatoração (mudança de código que não corrige bug nem adiciona funcionalidade)
- [ ] ⚡ Melhoria de performance
- [ ] 🧹 Limpeza de código
- [ ] 🔧 Configuração/Build

## 🚀 Componentes Afetados

<!-- Marque os componentes que foram modificados -->

- [ ] Frontend (React/TypeScript)
- [ ] Backend (FastAPI/Python)
- [ ] Database (MongoDB)
- [ ] Docker Configuration
- [ ] CI/CD Pipelines
- [ ] Documentation

## 🧪 Como Testar

<!-- Descreva os passos para testar as mudanças -->

1. Checkout desta branch
2. Execute `make setup` (se necessário)
3. Execute `make up` para iniciar os serviços
4. Navegue para...
5. Teste...

## 📋 Checklist

### Geral
- [ ] Meu código segue as convenções de estilo do projeto
- [ ] Fiz uma auto-revisão do meu código
- [ ] Comentei meu código, especialmente em áreas complexas
- [ ] Fiz mudanças correspondentes na documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Não há código comentado ou debug logs

### Testes
- [ ] Adicionei testes que provam que minha correção é efetiva ou que minha funcionalidade funciona
- [ ] Testes unitários novos e existentes passam localmente
- [ ] Testes de integração passam (se aplicável)

### Backend (se aplicável)
- [ ] Adicionei type hints apropriados
- [ ] Validei entrada de dados com Pydantic
- [ ] Adicionei logging apropriado
- [ ] Tratei erros adequadamente
- [ ] Atualizei a documentação da API (se necessário)

### Frontend (se aplicável)
- [ ] Componentes são responsivos
- [ ] Adicionei testes para novos componentes
- [ ] Considerei acessibilidade (WCAG)
- [ ] Tratei estados de loading e erro
- [ ] Implementei i18n (se necessário)

### Database (se aplicável)
- [ ] Criei scripts de migração (se necessário)
- [ ] Atualizei índices do MongoDB (se necessário)
- [ ] Validei performance das queries

### Segurança
- [ ] Validei entrada do usuário adequadamente
- [ ] Implementei autorização apropriada
- [ ] Não expus informações sensíveis
- [ ] Atualizei dependências com vulnerabilidades

## 📸 Screenshots

<!-- Adicione screenshots das mudanças na UI, se aplicável -->

## 📝 Notas Adicionais

<!-- Adicione qualquer informação adicional para os revisores -->

## 🔄 Breaking Changes

<!-- Se este PR contém breaking changes, descreva-as aqui -->

<!-- Se não há breaking changes, remova esta seção -->

---

**Para os Revisores:**
- [ ] Código foi revisado
- [ ] Testes foram executados
- [ ] Documentação foi verificada
- [ ] Performance foi considerada
- [ ] Segurança foi avaliada