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

### Core Skills (Updated for Hot-Seat Privacy)

| Skill | Purpose | Key Topics |
|-------|---------|-----------|
| **state-machine** | Game FSM with `ScreenState` (privacy gate) | GamePhase + ScreenState, hotseat privacy model |
| **hex-grid-math** | Hexagonal coordinate operations | Pathfinding, distance, adjacency, flat-top orientation |
| **hex-grid-flet-rendering** | Canvas rendering with privacy filtering | Player-filtered unit/order visibility, PLANNING vs EXECUTION |
| **ux-ui-flet-rendering** | Radical minimalism + PhaseTransitionScreen | Two-screen model, reusable PhaseButton, responsive design |
| **cycle-tap-mechanism** | Order validation and tap cycling | Hidden vs visible orders, state transitions |
| **code-standards** | SOLID principles, clean architecture | Type hints, zero magic numbers, hexagonal pattern |
| **testing-framework** | BDD testing with pytest | Fixtures, coverage, hotseat privacy tests |
| **configuration-management** | `configs.yaml` centralization | Overlay opacity, button colors, hex sizes |
| **dev-environment** | Setup and `uv` workflow | Dependencies, environment configuration |
| **assets-manager** | Kenney asset strategy | Hexagon tiles, board icons, fonts, caching |
| **git-workflow** | Conventional commits | Commit standards, branching strategy |
| **logging** | Loguru centralization | Debug/error logs, rotation policy |
| **fix-gaps** | Recursive gap resolution | Checklist management, feedback tracking, systematic fixes |
| **user-authentication** | MVP status: NOT IMPLEMENTED | Hot-seat only, no auth needed for v1 |

### Using Skills

Skills are triggered automatically when relevant, but can also be invoked manually:

```bash
# Manual invocation examples:
/state-machine        # FSM design with privacy gates
/hex-grid-flet-rendering  # Canvas privacy filtering
/ux-ui-flet-rendering     # Two-screen model & PhaseButton
/testing-framework    # BDD tests for hotseat privacy
/code-standards       # Code review against SOLID
```

Or trigger via context:
```
"design the privacy model for hotseat mode"
"implement the Phase Transition Screen"
"write tests for player switching"
"render the hex grid with privacy filtering"
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
**Last Updated:** January 18, 2026
**Project Name:** SyV-Flet (Subordinación y Valor - Flet Framework)
