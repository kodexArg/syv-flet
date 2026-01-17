# REQUIREMENTS.md

**SyV-Flet - Dependencias y Versiones**

Complemento al [PRD.md](./PRD.md). Lista las librerías necesarias y sus versiones mínimas.

---

## Core Runtime

| Library | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.12+ | Runtime (3.13 recommended) |
| **Flet** | 0.24+ | UI framework (canvas, gestures, responsiveness) |
| **Loguru** | 0.7.0+ | Centralized logging (file rotation + color output) |
| **Pydantic** | 2.0+ | Data validation (unit/hex models, config validation) |

---

## Development & Testing

| Library | Version | Purpose |
|---------|---------|---------|
| **pytest** | 7.0+ | Test runner (BDD + fixtures) |
| **black** | 23.0+ | Code formatter (PEP 8 compliance) |
| **ruff** | 0.1.0+ | Linter + import sorter |
| **pyright** | 1.1.0+ | Static type checker |

---

## Package Management

| Tool | Version | Purpose |
|------|---------|---------|
| **uv** | 0.1.0+ | Dependency resolver (replaces pip) |

---

## Configuration Management

**Single Source of Truth:** `configs.yaml` at project root

All tunable parameters (board size, movement distance, UI colors, FPS targets) live in a centralized YAML file, loaded at startup via `src/syv_flet/utils/config_loader.py`.

**Key Principle:** Zero magic numbers in source code. All constants → `configs.yaml`.

See [configuration-management skill](../skills/configuration-management/SKILL.md) for structure and usage patterns.

---

## Optional / Future

| Library | Version | Purpose |
|---------|---------|---------|
| **python-dotenv** | 1.0+ | Load `.env` configuration (environment-specific overrides) |
| **pytest-cov** | 4.0+ | Coverage reporting |

---

## Asset Dependencies

| Asset Pack | Source | Purpose |
|-----------|--------|---------|
| **Hexagon Kit** | kenney.nl | 64×64px terrain tiles (grass, water, sand, etc.) |
| **Board Game Icons** | kenney.nl | 64×128px unit/order markers |
| **Kenney Fonts** | kenney.nl | UI typography (open-source TTF/OTF) |

All assets are **CC0 (public domain)** — no licensing restrictions.

---

## Environment

- **OS:** Linux / macOS / WSL2
- **Python Path:** Managed by `uv` (project-local venv)
- **Package Lock:** `uv.lock` (deterministic reproducibility)

---

## Installation

```bash
cd /home/kodex/Dev/syv-flet
uv sync          # Install all dependencies from lock
uv run pytest    # Run tests
uv run python -m syv_flet.main  # Run app
```

See [dev-environment skill](../skills/dev-environment/SKILL.md) for detailed setup.
