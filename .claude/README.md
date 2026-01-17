# SyV-Flet Documentation & Skills

This directory contains comprehensive documentation and automatic Claude Code skills for SyV-Flet development.

## Documentation Files

### Architecture & Design
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System design, layered architecture, and component hierarchy
  - Hexagonal architecture (ports & adapters pattern)
  - Engine/UI separation and data flow patterns
  - Decoupled repository pattern and event-driven observer
  - Folder structure and dependency injection

### Product Specification
- **[PRD.md](docs/PRD.md)** — Complete product requirements and game mechanics
  - Game mechanics: turn resolution, combat system, 5-hexagon rule
  - UI/UX design philosophy (radical minimalism with Kenney assets)
  - Hexagonal coordinate system and board layout
  - Acceptance criteria and data structures

### Requirements & Dependencies
- **[REQUIREMENTS.md](docs/REQUIREMENTS.md)** — Dependencies, versions, and installation
  - Runtime libraries (Python, Flet, Loguru)
  - Development & testing tools (pytest, Black, Ruff, pyright)
  - Package management with `uv`
  - Asset packs and environment setup

## Automatic Claude Code Skills

Skills are automatically invoked by Claude when relevant. Use them with `/skill-name` or trigger them with context keywords.

### Available Skills

| Skill | Trigger Keywords | Purpose |
|-------|-----------------|---------|
| **code-standards-review** | review, SOLID, refactor, implement | Review code against mandatory standards |
| **hex-grid-math** | pathfinding, hex grid, coordinates, distance | Hex coordinate operations and algorithms |
| **hexagonal-grid-ui-ux** | UI, UX, minimalismo, design, buttons, layout | Build UI with minimalist design + Kenney assets |
| **hex-grid-rendering** | rendering, canvas, pixel-perfect, transform | Mathematical precision for grid rendering |
| **testing-framework** | test, pytest, coverage, unit test | Write and run tests with pytest |
| **dev-environment** | setup, environment, dependencies, troubleshoot | Configure development environment |
| **board-implementation** | board logic, tile system, grid operations | Implement board systems with architecture |

### Invoking Skills Manually

```bash
# List available skills
What Skills are available?

# Use skill directly
/code-standards-review
/hex-grid-math
/hexagonal-grid-ui-ux
/hex-grid-rendering
/testing-framework
/dev-environment
/board-implementation

# Or trigger via context
"review this code against SyV-Flet standards"
"implement minimalist UI with Kenney assets"
"render hex grid with pixel-perfect precision"
"write tests for the board"
```

## Automatic Hooks

Hooks run automatically before/after Claude tools to enforce standards and prevent errors.

### Enabled Hooks

- **Post-Write/Edit:** Auto-format Python files with Black + Ruff
- **Pre-Write/Edit:** Protect critical files (.git/, pyproject.toml, .env, etc.)
- **Pre-Bash:** Validate commands (warn against pip, dangerous commands, etc.)
- **Session Start:** Load this README automatically

### Hook Configuration

All hooks are configured in `settings.json`. Scripts are in `hooks/`:
- `format-file.py` — Auto-format Python code
- `protect-files.py` — Protect critical files
- `validate-command.py` — Validate bash commands

Hooks run silently. Warnings appear on stderr only if issues detected.

## Key Principles

### Naming Convention
- **Technical context:** `syv-flet` (lowercase, hyphens) → file paths, modules, commands
- **Semantic context:** `SyV-Flet` (title case) → documentation, titles, descriptions

### Project Structure
```
syv-flet/
├── src/syv-flet/
│   ├── engine/           ← Pure game logic (Flet-agnostic)
│   └── ui/               ← Flet interface layer
├── tests/                ← Unit tests
├── assets/               ← Images, fonts, etc.
└── .claude/docs/         ← This documentation
```

### Stack
- **Language:** Python 3.12+ (3.13+ recommended)
- **UI Framework:** Flet (v0.24.0+)
- **Package Manager:** `uv` (NOT pip)
- **Testing:** pytest + pytest-cov
- **Formatting:** Black
- **Linting:** Ruff

## How Claude Code Uses These Skills

These documents are automatically consulted when:
1. Writing or reviewing Python code
2. Designing architecture or refactoring
3. Setting up development environment
4. Implementing new features

## Navigation

All skills are cross-referenced:
- Architecture → links to Development Guide for setup
- Development Guide → references Code Standards for quality checks
- Code Standards → includes architectural patterns from Architecture doc
- Hexagonal Grid → mathematical foundation for board implementation

---

**Language:** 100% English  
**Last Updated:** January 16, 2026  
**Project Name:** SyV-Flet (Subordinación y Valor - Flet Framework)
