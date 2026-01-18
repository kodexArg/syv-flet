# ARCHITECTURE.md

**SyV-Flet - System Architecture**

Complemento al [PRD.md](./PRD.md). Define la estructura de carpetas, separación de capas, y decisiones de diseño para el MVP local.

---

## Design Principles

1. **Hexagonal Architecture (Engine/UI Separation)**
   - Game logic (engine) completamente independiente de Flet
   - La UI es reemplazable sin tocar el motor
   - Dependencias fluyen hacia adentro: UI → Engine

2. **Hash Maps**
   - Estado del juego vive en tres Hash Maps: `map`, `units`, `orders`
   - GameState es el contenedor central
   - Acceso directo O(1) para mantener 60 FPS

3. **Minimal Configuration**
   - Todos los valores hardcodeados viven en `configs.yaml`
   - Cero magic numbers en código fuente
   - Un solo archivo para todos los parámetros ajustables

4. **Arquitectura Evolucionable**
   - El diseño permite migración futura a servidor cloud sin refactoring mayor
   - Motor agnóstico al origen de datos (local MVP → API remota v2.0)

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
│   │   ├── game_state.py            ← GameState (Hash Maps: map, units, orders)
│   │   ├── board.py                 ← Hexagon grid operations (Q,R coords)
│   │   ├── game_controller.py       ← FSM (PLANNING/EXECUTION/RESET phases)
│   │   ├── tap_cycle.py             ← Tap cycling validation (stateless)
│   │   ├── order.py                 ← Order types & validation
│   │   └── combat.py                ← Combat resolution (deterministic)
│   │
│   ├── ui/                          ← Flet-specific (replaceable)
│   │   ├── __init__.py
│   │   ├── app.py                   ← Flet app root + routing
│   │   │
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── phase_transition_screen.py ← PRIVATE gate + phase announcer (NEW)
│   │   │   └── game_screen.py       ← Game view (grid + buttons, privacy filtered)
│   │   │
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── hex_grid.py          ← Canvas rendering + click detection (player-filtered)
│   │   │   ├── order_overlay.py     ← Order icons & highlights (privacy-aware)
│   │   │   └── phase_button.py      ← Reusable button (Iniciar/Siguiente/Nuevo)
│   │   │
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── game_ui_controller.py ← Bridges UI ↔ Engine (lee GameState)
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

**GameState (`engine/game_state.py`)**
```python
class GameState(BaseModel):
    # Core game state
    map: Dict[Tuple[int, int], HexData]
    units: Dict[str, UnitData]
    orders: Dict[str, OrderData]

    # Phase & screen management
    current_phase: GamePhase           # PLANNING, EXECUTION, RESET
    screen_state: ScreenState          # PHASE_TRANSITION, GAMEPLAY
    active_player: int                 # 0 or 1 (whose turn?)
    turn_number: int
    phase_transition_text: str         # Dynamic button text

    # UI state (ephemeral)
    selected_hex: Optional[Tuple[int, int]]
    order_path: List[Tuple[int, int]]

    # Counters
    next_unit_id: int
    next_order_id: int
    order_history: deque(maxlen=500)
```

**ScreenState values:**
- `PHASE_TRANSITION`: Show dark overlay with centered button (privacy gate)
- `GAMEPLAY`: Show Game Screen with grid (order placement or execution)

**Board (`engine/board.py`)**
```
Operaciones sobre coordenadas hexagonales:
  - is_valid(q, r) → bool
  - neighbors(q, r) → list[(q, r)]
  - distance(a, b) → int
  - get_unit_at(q, r) → unit_id | None

Inicializa el Hash Map map con terrenos
```

**GameController (`engine/game_controller.py`)**
```
FSM Phases:
  PLANNING    → Jugadores colocan órdenes
  EXECUTION   → Resolver movimientos y combates
  RESET       → Limpieza (Regla 5 Hexágonos), cambio de jugador
  └─→ back to PLANNING

Responsabilidades:
  - Gestionar current_phase en GameState
  - Validar órdenes mediante tap_cycle
  - Ejecutar resolución de turno
  - Actualizar Hash Maps
```

**Tap Cycle (`engine/tap_cycle.py`)**
```
Validador stateless de órdenes:
  - validate_tap(hex, current_selection, board) → valid/invalid
  - suggest_order(from_hex, to_hex) → OrderType | None

GameController lo usa para validar inputs antes de persistir
```

