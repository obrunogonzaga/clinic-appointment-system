# Branch Protection Rules

Este documento define as regras de proteção de branch configuradas para este repositório.

## Branch `main` - Regras de Proteção

### ✅ Regras Configuradas via GitHub CLI:

1. **Pull Request Reviews**:
   - ✅ Exigir pelo menos 1 aprovação
   - ✅ Descartar revisões antigas quando novos commits são feitos
   - ✅ Não exigir revisão de proprietários de código

2. **Restrições de Push**:
   - ✅ Não permitir force pushes
   - ✅ Não permitir deleção da branch

3. **Administradores**:
   - ✅ Não aplicar regras para administradores (permite hotfixes emergenciais)

### 📋 Regras Adicionais Recomendadas (Configurar manualmente no GitHub):

**Para implementar via Interface Web do GitHub:**

1. **Acesse**: `Settings > Branches > Add rule` para branch `main`

2. **Configurar Branch name patterns**:
   ```
   main
   ```

3. **Marcar estas opções**:
   - ✅ Restrict pushes that create files that match a pattern
   - ✅ Require a pull request before merging
     - ✅ Require approvals: 1
     - ✅ Dismiss stale reviews when new commits are pushed
   - ✅ Restrict pushes to matching branches
   - ✅ Do not allow bypassing the above settings

4. **Branch patterns permitidos para merge**:
   - `develop`
   - `hotfix-*`

### 🎯 Objetivo das Regras:

- **`main`** só recebe merges de:
  - ✅ `develop` (releases normais)
  - ✅ `hotfix-*` (correções críticas)
- **Todos os outros merges** são bloqueados
- **Pull requests obrigatórios** para qualquer mudança
- **Force push bloqueado** para preservar histórico

## Branch `develop`

- Sem restrições especiais
- Recebe merges de feature branches
- Base para releases

## Padrão de Branches:

```
main
├── develop
│   ├── feature/authentication-system
│   ├── feature/user-management
│   └── feature/*
└── hotfix-*
    ├── hotfix-critical-auth-fix
    └── hotfix-database-migration
```

## Comandos GitHub CLI Utilizados:

```bash
# 1. Criar branch develop
git checkout main
git checkout -b develop
git push -u origin develop

# 2. Configurar proteção básica na main
gh api repos/obrunogonzaga/clinic-appointment-system/branches/main/protection \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

## Status de Implementação:

- ✅ Branch `develop` criada
- ✅ Branch `feature/authentication-system` criada
- ✅ Proteção básica da `main` configurada
- ⏳ **Próximo passo**: Configurar restrições de merge patterns na interface web do GitHub

---

**Nota**: Para configurar as restrições de merge patterns (permitir apenas `develop` e `hotfix-*`), é necessário usar a interface web do GitHub ou GitHub Enterprise features que não estão disponíveis via CLI para repositórios pessoais.