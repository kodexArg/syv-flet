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

### Structure

```yaml
# Game Rules
board:
  radius: 20                          # Board size: 3*R*(R+1) + 1 = 1,261 hexes

rules:
  movement:
    max_move_distance: 3              # Max hexes a unit can move per order
    max_support_distance: 5           # "Five-Hex Rule" — max distance to officer

  combat:
    tie_behavior: "static"            # Combat tie result: units remain static

# UI/UX
ui:
  # Responsive hex sizes (pixels)
  hex_sizes:
    desktop_1920: 64
    desktop_1280: 56
    tablet: 48
    mobile: 40

  # Faction team colors
  faction_colors:
    player_1: "#2196F3"               # Blue
    player_2: "#F44336"               # Red
    neutral: "#CCCCCC"                # Gray

  # Phase visibility (opacity 0.0-1.0)
  phase_opacity:
    planning: 0.4                     # Orders faint during planning
    execution: 1.0                    # Orders fully visible during execution

  # Button styling
  buttons:
    start_game_color: "#4CAF50"       # Green
    cambiar_jugador_color: "#FF9800"  # Orange
    border_radius: 50                 # Rounded (gomoso)

# Assets
assets:
  hexagons_path: "assets/hexagons/Previews/"
  icons_path: "assets/icons/PNG/"
  fonts_path: "assets/fonts/kenney_kenney-fonts/"

# Display/Performance
display:
  target_fps_desktop: 60
  target_fps_mobile: 30
  canvas_update_threshold_ms: 16      # Refresh every 16ms (60 FPS)
```

---

## Loading Configuration

### Method: `config_loader.py`

```python
# Location: src/syv_flet/utils/config_loader.py

Module responsibility:
  - Load YAML at startup
  - Validate required keys
  - Return as dict or TypedDict

Example pseudocode:

  load_config(path="configs.yaml"):
    Read YAML file
    Parse into Python dict
    Validate all required keys exist
    Return config dict

  get_value(config, path):
    Example: get_value(config, "board.radius") → 20
    Split path by "."
    Navigate nested dict
    Return value or error if missing
```

---

## Usage Pattern in Code

### ✓ Correct

```python
# In engine/board.py
from utils.config_loader import load_config

config = load_config()
BOARD_RADIUS = config["board"]["radius"]

class HexagonGrid:
    def __init__(self):
        self.radius = BOARD_RADIUS
```

### ✗ Wrong

```python
# NEVER do this
class HexagonGrid:
    RADIUS = 20  # ← Magic number! WRONG
```

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

1. **Add to `configs.yaml`:**
   ```yaml
   my_new_feature:
     param_name: value
   ```

2. **Load in Python:**
   ```python
   config = load_config()
   param_value = config["my_new_feature"]["param_name"]
   ```

3. **Never hardcode** the param in source code.

---

## Environment-Specific Configs (Future)

For deployment environments (dev/staging/production):

```bash
# Option 1: Multiple YAML files
configs.dev.yaml
configs.prod.yaml

# Option 2: Load + override from .env
CONFIGS_FILE=configs.prod.yaml

# Load in code:
config_file = os.getenv("CONFIGS_FILE", "configs.yaml")
config = load_config(config_file)
```

For MVP, use single `configs.yaml`.

---

## Validation

Optional: Use Pydantic to validate config structure at load time.

```python
from pydantic import BaseModel

class BoardConfig(BaseModel):
    radius: int
    # Pydantic validates: radius is integer, in valid range, etc.

config_obj = BoardConfig(**config["board"])
```

---

## Version Control

- ✓ **Commit `configs.yaml`** (it's a schema file, not secrets)
- ✗ **Never commit `.env`** (contains sensitive data)

---

## Checklist

- [ ] All numeric constants in `configs.yaml` (not .py files)
- [ ] `config_loader.py` handles YAML parsing
- [ ] At least one test loads config successfully
- [ ] Documentation explains how to override values
- [ ] No magic numbers remain in source code

---

## See Also

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — Where configs fit in design
- [dev-environment skill](../dev-environment/SKILL.md) — Setup instructions