---

### Layer 2: UI Bridge (Flet-Specific)

**Game UI Controller (`ui/controllers/game_ui_controller.py`)**
```
Propósito: Puente entre GameState y componentes Flet

Responsabilidades:
  - Leer GameState para renderizar UI
  - Capturar clicks del usuario → enviar a GameController
  - Actualizar componentes visuales tras cada fase
  - Gestionar estado local de UI (selección, hover, opacidad)

Flujo:
  Usuario click → UI Controller → GameController.handle_tap()
  GameController actualiza GameState
  UI Controller lee GameState → actualiza canvas
```

**Screen Components**
- **PhaseTransitionScreen:** Dark overlay (0.95 opacity) + centered reusable button
  - Shows when `screen_state == PHASE_TRANSITION`
  - Dynamic button text: "Iniciar Partida", "Siguiente Jugador", "Nuevo Turno"
  - **Critical for privacy:** Prevents seeing opponent's orders
  - Appears: game start, between PLANNING turns, after RESET

- **GameScreen:** Grid + buttons, layout responsivo
  - Shows when `screen_state == GAMEPLAY`
  - In PLANNING: filters rendering based on `active_player` (privacy visual layer)
  - In EXECUTION: all units/orders visible (simultaneous resolution)

- **HexGrid:** Canvas rendering + conversión click→hex
  - **Privacy-aware:** Only renders units/orders matching active_player during PLANNING
  - Terrain (grass/water) always visible
  - Input handling respects `active_player` restriction

- **OrderOverlay:** Iconos y outlines sobre hexágonos
  - Privacy-aware: Only shows icons for active player during PLANNING

- **PhaseButton:** Reusable button component
  - Takes text prop: button label (dynamic per screen state)
  - Consistent styling: pill-shaped, cushioned shadow

---

### Layer 3: Dependency Injection (Startup)

**`main.py` orchestration:**
```
1. Cargar configuración desde configs.yaml

2. Crear componentes del engine:
   - game_state = GameState(
       board_radius=configs.board_radius,
       max_order_history=configs.max_order_history
     )
   - game_ctrl = GameController(game_state)

3. Crear componentes de UI:
   - ui_ctrl = GameUIController(game_ctrl, game_state)
   - game_screen = GameScreen(ui_ctrl)
   - app = FletApp([menu_screen, game_screen])

4. Iniciar Flet: app.run()
```

---

## Key Architectural Decisions

### 1. Hash Maps como Estructura Central

**Decisión:** Estado del juego en tres Hash Maps directos (map, units, orders)

**Razón:**
- Acceso O(1) crítico para 60 FPS
- Simplicidad
- Perfilado fácil de memory usage

### 2. Pydantic para Estructuras de Datos

**Decisión:** Todos los modelos de datos usan Pydantic BaseModel

**Razón:**
- Validación automática
- Type hints nativos
- Serialización JSON directa

### 3. Configs en YAML

**Decisión:** Todos los valores hardcodeados en `configs.yaml`

**Razón:**
- Único archivo para parámetros ajustables
- Sin magic numbers en código
- Fácil version control (git diff legible)
- Tweakable sin rebuild

**Ejemplos:** board_radius, hex_size, max_order_history, faction_colors

---

## State Machine (FSM y Tap Cycling)

### Game FSM (PLANNING[P1-PRIVATE] → PLANNING[P2-PRIVATE] → EXECUTION[SHARED] → RESET)

**Ubicación:** `GameState.current_phase` (game phase) + `GameState.screen_state` (UI display)

**Transiciones Completas (incluyendo screen_state):**
```
GAME START:
  screen_state = PHASE_TRANSITION, phase_transition_text = "Iniciar Partida"
  ↓ button click
  current_phase = PLANNING, active_player = 0
  screen_state = GAMEPLAY
  ↓ P1 clicks "Siguiente Jugador"
  screen_state = PHASE_TRANSITION, phase_transition_text = "Siguiente Jugador"
  ↓ button click
  current_phase = PLANNING, active_player = 1
  screen_state = GAMEPLAY
  ↓ P2 clicks "Siguiente Jugador"
  screen_state = PHASE_TRANSITION (both done?)
  ↓ auto-transition or button click
  current_phase = EXECUTION
  screen_state = GAMEPLAY
  ↓ execution completes
  current_phase = RESET (cleanup silent)
  ↓ cleanup done
  screen_state = PHASE_TRANSITION, phase_transition_text = "Nuevo Turno"
  ↓ button click
  current_phase = PLANNING, active_player = 0
  screen_state = GAMEPLAY
  [repeat]
```

