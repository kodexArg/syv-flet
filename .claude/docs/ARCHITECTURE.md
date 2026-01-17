# ARCHITECTURE.md

**SyV-Flet - System Architecture**

Complemento al [PRD.md](./PRD.md). Define la estructura de carpetas, separación de capas, y decisiones de diseño.

---

## Design Principles

1. **Hexagonal Architecture (Ports & Adapters)**
   - Engine logic completely independent of Flet UI
   - Dependencies flow inward (UI → Controllers → Engine)

2. **Decoupled Repository Pattern**
   - Unit data lives in `UnitRepository` (not in Hexagons)
   - Repository abstraction allows future database/multiplayer without changing engine
   - Single source of truth for all unit state

3. **Event-Driven Observer Pattern**
   - Engine emits events; UI subscribes
   - No back-references: UI never pulls state from engine
   - Enables multiplayer: events serialize to JSON for network

4. **Minimal Configuration**
   - All hardcoded values live in `configs.yaml`
   - Zero magic numbers in source code
   - Single file for all tunable parameters

---

## Folder Structure (Minimal & Maximal)

```
syv-flet/
├── src/syv-flet/
│   ├── __init__.py
│   ├── main.py                      ← Entry point (Flet app)
│   │
│   ├── engine/                      ← Game logic (UI-agnostic)
│   │   ├── __init__.py
│   │   ├── board.py                 ← HexagonGrid (Q,R coords)
│   │   ├── unit.py                  ← Unit data model
│   │   ├── repository.py            ← UnitRepository (Protocol + InMemory)
│   │   ├── game_controller.py       ← FSM (PLANNING/EXECUTION/RESET phases)
│   │   ├── order.py                 ← Order types & resolution logic
│   │   ├── combat.py                ← Combat resolution (deterministic)
│   │   └── events.py                ← EventBus (centralized event dispatch)
│   │
│   ├── ui/                          ← Flet-specific (replaceable)
│   │   ├── __init__.py
│   │   ├── app.py                   ← Flet app root + routing
│   │   │
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── menu_screen.py       ← Main menu (Start Game button)
│   │   │   └── game_screen.py       ← Game view (grid + buttons)
│   │   │
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── hex_grid.py          ← Canvas rendering + click detection
│   │   │   ├── order_overlay.py     ← Order icons & highlights
│   │   │   └── button_bar.py        ← "Cambiar Jugador" button
│   │   │
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── game_ui_controller.py ← Bridges UI ↔ Engine (listens to EventBus)
│   │   │
│   │   └── styles/
│   │       ├── __init__.py
│   │       └── colors.py            ← Faction colors, opacity values
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py         ← Reads configs.yaml
│       └── logger.py                ← Debug logging
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  ← Shared fixtures (board_empty, player_with_units, etc.)
│   ├── test_board.py                ← Board generation, hex validity
│   ├── test_units.py                ← Unit creation, movement, status
│   ├── test_orders.py               ← Order placement & cycling
│   ├── test_combat.py               ← Combat resolution logic
│   ├── test_game_phases.py          ← PLANNING → EXECUTION → RESET flow
│   └── test_events.py               ← EventBus subscriptions
│
├── assets/
│   ├── hexagons/Previews/           ← Kenney terrain tiles (64×64px)
│   │   ├── grass.png                ← Default
│   │   ├── water.png                ← Impassable
│   │   └── ...
│   ├── icons/PNG/
│   │   ├── Default (64px)/          ← Unit markers
│   │   └── Double (128px)/          ← Scaled variants
│   └── fonts/kenney_kenney-fonts/   ← UI typography
│
├── configs.yaml                     ← ALL hardcoded values (see skill)
├── pyproject.toml                   ← uv project manifest
├── uv.lock                          ← Locked dependencies
├── PRD.md                           ← Product spec
├── REQUIREMENTS.md                  ← This dependencies list
├── ARCHITECTURE.md                  ← This file
└── .gitignore
```

---

## Core Layers & Data Flow

