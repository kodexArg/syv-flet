# Development Guide - SyV-Flet

**Version:** 1.0
**Date:** January 16, 2026
**Stack:** Python 3.12 + Flet + uv
**Supported Platforms:** Linux (dev), Windows (dev), Android (build)

---

## 1. Initial Project Setup

### 1.1. Prerequisites

```bash
# Check versions
python3 --version        # >= 3.12
uv --version             # >= 0.1.0 (https://github.com/astral-sh/uv)
```

### 1.2. Clone and Configure

```bash
cd /home/kodex/Dev/syv-flet

# Create folder structure
mkdir -p src/syv-flet/{engine,ui/{screens,components,controllers,models,styles},utils}
mkdir -p tests
mkdir -p assets/{images,fonts}

# Initialize pyproject.toml (if not exists)
cat > pyproject.toml << 'EOF'
[project]
name = "syv-flet"
version = "0.1.0"
description = "Hexagonal strategy game in Python + Flet"
authors = [{name = "Team SyV-Flet"}]
requires-python = ">=3.12"

dependencies = [
    "flet>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
python-version = "3.12"

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short"
EOF
```

### 1.3. Install Dependencies

```bash
# Create lock file and install dependencies
uv sync --all-extras

# Verify installation
uv run python -c "import flet; print(f'Flet {flet.__version__}')"
```

---

## 2. Daily Development Workflow

### 2.1. Start Development Session

```bash
cd /home/kodex/Dev/syv-flet

# Activate environment (uv loads automatically)
# To explicitly activate:
source .venv/bin/activate  # Linux
# or
.\.venv\Scripts\activate   # Windows

# Verify
which python  # Should point to .venv
```

### 2.2. Run Application with Hot Reload

```bash
# Normal mode (default)
uv run python -m syv-flet.main

# With verbose Flet logging
FLET_DEBUG=1 uv run python -m syv-flet.main

# Specify platform
FLET_WEB_PORT=8080 uv run python -m syv-flet.main  # Web debug

# In application: press Ctrl+R for hot reload
```

**Note:** Hot reload works when modifying files in `src/syv-flet/ui/`. For engine changes, restart application.

### 2.3. Test-Driven Development

```bash
# Run all tests
uv run pytest

# Tests with coverage
uv run pytest --cov=src/syv-flet

# Watch mode (requires pytest-watch, installable with uv)
uv run pytest-watch

# Specific test
uv run pytest tests/test_board.py::test_distance -v

# Engine tests (fast, no Flet)
uv run pytest tests/engine/ -v

# UI tests (requires Flet mocking)
uv run pytest tests/ui/ -v
```

---

## 3. Code Formatting and Linting

### 3.1. Black (Formatter)

```bash
# Format entire project
uv run black src/ tests/

# Format specific file
uv run black src/syv-flet/main.py

# Check without modifying
uv run black --check src/ tests/

# Verbose
uv run black -v src/
```

### 3.2. Ruff (Linter - Fast PyLint alternative)

```bash
# Check style
uv run ruff check src/ tests/

# Autofix simple issues
uv run ruff check --fix src/ tests/

# Specific rules (e.g., imports only)
uv run ruff check src/ --select I
```

### 3.3. MyPy (Type Checking)

```bash
# Type check project
uv run mypy src/

# Configuration in pyproject.toml:
# [tool.mypy]
# python_version = "3.12"
# warn_return_any = true
# disallow_untyped_defs = false
```

### 3.4. Pre-commit Hook (Optional)

```bash
# Create pre-commit script
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
uv run black --check src/ tests/ || exit 1
uv run ruff check src/ tests/ || exit 1
uv run pytest -x || exit 1
EOF

chmod +x .git/hooks/pre-commit
```

---

## 4. Debugging

### 4.1. Basic Logging

```python
# In src/syv-flet/utils/logger.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# In modules:
from syv-flet.utils.logger import logger

logger.debug("Unit moved to (5, 3)")
logger.info("Combat resolved: unit_a wins")
logger.warning("Unit isolated from command chain")
logger.error("Invalid order format")
```

