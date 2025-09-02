# Git Workflow Rules - Clinic Appointment System

**CRITICAL RULE**: This project follows a **strict branch-based workflow**. All changes MUST go through Pull Requests.

## 🚫 NEVER DO THIS:

```bash
# ❌ FORBIDDEN - Never commit directly to main or develop
git checkout main
git commit -m "some changes"
git push

# ❌ FORBIDDEN - Never commit directly to develop  
git checkout develop
git commit -m "some changes"
git push
```

## ✅ ALWAYS DO THIS:

### For New Features:
```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Work on your feature
git add .
git commit -m "feat: implement your feature"

# 4. Push feature branch
git push -u origin feature/your-feature-name

# 5. Create PR: feature/your-feature-name → develop
gh pr create --base develop --title "feat: your feature" --body "Description"
```

### For Hotfixes (Critical Production Fixes):
```bash
# 1. Start from main (latest production)
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix-critical-issue-description

# 3. Fix the critical issue
git add .
git commit -m "hotfix: fix critical issue"

# 4. Push hotfix branch
git push -u origin hotfix-critical-issue-description

# 5. Create PR: hotfix-* → main
gh pr create --base main --title "hotfix: critical fix" --body "Urgent fix description"

# 6. After merge to main, also merge to develop
gh pr create --base develop --title "hotfix: sync critical fix to develop"
```

## Branch Naming Conventions:

### Feature Branches:
- `feature/authentication-system`
- `feature/user-management`
- `feature/appointment-scheduler`
- `feature/excel-import`
- `feature/pdf-generation`

### Hotfix Branches:
- `hotfix-security-vulnerability`
- `hotfix-database-connection`
- `hotfix-authentication-bypass`
- `hotfix-data-corruption`

## Pull Request Flow:

### Feature Development:
```
feature/branch → develop → main
     ↓              ↓       ↓
   PR #1          PR #2   Release
 (Review)       (Review)
```

### Hotfix Flow:
```
hotfix/branch → main
     ↓           ↓
   PR #1    Emergency Release
 (Review)
     ↓
hotfix/branch → develop  
     ↓           ↓
   PR #2    Sync to develop
 (Review)
```

## Branch Protection Summary:

- **`main`**: Protected, requires PR + 1 approval
- **`develop`**: Should be protected, requires PR + 1 approval (recommended)
- **`feature/*`**: No restrictions, regular development
- **`hotfix-*`**: Can merge to main (for emergencies)

## Commit Message Standards:

```bash
# Features
git commit -m "feat: add user authentication system"
git commit -m "feat: implement Excel import functionality"

# Bug fixes
git commit -m "fix: resolve login redirect loop"
git commit -m "fix: correct database connection timeout"

# Hotfixes
git commit -m "hotfix: patch security vulnerability in auth"
git commit -m "hotfix: fix critical data loss issue"

# Other types
git commit -m "docs: update API documentation"
git commit -m "refactor: improve code structure"
git commit -m "test: add unit tests for auth service"
git commit -m "chore: update dependencies"
```

## Emergency Procedures:

### Critical Production Issue:
1. **Immediately** create `hotfix-*` branch from `main`
2. Fix the issue with **minimal changes**
3. Create PR to `main` with **urgent** label
4. Get **immediate review** and merge
5. **Deploy** the hotfix
6. Create **second PR** to sync hotfix to `develop`

### Non-Critical Issues:
1. Create `feature/*` branch from `develop`
2. Fix the issue
3. Create PR to `develop`
4. Normal review process
5. Merge to `develop`
6. Wait for next release cycle

## Git Commands Cheat Sheet:

```bash
# Check current status
git status
git branch -a

# Switch branches safely  
git checkout develop
git pull origin develop

# Create new feature
git checkout -b feature/my-new-feature

# Clean up after PR merge
git checkout develop
git pull origin develop
git branch -d feature/completed-feature

# Emergency hotfix
git checkout main
git pull origin main
git checkout -b hotfix-urgent-fix

# Check what changed
git log --oneline develop..feature/my-branch
git diff develop...feature/my-branch
```

## Pre-commit Checklist:

Before creating any PR, ensure:
- [ ] Code follows project conventions
- [ ] Tests are passing (`make test`)
- [ ] Linting is clean (`make lint`)
- [ ] Security scan passed (`make check-security`)
- [ ] Branch is up to date with target branch
- [ ] Commit messages follow convention
- [ ] No sensitive data committed

## Claude Code Instructions:

When Claude Code is working on this project:

1. **NEVER** use `git commit` directly on `main` or `develop`
2. **ALWAYS** create feature branches for any changes
3. **ALWAYS** use descriptive branch names with `feature/` or `hotfix-` prefix
4. **ALWAYS** create PRs for merging changes
5. **ALWAYS** run quality checks before committing
6. **ALWAYS** update this workflow if needed

## Enforcement:

- Branch protection rules are configured on GitHub
- Direct pushes to `main` and `develop` are **blocked**
- All changes require **Pull Request review**
- CI/CD checks must **pass** before merge
- Quality gates ensure **code standards**

---

**Remember**: This workflow protects code quality, enables proper review, and prevents production issues. Following these rules is **mandatory** for all contributors.

## Quick Reference Commands:

```bash
# Start new feature
git checkout develop && git pull && git checkout -b feature/name

# Create PR to develop
gh pr create --base develop

# Start hotfix
git checkout main && git pull && git checkout -b hotfix-description  

# Create emergency PR to main
gh pr create --base main

# Clean up after merge
git checkout develop && git pull && git branch -d feature/old-branch
```