### Layer 1: Engine (Agnostic to UI)

**Board (`engine/board.py`)**
- Axial coordinates `(q, r)` only
- Queries: `is_valid(q, r)`, `neighbors(q, r)`, `distance(a, b)`
- No Flet imports

**Units & Repository (`engine/unit.py`, `engine/repository.py`)**
```
Protocol UnitRepository:
  ├─ get(uid) → Unit
  ├─ create(unit) → None
  ├─ move(uid, q, r) → None
  ├─ update_status(uid, status) → None
  └─ subscribe(listener) → None

Concrete: InMemoryUnitRepository (MVP)
```

**Game Controller (`engine/game_controller.py`)**
```
FSM Phases:
  PLANNING    → Player places orders (tap cycling)
  EXECUTION   → Orders resolve simultaneously
  RESET       → Cleanup (5-hex rule, dead units)
  └─→ back to PLANNING

Responsibilities:
  - Manage current_phase
  - Route hex clicks to tap cycling state machine
  - Trigger order resolution
  - Emit events on state changes
```

**Events (`engine/events.py`)**
```
EventBus (centralized):
  - emit(event_type, **data)
  - subscribe(event_type, listener)
  - event_log (for debugging/replay)

Event Types:
  "hex_state_changed" {q, r, old_state, new_state}
  "unit_moved" {uid, from_hex, to_hex}
  "order_placed" {q, r, order_type, owner_id}
  "phase_transitioned" {old_phase, new_phase}
  "turn_complete" {}
```

---

### Layer 2: UI Bridge (Flet-Specific)

**Game UI Controller (`ui/controllers/game_ui_controller.py`)**
```
Purpose: Bridge between engine events and Flet widgets
Pattern: Event subscriber (NOT event emitter)

Listens to:
  - "order_placed" → update hex grid visuals
  - "phase_transitioned" → fade in/out orders
  - "unit_moved" → animate unit position

Responsibilities:
  - Subscribe to engine EventBus
  - Translate events → Flet component updates
  - Handle user clicks → call engine methods
  - Manage UI state (selection, hover, opacity)
```

**Screen Components**
- Menu: Static, just "Start Game" button
- Game: Grid + buttons, responsive layout
- Hex Grid: Canvas rendering + click→hex conversion
- Order Overlay: Icons, labels, outlines on hexes

---

### Layer 3: Dependency Injection (Startup)

**`main.py` orchestration:**
```
1. Load configs from configs.yaml
2. Create engine components:
   - board = HexagonGrid(radius=configs.board_radius)
   - unit_repo = InMemoryUnitRepository()  (or DatabaseRepository for multiplayer)
   - event_bus = EventBus()
   - game_ctrl = GameController(board, unit_repo, event_bus)

3. Create UI components:
   - ui_ctrl = GameUIController(event_bus, game_ctrl)
   - game_screen = GameScreen(ui_ctrl)
   - app = FletApp([menu_screen, game_screen])

4. Start Flet: app.run()
```

---

## Key Architectural Decisions

### 1. Unit Repository Decoupling

**Why:** Future multiplayer backend
- Swap `InMemoryUnitRepository` ↔ `DatabaseRepository` at startup
- Engine code unchanged
- UI code unchanged
- Only main.py DI logic changes

**Example migration path:**
```
MVP:  InMemoryUnitRepository (all units in RAM)
      ↓
MP:   DatabaseUnitRepository (PostgreSQL, one source of truth)
      ↓
Network: EventBus events serialized → WebSocket → other clients
```

### 2. EventBus (Not Callbacks)

**Why:** Scalable, debuggable, multiplayer-ready
- Single event_log for replay/debug
- No scattered callbacks
- Easy to add new listeners (UI, analytics, network)
- Events serialize to JSON trivially

**Example:**
```
Engine: event_bus.emit("unit_moved", uid="u1", from_hex=(5,3), to_hex=(6,3))
  ↓
EventLog: [{event_type: "unit_moved", timestamp: ..., data: {...}}]
  ↓
UI Controller: receives event → updates grid visuals
  ↓
Network (future): serialize event → broadcast to other clients
```

