---
name: configuration-management
description: Centralized configuration strategy. All hardcoded values live in configs.yaml. YAML is the single source of truth. Zero magic numbers in Python source code.
allowed-tools: Read, Edit
---

# Configuration Management

This skill defines how SyV-Flet stores and loads all tunable parameters.

## Core Principle

**NEVER hardcode values in Python source.**

All constants—board radius, hex size, movement distance, opacity values, colors—live in **`configs.yaml`** at project root.

---

## The Single File: `configs.yaml`

Located: `/home/kodex/Dev/syv-flet/configs.yaml`

### Structure and Example

See [example-config.yaml](./example-config.yaml) in this directory for a complete reference of the keys and structure.

---

## Loading Configuration

### Method: `config_loader.py`

**Responsibility:**
- Load the YAML file at startup.
- Validate that all required keys exist (fail early if config is broken).
- Return the configuration as a dictionary or a structured object.

**Pseudocode Logic:**
1. Open and read `configs.yaml`.
2. Parse YAML content safely.
3. Check for essential keys (e.g., `board`, `rules`).
4. Return the data structure.

---

## Usage Pattern

### Correct Approach
Import the loader anywhere you need configuration. Assign loaded values to local variables or class attributes during initialization.

### Avoid
Do NOT define constants directly in classes (e.g., `RADIUS = 20`) or usage of "magic numbers" in logic. Code should be agnostic of the specific values.

---

## Where Values Live

| Type | Location | Why |
|------|----------|-----|
| Game rules (board size, movement distance) | `configs.yaml` | Affects gameplay balance |
| UI styling (colors, sizes, opacity) | `configs.yaml` | Affects visual design |
| API endpoints (future multiplayer) | `configs.yaml` | Environment-specific |
| Hardcoded text (labels, strings) | Python source (or i18n file) | Not tunable at runtime |
| Python dependencies & versions | `pyproject.toml` | Managed by `uv` |

---

## Workflow: Adding a New Configuration

1. **Add to `configs.yaml`**: Define your new parameter and value in the YAML file.
2. **Load in Application**: Retrieve the value using your config loader.
3. **Use Variable**: Pass the value to where it is needed.

---

## Environment-Specific Configs (Future)

For deployment environments (dev/staging/production), the strategy is to:
- Use environment variables to select the target config file (e.g., `configs.prod.yaml`).
- Or load base config and override specific keys with environment variables.

For MVP, use a single `configs.yaml`.

---

## Validation

It is highly recommended to validate the configuration structure at load time (e.g., ensuring radii are positive integers, colors are hex strings) to prevent runtime errors.

---

## Version Control

- ✓ **Commit `configs.yaml`** (it serves as the schema and default values).
- ✗ **Never commit `.env`** (contains sensitive data/secrets).

---

## Checklist

- [ ] All numeric constants in `configs.yaml`.
- [ ] Config loader handles YAML parsing errors gracefully.
- [ ] No magic numbers remain in source code.

---

## See Also

- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — Where configs fit in design
- [dev-environment skill](../dev-environment/SKILL.md) — Setup instructions