```bash
# Run with DEBUG logging
HEXSIM_LOG_LEVEL=DEBUG uv run python -m syv-flet.main
```

### 4.2. Debugging with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SyV-Flet (Flet)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/syv-flet/main.py",
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

**Usage:**
1. Set breakpoint: Gray dot on left side of editor
2. F5 or Run → Start Debugging
3. Inspect variables in Debug Console

### 4.3. Print Debugging (Quick)

```python
# In engine/state.py
print(f"[ENGINE] Turn {self.turn}: Processing {len(self.units)} units")
print(f"[COMBAT] {unit_a.id} vs {unit_b.id}: Winner = {winner}")
```

```bash
# Capture output
uv run python -m syv-flet.main 2>&1 | grep "\[ENGINE\]"
```

---

## 5. Dependency Management with `uv`

### 5.1. Add Dependencies

```bash
# Add new dependency
uv add flet-core

# Add dev dependency
uv add --dev pytest-asyncio

# List installed dependencies
uv pip list

# Update lock file
uv sync --upgrade
```

### 5.2. Pin Versions

```bash
# Specific version in pyproject.toml
# dependencies = ["flet>=0.24.0,<0.25.0"]

uv sync --upgrade
```

### 5.3. Clean Environment

```bash
# Remove unused dependencies (dry-run)
uv pip compile --dry-run

# Clean cache
rm -rf .venv uv.lock
uv sync
```

---

## 6. Minimal File Structure to Start

### 6.1. Entry Point

```bash
# src/syv-flet/__init__.py (empty)
touch src/syv-flet/__init__.py

# src/syv-flet/main.py
cat > src/syv-flet/main.py << 'EOF'
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

chmod +x src/syv-flet/main.py
```

### 6.2. Minimal Engine Module

```bash
cat > src/syv-flet/engine/__init__.py << 'EOF'
"""Game engine module - agnostic to Flet."""
EOF

cat > src/syv-flet/engine/board.py << 'EOF'
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

### 6.3. Minimal Test

```bash
cat > tests/test_board.py << 'EOF'
from syv-flet.engine.board import Board

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

### 6.4. Run Everything

```bash
# Format
uv run black src/ tests/

# Lint
uv run ruff check src/

# Tests
uv run pytest tests/ -v

# Application
uv run python -m syv-flet.main
```

---

## 7. Git Workflow (Recommended)

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

---

## 8. IDE Configuration (Neovim + Mason LSPs)

### 8.1. Neovim Init (init.lua)

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

### 8.2. Keybindings

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

---

## 9. Environment Variables

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

---

## 10. Common Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'syv-flet'`

**Solution:**
```bash
# Ensure you're in project root
cd /home/kodex/Dev/syv-flet

# Reinstall with sync
uv sync

# Run correctly
uv run python -m syv-flet.main
```

### Issue: Flet doesn't render on X11/Wayland

**Solution:**
```bash
# Check session
echo $XDG_SESSION_TYPE  # "x11" or "wayland"

# For Wayland (NVIDIA)
FLET_DISPLAY_WAYLAND=0 uv run python -m syv-flet.main
```

### Issue: Tests can't find modules

**Solution:**
```bash
# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

uv run pytest tests/
```

### Issue: Hot reload not working

**Solution:**
- Verify you're modifying files in `src/syv-flet/ui/`
- Don't touch `pyproject.toml` (restart app)
- In terminal: press `Ctrl+R` after changes

---

## 11. CI/CD Preparation (GitHub Actions)

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
      run: uv run pytest tests/ --cov=src/syv-flet
```

---

## 12. Quick Commands (Cheat Sheet)

```bash
# Development
uv run python -m syv-flet.main              # Run app
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
FLET_DEBUG=1 uv run python -m syv-flet.main # Debug mode
uv run pytest -xvs tests/test_board.py    # Verbose + stop on first failure
```

---

**NEXT STEP:** Implement folder structure and entry point. See [01-architecture.md](./01-architecture.md) for architectural details.