### 3. Configs in YAML

**Why:** Human-readable, no magic numbers in code
- Single source for R, hex_size, max_move_distance, 5-hex-rule distance
- Tweakable without code rebuild
- Easy to version-control (git diff is readable)

---

## State Machine (Tap Cycling) — Where Does It Live?

The **tap cycling logic** (origin hex selected → adjacent orders → cycles) is **NOT in GameController**.

**Proposed location: `engine/tap_cycle.py` (stateless)**
```
Pure function: tap_cycle_handler(state, hex_coords, board) → new_state

Input:
  - Current tap cycle state (which hex is origin, which order is selected)
  - Hex clicked
  - Board reference (to validate neighbors)

Output:
  - New tap cycle state
  - Orders to place (if any)
  - Events to emit (hex_state_changed, order_placed)

GameController calls this on each hex click, updates its internal tap_state,
emits resulting events.
```

See `cycle-tap-mechanism` skill for pseudocode details.

---

## Testing Strategy (Aligned with BDD)

**Test files mirror engine modules:**
```
engine/board.py           → tests/test_board.py
engine/unit.py            → tests/test_units.py
engine/order.py + combat  → tests/test_combat.py
engine/game_controller.py → tests/test_game_phases.py
engine/events.py          → tests/test_events.py
```

**No UI tests initially** (UI is visual; screenshot tests are fragile).

---

## Configuration: Hardcoded Values

**All in `configs.yaml`. See [configuration-management skill](../skills/configuration-management/SKILL.md) for details.**

Examples:
```yaml
board:
  radius: 20                    # Board size formula: 3*R*(R+1) + 1
  hex_size_desktop: 64          # pixels
  hex_size_mobile: 40

rules:
  max_move_distance: 3
  max_support_distance: 5       # 5-hex rule
  tie_behavior: "static"        # Combat tie result: units remain static

ui:
  faction_colors:
    player_1: "#2196F3"         # Blue
    player_2: "#F44336"         # Red
  opacity:
    planning_phase: 0.4
    execution_phase: 1.0
```

---

## Scalability Notes

1. **Large Boards (R > 20):**
   - Implement viewport culling in hex_grid.py (only render visible hexes)
   - Cache pixel positions for all hexes (1,261 pre-calculated)

2. **Many Units (>500):**
   - Repository already abstracts storage; swap to database
   - Filter queries (units_by_player, units_by_status) become SQL queries

3. **Network Multiplayer:**
   - EventBus events → JSON serialization
   - Send events over WebSocket
   - Remote client replays events locally

---

## Files Checklist (MVP Critical Path)

- [x] `engine/board.py` — Board queries
- [x] `engine/unit.py` + `repository.py` — Unit storage
- [x] `engine/game_controller.py` — Phase FSM
- [x] `engine/order.py` — Order types & validation
- [x] `engine/combat.py` — Combat resolution
- [ ] `engine/events.py` — EventBus
- [ ] `engine/tap_cycle.py` — Tap cycling logic (stateless)
- [ ] `ui/screens/game_screen.py` — Main game view
- [ ] `ui/components/hex_grid.py` — Canvas + click detection
- [ ] `ui/controllers/game_ui_controller.py` — Event bridge
- [ ] `configs.yaml` — All hardcoded values
- [ ] `tests/` — Full BDD test coverage

---

## Related Documentation

- [PRD.md](./PRD.md) — Complete product spec
- [REQUIREMENTS.md](./REQUIREMENTS.md) — Dependencies
- [hex-grid-math skill](../skills/hex-grid-math/SKILL.md) — Coordinate math
- [state-machine skill](../skills/state-machine/SKILL.md) — FSM design
- [cycle-tap-mechanism skill](../skills/cycle-tap-mechanism/SKILL.md) — Tap logic
- [code-standards skill](../skills/code-standards/SKILL.md) — SOLID principles
