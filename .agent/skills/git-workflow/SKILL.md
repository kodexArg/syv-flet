---
name: git-workflow
description: Git commit and push workflow for syv-flet. Conventional commits, always confirm before push.
allowed-tools: Bash, AskUserQuestion
---

# Git Workflow

## Repository Info
- **Repo:** kodexArg/syv-flet
- **Branch:** main (única rama)
- **User:** kodexArg
- **Tools:** gh (GitHub CLI disponible)

## Commit Standards

### Conventional Commits
Use prefixes:
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `refactor:` - Refactorización sin cambiar funcionalidad
- `test:` - Añadir o modificar tests
- `docs:` - Cambios en documentación
- `chore:` - Tareas de mantenimiento, config, deps

### Formato
```
tipo: descripción breve

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Workflow

### 1. Staging
```bash
git add <files>
```

### 2. Commit
```bash
git commit -m "$(cat <<'EOF'
feat: descripción del cambio

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### 3. Push
**CRITICAL:** ALWAYS ask user confirmation before pushing:
```bash
# After user confirms:
git push origin main
```

## GitHub CLI (gh)

Available commands with user permission:
- `gh pr create` - Crear pull requests
- `gh pr list` - Listar PRs
- `gh issue create` - Crear issues
- `gh repo view` - Ver info del repo

## Pre-push Checklist
- [ ] Tests pass: `uv run pytest tests/`
- [ ] Code formatted: `uv run black src/ tests/`
- [ ] Linting clean: `uv run ruff check src/ tests/`
- [ ] User confirmed push
