---
name: dev-environment
description: Set up and configure the SyV-Flet development environment. Use when setting up a new machine, installing dependencies, troubleshooting Python versions, or configuring IDEs.
allowed-tools: Bash, Read, Write, Edit
---

# SyV-Flet Development Environment

## Prerequisites

- **Python:** 3.13+ (3.12 minimum)
- **Package Manager:** `uv` (NOT pip)
- **Git:** 2.40+
- **OS:** Linux / macOS / WSL2

> Windows: Use WSL2 with Ubuntu 22.04+

## Initial Setup

```bash
cd /home/kodex/Dev/syv-flet

# 1. Install dependencies using uv (never pip!)
uv sync

# 2. Verify Python version
python --version              # Must be 3.12+
which python                  # Show Python path

# 3. List installed packages
uv pip list

# 4. Run tests to verify setup
uv run pytest tests/ -v

# 5. Format code
uv run black src/ tests/

# 6. Lint code
uv run ruff check src/ tests/
```

## Development Workflow

### Running the Application
```bash
# Standard execution
uv run python -m syv_flet

# With debug logging
FLET_DEBUG=1 uv run python -m syv_flet

# With verbose output
uv run python -m syv_flet --verbose
```

### Code Quality Before Commit
```bash
# Format all Python files
uv run black src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Run full test suite with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Check formatting (dry run)
uv run black --check src/ tests/
```

### Useful Development Commands
```bash
# Watch tests (auto-run on file changes)
uv run pytest tests/ --watch

# Run specific test file
uv run pytest tests/test_board.py -v

# Run tests by keyword
uv run pytest tests/ -k "hex" -v

# Install new dependency
uv add package-name

# Install dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

## IDE Configuration

### VS Code Setup

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": true
    }
  }
}
```

### Neovim Setup (LSP)

Ensure Mason has Python LSP:
```bash
:MasonInstall pylsp
:MasonInstall python-lsp-server
```

Configure in `init.lua`:
```lua
require("lspconfig").pylsp.setup {}
```

## Troubleshooting

### Wrong Python Version
```bash
pyenv versions                    # List installed versions
pyenv install 3.13.0              # Install specific version
pyenv local 3.13.0                # Use for this project
python --version                  # Verify
```

### Dependencies Conflict
```bash
rm uv.lock
uv sync --fresh
```

### Import Errors
```bash
# Clear Python cache
find src tests -type d -name __pycache__ -exec rm -rf {} +
find src tests -type f -name "*.pyc" -delete

# Reinstall
uv sync
```

### Tests Failing
```bash
# Verbose output
uv run pytest tests/ -v --tb=short

# Show print statements
uv run pytest tests/ -v -s

# Drop into debugger
uv run pytest tests/ --pdb
```

### Module Not Found
```bash
# Verify package structure
ls -la src/syv_flet/
ls -la src/syv_flet/__init__.py

# Try direct import
uv run python -c "from src.syv_flet.engine import board; print(board)"
```

## Environment Variables

Common development variables:
```bash
export PYTHONUNBUFFERED=1        # Unbuffered Python output
export FLET_DEBUG=1              # Flet debug logging
export PYTHONDONTWRITEBYTECODE=1 # Don't create .pyc files
```

Add to `.env` or shell rc file for persistence.

## Commands Reference

| Command | Purpose |
|---------|---------|
| `uv sync` | Install dependencies |
| `uv add <pkg>` | Add dependency |
| `uv run pytest` | Run tests |
| `uv run black` | Format code |
| `uv run ruff check` | Lint code |
| `uv run python -m syv_flet` | Run app |
| `uv lock --update-all` | Update dependencies |

See `.claude/docs/02-development-guide.md` for comprehensive commands.

## Next Steps

- Read `01-flet-architecture.md` for architecture overview
- Read `02-development-guide.md` for complete workflow guide
- Read `03-code-standards.md` for mandatory standards
- Explore `src/syv_flet/` directory structure
