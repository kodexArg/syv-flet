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

## Advanced Development Topics

### 1. Development Workflow Deep Dive

#### Git Workflow (Recommended)

```bash
# Feature branch
git checkout -b feature/hex-grid-rendering

# Frequent commits
git add src/syv-flet/ui/components/hex_grid.py
git commit -m "feat: implement static hexagon canvas"

# Push when ready for review
git push origin feature/hex-grid-rendering

# Merge to main after tests + review
```

#### IDE Configuration (Neovim + Mason LSPs)

**Neovim Init (init.lua):**

```lua
-- Treesitter for Python
local treesitter = require("nvim-treesitter.configs")
treesitter.setup {
  ensure_installed = { "python", "toml" },
  highlight = { enable = true },
}

-- LSP Python (Pyright via Mason)
require("mason").setup()
require("mason-lspconfig").setup {
  ensure_installed = { "pyright" },
}

-- Formatter (Black)
require("conform").setup {
  formatters_by_ft = {
    python = { "black", "isort" },
  },
}
```

**Keybindings:**

```lua
local opts = { noremap = true, silent = true }

-- Format on save
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.py",
  callback = function() vim.lsp.buf.format() end,
})

-- Jump to definition
vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)

-- Find references
vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
```

### 2. Environment Variables

Create `.env` (don't commit):

```bash
# .env
FLET_DEBUG=0
HEXSIM_LOG_LEVEL=INFO
HEXSIM_BOARD_RADIUS=20
HEXSIM_FPS_TARGET=60
```

Load in main.py:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("FLET_DEBUG", "0") == "1"
LOG_LEVEL = os.getenv("HEXSIM_LOG_LEVEL", "INFO")
BOARD_RADIUS = int(os.getenv("HEXSIM_BOARD_RADIUS", "20"))
FPS_TARGET = int(os.getenv("HEXSIM_FPS_TARGET", "60"))
```

### 3. Common Troubleshooting

#### Issue: `ModuleNotFoundError: No module named 'syv-flet'`

**Solution:**
```bash
# Ensure you're in project root
cd /home/kodex/Dev/syv-flet

# Reinstall with sync
uv sync

# Run correctly
uv run python -m syv_flet.main
```

#### Issue: Flet doesn't render on X11/Wayland

**Solution:**
```bash
# Check session
echo $XDG_SESSION_TYPE  # "x11" or "wayland"

# For Wayland (NVIDIA)
FLET_DISPLAY_WAYLAND=0 uv run python -m syv_flet.main
```

#### Issue: Tests can't find modules

**Solution:**
```bash
# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

uv run pytest tests/
```

#### Issue: Hot reload not working

**Solution:**
- Verify you're modifying files in `src/syv_flet/ui/`
- Don't touch `pyproject.toml` (restart app)
- In terminal: press `Ctrl+R` after changes

### 4. CI/CD Preparation (GitHub Actions)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]

    steps:
    - uses: actions/checkout@v3
    - name: Install uv
      run: pip install uv
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Sync dependencies
      run: uv sync --all-extras
    - name: Lint
      run: uv run ruff check src/ tests/
    - name: Format check
      run: uv run black --check src/ tests/
    - name: Tests
      run: uv run pytest tests/ --cov=src/syv_flet
```

### 5. VS Code Setup

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

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SyV-Flet (Flet)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/syv_flet/main.py",
      "console": "integratedTerminal",
      "justMyCode": true,
      "env": {
        "FLET_DEBUG": "1"
      }
    },
    {
      "name": "Unit Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

---

## Command Reference Cheat Sheet

```bash
# Development
uv run python -m syv_flet.main              # Run app
uv run pytest                              # Run tests
uv run black src/ tests/                   # Format
uv run ruff check --fix src/               # Lint + fix

# Adding packages
uv add flet-core                           # Add dependency
uv add --dev pytest-xdist                  # Add dev dependency

# Sync
uv sync                                    # Install from lock
uv sync --upgrade                          # Upgrade all

# Clean
rm -rf .venv uv.lock                       # Hard reset
uv sync                                    # Reinstall

# Debugging
FLET_DEBUG=1 uv run python -m syv_flet.main # Debug mode
uv run pytest -xvs tests/test_board.py    # Verbose + stop on first failure

# Code Quality (Complete Pre-Commit Flow)
uv run black src/ tests/
uv run ruff check --fix src/ tests/
uv run mypy src/
uv run pytest tests/ --cov=src/syv_flet --cov-report=term-missing
```

---

## Minimal File Structure to Start

### Entry Point

```bash
# src/syv_flet/__init__.py (empty)
touch src/syv_flet/__init__.py

# src/syv_flet/main.py
cat > src/syv_flet/main.py << 'EOF'
import flet as ft

def main(page: ft.Page):
    page.title = "SyV-Flet"
    page.window_width = 1280
    page.window_height = 720

    title = ft.Text("SyV-Flet", size=40, weight="bold")
    subtitle = ft.Text("Hexagonal Strategy Game", size=16)

    page.add(
        ft.Column([title, subtitle], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.run(main)
EOF

chmod +x src/syv_flet/main.py
```

### Minimal Engine Module

```bash
cat > src/syv_flet/engine/__init__.py << 'EOF'
"""Game engine module - agnostic to Flet."""
EOF

cat > src/syv_flet/engine/board.py << 'EOF'
from typing import List, Tuple

class Board:
    """Hexagonal board using axial coordinates (q, r)."""

    def __init__(self, radius: int = 20):
        self.radius = radius

    def is_valid(self, q: int, r: int) -> bool:
        """Check if (q, r) is within board bounds."""
        s = -q - r
        return max(abs(q), abs(r), abs(s)) <= self.radius

    def neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Return 6 adjacent hexagons (if valid)."""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [
            (q + dq, r + dr) for dq, dr in directions
            if self.is_valid(q + dq, r + dr)
        ]

    def distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance in hexagonal grid."""
        aq, ar = a
        bq, br = b
        as_ = -aq - ar
        bs_ = -bq - br
        return (abs(aq - bq) + abs(ar - br) + abs(as_ - bs_)) // 2
EOF
```

### Minimal Test

```bash
cat > tests/test_board.py << 'EOF'
from syv_flet.engine.board import Board

def test_board_valid():
    board = Board(radius=5)
    assert board.is_valid(0, 0)
    assert board.is_valid(3, 2)
    assert not board.is_valid(10, 10)

def test_distance():
    board = Board()
    assert board.distance((0, 0), (1, 0)) == 1
    assert board.distance((0, 0), (2, 0)) == 2

if __name__ == "__main__":
    test_board_valid()
    test_distance()
    print("✓ All tests passed")
EOF
```

### Run Everything

```bash
# Format
uv run black src/ tests/

# Lint
uv run ruff check src/

# Tests
uv run pytest tests/ -v

# Application
uv run python -m syv_flet.main
```

---

## Quick Start (Copy-Paste)

```bash
# Navigate to project
cd /home/kodex/Dev/syv-flet

# Setup Python environment
python3 --version        # >= 3.12
uv --version             # >= 0.1.0

# Create folder structure
mkdir -p src/syv_flet/{engine,ui/{screens,components,controllers,models,styles},utils}
mkdir -p tests
mkdir -p assets/{images,fonts}

# Install dependencies using uv (never pip!)
uv sync

# Verify installation
uv run python -c "import flet; print(f'Flet {flet.__version__}')"

# Run tests to verify setup
uv run pytest

# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/

# Run application
uv run python -m syv_flet.main
```

---

## Next Steps

- See `PRD.md` for complete product specification
- See `code-standards` skill for mandatory code standards
- See `hex-grid-math` skill for hexagonal coordinate mathematics
- Explore `src/syv_flet/` directory structure