**GameController maneja:**
- Validación de órdenes (tap_cycle)
- Ejecución de combate (combat resolution)
- Limpieza post-turno (Regla 5 Hexágonos)
- **NO maneja transiciones UI** — eso es responsabilidad de GameUIController

### Tap Cycling Logic

**Ubicación:** `engine/tap_cycle.py` (funciones stateless)

**Función:** Validar secuencias de taps del usuario
```
validate_tap(hex_clicked, current_selection, board) → valid/invalid
suggest_order(from_hex, to_hex) → OrderType | None
```

**GameController** llama estas funciones antes de persistir órdenes en `GameState.orders`.

Ver `cycle-tap-mechanism` skill para detalles completos.

---

## Testing Strategy (Aligned with BDD)

**Test files mirror engine modules:**
```
engine/game_state.py      → tests/test_game_state.py
engine/board.py           → tests/test_board.py
engine/order.py + combat  → tests/test_combat.py
engine/game_controller.py → tests/test_game_phases.py
engine/tap_cycle.py       → tests/test_tap_cycle.py
```

**No UI tests initially** (UI es visual; screenshot tests son frágiles).

---

## Configuration: Hardcoded Values

**Todo en `configs.yaml`. Ver [configuration-management skill](../skills/configuration-management/SKILL.md) para detalles.**

Ejemplos:
```yaml
game_state:
  board_radius: 20              # Tamaño tablero: 3*R*(R+1) + 1 = 1,261 hexs
  max_order_history: 500        # Máx órdenes en historial FIFO

board:
  hex_size_desktop: 64          # pixels
  hex_size_mobile: 40

rules:
  max_support_distance: 5       # Regla de los 5 Hexágonos
  tie_behavior: "static"        # Empate de combate: unidades estáticas

ui:
  faction_colors:
    player_1: "#2196F3"         # Azul
    player_2: "#F44336"         # Rojo
  opacity:
    planning_phase: 0.4
    execution_phase: 1.0
```

---

## Files Checklist (MVP Critical Path)

**Engine (Game Logic):**
- [ ] `engine/game_state.py` — GameState con Hash Maps
- [ ] `engine/board.py` — Operaciones hexagonales
- [ ] `engine/game_controller.py` — FSM (PLANNING/EXECUTION/RESET)
- [ ] `engine/tap_cycle.py` — Validación de taps (stateless)
- [ ] `engine/order.py` — Tipos de órdenes y validación
- [ ] `engine/combat.py` — Resolución de combate determinista

**UI (Flet Interface):**
- [ ] `ui/screens/phase_transition_screen.py` — **NEW** Dark overlay + button (privacy gate)
- [ ] `ui/screens/game_screen.py` — Vista principal del juego (privacy-filtered rendering)
- [ ] `ui/components/phase_button.py` — **NEW** Reusable button (Iniciar/Siguiente/Nuevo)
- [ ] `ui/components/hex_grid.py` — Renderizado canvas + detección de clicks (player-filtered)
- [ ] `ui/components/order_overlay.py` — Iconos de órdenes sobre hexágonos (privacy-aware)
- [ ] `ui/controllers/game_ui_controller.py` — Puente UI ↔ Engine (maneja screen_state)

**Configuration & Tests:**
- [ ] `configs.yaml` — Todos los valores hardcodeados
- [ ] `tests/test_game_state.py` — Tests de GameState + FIFO
- [ ] `tests/test_board.py` — Tests de grid hexagonal
- [ ] `tests/test_game_controller.py` — Tests de FSM
- [ ] `tests/test_combat.py` — Tests de resolución de combate

---

## Related Documentation

- [PRD.md](./PRD.md) — Complete product spec
- [REQUIREMENTS.md](./REQUIREMENTS.md) — Dependencies
- [hex-grid-math skill](../skills/hex-grid-math/SKILL.md) — Coordinate math
- [state-machine skill](../skills/state-machine/SKILL.md) — FSM design
- [cycle-tap-mechanism skill](../skills/cycle-tap-mechanism/SKILL.md) — Tap logic
- [code-standards skill](../skills/code-standards/SKILL.md) — SOLID principles
