# SyV-Flet Implementation Plan

**Purpose:** Comprehensive execution blueprint for building the MVP. This document orchestrates agents, defines execution order with explicit rationale, specifies design patterns, and anticipates failure modes.

**Document Philosophy:** This plan answers not just WHAT to build and HOW to build it, but critically WHY each step occurs in its specific sequence. Every decision is traceable to PRD requirements, architectural constraints, or dependency relationships.

**Language:** English (technical documentation standard)
**Status:** READY FOR EXECUTION
**Version:** 2.0
**Last Updated:** January 20, 2026

---

## Part I: Strategic Foundation

### 1.1 Project Vision and Constraints

SyV-Flet implements a two-player simultaneous-turn strategy game on a hexagonal board. The MVP delivers a fully functional hot-seat experience on a single device, where two players take turns placing orders in privacy, then watch simultaneous resolution together. The architecture must support future evolution toward cloud-based multiplayer without requiring fundamental restructuring.

The critical constraint that shapes every implementation decision is **engine isolation**: the game logic must remain completely independent of Flet, enabling future UI replacement or server-side execution. This drives the hexagonal architecture pattern where dependencies flow strictly inward from presentation to domain.

The second critical constraint is **hot-seat privacy**: since both players share a single screen, the system must guarantee that neither player can observe the opponent's orders during planning. This is achieved through a physical barrier (the Phase Transition Screen) combined with rendering filters that completely exclude opponent data from the canvas during planning phases.

### 1.2 Execution Philosophy: Skeleton-First Architecture

Traditional incremental development creates import errors, circular dependencies, and integration failures. This plan employs a **skeleton-first** approach: we create the complete file structure with proper module boundaries and exports before implementing any logic. This strategy offers three decisive advantages.

First, it eliminates import failures. When all `__init__.py` files exist with correct exports, any module can import any other module without error—even if the implementations raise `NotImplementedError`. This allows parallel development without blocking.

Second, it establishes interface contracts early. By defining function signatures and class structures before implementation, we create binding agreements between components. The engine team and UI team can work independently because the interfaces are fixed.

Third, it enables comprehensive test scaffolding. Test files can import production modules immediately, and test writers can begin creating fixtures and test cases in parallel with implementation.

### 1.3 Agent Orchestration Model

Four specialized agents execute this plan, each with distinct capabilities and constraints.

**hex-engine-developer** (Model: Opus) serves as the engine architect. This agent implements all pure Python game logic including the state machine, hex mathematics, order processing, combat resolution, and game controller. The agent has deep access to `/hex-grid-math`, `/state-machine`, and `/cycle-tap-mechanism` skills. Critically, this agent must never introduce Flet imports into the engine layer—a constraint enforced through code review verification.

**flet-ui-builder** (Model: Sonnet) handles all presentation layer components. This agent builds screens, renderers, input handlers, and the state binder that connects UI to engine. The agent works from `/ux-ui-flet-rendering` and `/hex-grid-flet-rendering` specifications. The UI builder begins work only after the engine provides stable interfaces.

**test-writer** (Model: Sonnet) creates BDD-style tests in parallel with implementation. This agent follows `/testing-framework` conventions, writing tests that describe user behaviors rather than implementation details. Tests run continuously as validation gates between phases.

**code-reviewer** (Model: Haiku) performs quality verification after each major component. This lightweight agent enforces `/code-standards` compliance: SOLID principles, type hints, zero comments, no magic numbers, and architectural boundary integrity.

The orchestration sequence flows as follows: hex-engine-developer and test-writer work in parallel during engine implementation. Once engine interfaces stabilize, flet-ui-builder begins UI work while test-writer continues with integration tests. code-reviewer validates after each phase completion.

---

## Part II: Design Patterns and Architectural Contracts

### 2.1 Core Design Patterns

The architecture employs specific design patterns chosen for their alignment with project requirements. Understanding these patterns is essential for consistent implementation.

**Singleton Pattern (Logical)** governs GameState. There exists exactly one source of truth for game state at any moment. While not implemented as a traditional singleton class, the pattern manifests through the GameController holding a single GameState reference that all components access. This prevents state fragmentation and ensures consistency.

**Observer Pattern** connects engine to UI. The UI layer reacts to state changes rather than polling or directly modifying state. When GameState changes (selection, order placed, phase transition), observers receive notifications and update their visual representations. This decoupling allows the engine to remain UI-agnostic.

**Command Pattern** reifies orders as data objects. Rather than executing orders immediately, the system creates OrderData objects that describe intent. These commands queue for batch execution during the EXECUTION phase. This enables order validation, cancellation, and simultaneous resolution.

**State Pattern** implements the game phase machine. GamePhase and ScreenState enums define discrete states with explicit transition rules. The GameController manages transitions, ensuring valid state sequences and triggering appropriate side effects.

**Strategy Pattern** handles different order types. ATTACK, MOVE, DEFEND, DEPLOY, and CANCEL each implement distinct validation and execution logic. The resolver processes orders by delegating to type-specific strategies.

**Facade Pattern** positions GameController as the primary interface between UI and engine. Rather than exposing internal components, the controller provides a simplified API: `handle_click()`, `advance_phase()`, `switch_player()`, `get_state()`. This hides complexity and enforces controlled access.

**Factory Pattern** generates the hex board. The `generate_board()` function creates the complete hex grid with proper coordinates and initial terrain, encapsulating creation logic.

**Layered Architecture** structures the Flet rendering stack. Four distinct layers (Static Canvas, Dynamic Canvas, Gesture Detector, UI Overlay) compose the game screen, each with specific responsibilities and update frequencies.

### 2.2 Data Flow Contracts

Data flows through the system in well-defined paths that maintain layer separation.

**User Input Flow:** Canvas tap → GestureDetector captures event → InputHandler converts pixel to hex coordinates → GameController.handle_click() validates and processes → GameState updates → StateBinder notifies UI → Renderers redraw affected layers.

**Phase Transition Flow:** Player clicks "Siguiente Jugador" → GameController.switch_player() updates active_player → screen_state becomes PHASE_TRANSITION → UI displays dark overlay → Player clicks button → screen_state becomes GAMEPLAY → UI reveals filtered game view.

**Order Resolution Flow:** EXECUTION phase begins → Resolver iterates pending orders → Movement orders process first (BFS pathfinding, collision detection) → Combat orders resolve (deterministic force comparison) → Five-Hex Rule applies (connectivity check) → Orders marked executed → RESET phase triggers → Turn increments → PLANNING resumes.

### 2.3 Privacy Implementation Contract

Hot-seat privacy requires both physical and logical barriers. The physical barrier is the Phase Transition Screen—a near-opaque overlay that completely obscures game content between turns. The logical barrier is visibility filtering in renderers.

During PLANNING phase with active_player = 0:
- Units where unit.owner == 0: Rendered at full opacity
- Units where unit.owner == 1: Not rendered (completely hidden)
- Orders where order.unit_id resolves to owner == 0: Rendered at 0.4 opacity (ghost mode)
- Orders where order.unit_id resolves to owner == 1: Not rendered

During EXECUTION phase:
- All units: Rendered at full opacity
- All orders: Rendered at full opacity with faction colors

This filtering occurs in the rendering layer, not in GameState. The complete game state always exists; visibility is a presentation concern.

---

## Part III: Execution Sequence

The implementation proceeds through four major phases. Phase A establishes foundation and creates all file skeletons. Phase B implements engine logic. Phase C implements UI components. Phase D performs integration and verification. Each phase contains numbered steps that must execute in order.

### Phase A: Foundation and Skeleton Creation

Phase A creates the complete project structure before any logic implementation. This phase completes in a single pass with no iteration. Upon completion, all imports will succeed (though implementations will raise NotImplementedError), enabling parallel development in subsequent phases.

---

#### A.1 Environment Verification

**Why First:** Nothing can proceed without a functioning Python environment and dependency manager. This step confirms prerequisites before any file creation.

**Agent:** None (manual verification)

**Verification Commands:**
```bash
python3 --version    # Must show 3.12+ (3.13 recommended per PRD)
uv --version         # Must be installed
```

**Failure Recovery:** If uv is missing, install via `curl -LsSf https://astral.sh/uv/install.sh | sh`. If Python version is inadequate, the project cannot proceed—system upgrade required.

**Exit Condition:** Both commands succeed with acceptable versions.

---

#### A.2 Dependency Synchronization

**Why Second:** The virtual environment and locked dependencies must exist before any Python code runs. This establishes the isolation boundary.

**Agent:** None (manual execution)

**Prerequisite Check:** Verify `pyproject.toml` contains required dependencies:
- flet>=0.24.0 (UI framework)
- loguru>=0.7.0 (logging)
- pydantic>=2.0.0 (data validation)
- python-dotenv>=1.0.0 (environment variables)
- pyyaml>=6.0.0 (configuration loading)

**Why pyyaml:** The configuration management strategy centers on `configs.yaml` as the single source of truth. Without PyYAML, no configuration can load, blocking all subsequent initialization.

**Execution:**
```bash
uv sync
uv run python -c "import flet; import pydantic; import loguru; import yaml; print('Dependencies OK')"
```

**Exit Condition:** Import test succeeds.

---

#### A.3 Configuration File Creation

**Why Third:** The configuration file must exist before any code that reads it. Creating `configs.yaml` first establishes the parameter source that all subsequent code references.

**Agent:** None (template copy)

**Source:** `.claude/skills/configuration-management/example-config.yaml`

**Target:** `configs.yaml` (project root)

**Rationale:** The example-config.yaml in the skill directory serves as the canonical template. It contains all required keys organized into logical sections: game rules, UI parameters, asset paths, display settings, and logging configuration. Copying this template ensures completeness.

**Critical Sections That Must Exist:**
- `game.board.radius: 20` — Determines board size (1,261 hexes)
- `game.rules.movement.max_path_waypoints: 3` — Movement path limit
- `game.rules.movement.max_support_distance: 5` — Five-Hex Rule threshold
- `ui.visibility.*` — Privacy opacity values
- `ui.phase_transition.*` — Privacy gate styling

**Verification:**
```bash
uv run python -c "import yaml; c=yaml.safe_load(open('configs.yaml')); assert c['game']['board']['radius'] == 20"
```

**Exit Condition:** Config file parses and contains expected values.

---

#### A.4 Directory Structure Creation

**Why Fourth:** Python's import system requires `__init__.py` files to exist before modules within those packages can be imported. Creating the directory structure with all `__init__.py` files first prevents import errors during skeleton creation.

**Agent:** None (file system operations)

**Critical Ordering Rule:** For each directory, create `__init__.py` BEFORE creating any modules within it. This is not optional—Python will fail to import modules from packages without `__init__.py`.

**Structure to Create:**

```
src/syv_flet/
├── __init__.py                 [exists - verify]
├── config_loader.py            [A.5]
├── logging_config.py           [exists - verify]
├── main.py                     [A.6]
├── __main__.py                 [A.6]
├── engine/
│   ├── __init__.py             [A.7.1 - FIRST]
│   ├── models/
│   │   ├── __init__.py         [A.7.2 - FIRST]
│   │   ├── enums.py            [A.7.3]
│   │   ├── hex_data.py         [A.7.4]
│   │   ├── unit_data.py        [A.7.5]
│   │   ├── order_data.py       [A.7.6]
│   │   └── game_state.py       [A.7.7]
│   ├── hex_math.py             [A.8.1]
│   ├── board.py                [A.8.2]
│   ├── cycle_tap.py            [A.8.3]
│   ├── resolver.py             [A.8.4]
│   └── controller.py           [A.8.5]
├── ui/
│   ├── __init__.py             [A.9.1 - FIRST]
│   ├── screens/
│   │   ├── __init__.py         [A.9.2 - FIRST]
│   │   ├── phase_transition.py [A.9.3]
│   │   └── game_screen.py      [A.9.4]
│   ├── rendering/
│   │   ├── __init__.py         [A.9.5 - FIRST]
│   │   ├── hex_renderer.py     [A.9.6]
│   │   ├── unit_renderer.py    [A.9.7]
│   │   └── order_renderer.py   [A.9.8]
│   ├── input_handler.py        [A.9.9]
│   ├── state_binder.py         [A.9.10]
│   └── assets.py               [A.9.11]

tests/
├── __init__.py                 [A.10.1]
├── conftest.py                 [A.10.2]
├── engine/
│   ├── __init__.py             [A.10.3 - FIRST]
│   ├── test_models.py          [A.10.4]
│   ├── test_hex_math.py        [A.10.5]
│   ├── test_board.py           [A.10.6]
│   ├── test_cycle_tap.py       [A.10.7]
│   ├── test_resolver.py        [A.10.8]
│   ├── test_controller.py      [A.10.9]
│   └── test_integration.py     [A.10.10]
└── ui/
    ├── __init__.py             [A.10.11 - FIRST]
    └── test_screens.py         [A.10.12]
```

---

#### A.5 Configuration Loader Skeleton

**Why Now:** With configs.yaml existing and directory structure in place, we create the module that will load it. This is the first code file because all other modules will depend on configuration values.

**Agent:** hex-engine-developer

**File:** `src/syv_flet/config_loader.py`

**Interface Contract:**
- `load_config(config_path: Path | None = None) -> dict[str, Any]` — Load and validate YAML
- `get_config() -> dict[str, Any]` — Return cached singleton configuration

**Design Pattern:** Module-level singleton. The configuration loads once on first access and caches for subsequent calls. This prevents redundant file I/O and ensures consistency.

**Validation Requirements:** The loader must verify presence of critical keys (`game.board.radius`, `ui.visibility`, etc.) and raise descriptive errors if missing. Fail-fast prevents mysterious downstream failures.

---

#### A.6 Entry Point Skeletons

**Why Now:** Entry points define how the application launches. Creating them early establishes the execution contract.

**Agent:** flet-ui-builder

**Files:** `src/syv_flet/main.py`, `src/syv_flet/__main__.py`

**Why Two Files:** `main.py` contains the Flet application function. `__main__.py` enables `python -m syv_flet` execution by importing and running main. This dual structure follows Python packaging conventions and enables both direct execution and module execution.

**Interface Contract for main.py:**
```python
def main(page: ft.Page) -> None:
    """Initialize and run the Flet application."""
```

---

#### A.7 Engine Model Skeletons

**Why Now:** Data models form the foundation that all engine logic builds upon. Models must exist before any code that manipulates them.

**Agent:** hex-engine-developer

**Order Rationale:** Enums first (no dependencies), then simple models (HexData, UnitData, OrderData), then composite model (GameState which references others).

**A.7.1 — engine/__init__.py:** Export all public engine interfaces. This file must import from submodules and re-export, enabling `from syv_flet.engine import GameState, GameController`.

**A.7.2 — engine/models/__init__.py:** Export all model classes and enums.

**A.7.3 — engine/models/enums.py:** Define GamePhase, ScreenState, TerrainType, UnitType, UnitStatus, OrderType. These are string enums for JSON serialization compatibility (future API readiness).

**A.7.4 — engine/models/hex_data.py:** Pydantic model for single hex cell. Fields: terrain, occupant_id, last_order_id, attributes. Frozen for immutability.

**A.7.5 — engine/models/unit_data.py:** Pydantic model for single unit. Fields: unit_id, owner (validated 0 or 1), unit_type, position, status. Frozen for immutability.

**A.7.6 — engine/models/order_data.py:** Pydantic model for single order. Fields: order_id, unit_id, order_type, coords (single tuple or path list), turn, executed. Frozen for immutability.

**A.7.7 — engine/models/game_state.py:** Root state container (Singleton Pattern). Contains all Hash Maps (map, units, orders), phase tracking (current_phase, screen_state, active_player, turn_number), and ephemeral UI state (selected_hex, order_path, phase_transition_text).

---

#### A.8 Engine Logic Skeletons

**Why Now:** With models defined, we create the logic modules that operate on them.

**Agent:** hex-engine-developer

**Order Rationale:** hex_math (pure functions, no dependencies) → board (uses hex_math) → cycle_tap (uses models) → resolver (uses all above) → controller (orchestrates everything).

**A.8.1 — engine/hex_math.py:** Pure mathematical functions. Skill reference: `/hex-grid-math`. Functions: neighbors, distance, hex_to_pixel, pixel_to_hex, round_hex, is_valid, all_hexagons, line_hex, bfs_path. All functions are stateless and testable in isolation.

**A.8.2 — engine/board.py:** Board generation and validation. Functions: generate_board (Factory Pattern), validate_connectivity (flood fill), count_hexagons (formula verification).

**A.8.3 — engine/cycle_tap.py:** Order placement state machine. Skill reference: `/cycle-tap-mechanism`. Defines TapState enum and functions: process_tap (main handler), get_valid_adjacent, validate_path. This module implements the two-tier tap cycling system for origin and adjacent hex interactions.

**A.8.4 — engine/resolver.py:** Turn resolution logic. Functions: resolve_turn (main), resolve_movements (process MOVE orders), resolve_combat (deterministic comparison), apply_five_hex_rule (connectivity elimination). Must be completely deterministic—same input always produces same output.

**A.8.5 — engine/controller.py:** Game orchestration (Facade Pattern). GameController class with methods: __init__, handle_click, advance_phase, switch_player, get_state. The controller owns a GameState instance and provides the primary API for UI interaction.

---

#### A.9 UI Component Skeletons

**Why Now:** With engine interfaces defined, UI skeletons can establish their dependencies on those interfaces.

**Agent:** flet-ui-builder

**Order Rationale:** Package init files first, then screens (top-level containers), then renderers (canvas components), then utilities (input, state binding, assets).

**A.9.1-A.9.2 — UI package and screens package init files**

**A.9.3 — ui/screens/phase_transition.py:** Privacy gate screen. Skill reference: `/ux-ui-flet-rendering`. Container with black overlay and centered button. Dynamic text based on game state.

**A.9.4 — ui/screens/game_screen.py:** Main gameplay view. Skill reference: `/ux-ui-flet-rendering`. Composes all renderers, input handler, and overlay button. Implements the four-layer stack architecture.

**A.9.5 — Rendering package init**

**A.9.6 — ui/rendering/hex_renderer.py:** Static grid renderer. Skill reference: `/hex-grid-flet-rendering`. Draws hexagons once and caches. Uses hex_to_pixel for positioning.

**A.9.7 — ui/rendering/unit_renderer.py:** Unit visualization with privacy filtering. Filters units based on active_player during PLANNING phase.

**A.9.8 — ui/rendering/order_renderer.py:** Order icons and paths with visibility rules. Applies opacity based on phase and ownership.

**A.9.9 — ui/input_handler.py:** Tap capture and coordinate conversion. Uses pixel_to_hex and delegates to GameController.

**A.9.10 — ui/state_binder.py:** Observer Pattern implementation. Watches GameState for changes and triggers appropriate re-renders.

**A.9.11 — ui/assets.py:** Asset loading and caching. Skill reference: `/assets-manager`. Preloads hex tiles, caches images, provides fallbacks.

---

#### A.10 Test File Skeletons

**Why Now:** With all production modules defined, test files can import them.

**Agent:** test-writer

**A.10.1-A.10.3 — Test package init files**

**A.10.2 — tests/conftest.py:** Shared fixtures following `/testing-framework` conventions. Fixtures: empty_board, game_state_new, player_with_units, pending_orders, mid_execution_state.

**A.10.4-A.10.10 — Engine test files:** One file per engine module, named test_{module}.py.

**A.10.11-A.10.12 — UI test files:** Minimal initially, expanded during Phase C.

---

#### A.11 Skeleton Verification Gate

**Why Last in Phase A:** Confirms all skeletons exist and import correctly before proceeding to implementation.

**Agent:** code-reviewer

**Verification Commands:**
```bash
# Verify all engine imports
uv run python -c "
from syv_flet.engine.models import GameState, HexData, UnitData, OrderData
from syv_flet.engine.models.enums import GamePhase, ScreenState, OrderType, UnitType
from syv_flet.engine import GameController
print('Engine imports: OK')
"

# Verify test collection
uv run pytest --collect-only

# Verify no Flet imports in engine
grep -r "import flet" src/syv_flet/engine/ || echo "Engine isolation: OK"
```

**Exit Condition:** All imports succeed, pytest collects tests, no Flet imports in engine.

---

### Phase B: Engine Implementation

Phase B implements all game logic. The engine must be complete and tested before UI implementation begins, ensuring a stable foundation. The hex-engine-developer agent leads this phase with test-writer working in parallel.

---

#### B.1 Configuration and Logging Implementation

**Why First in Phase B:** All subsequent code depends on configuration loading and logging. These infrastructure components must function before domain logic.

**Agent:** hex-engine-developer

**config_loader.py Implementation:**

The loader must implement a module-level singleton pattern. On first call to `get_config()`, it loads `configs.yaml` from the project root, validates required keys, and caches the result. Subsequent calls return the cached dictionary.

Validation must check for critical keys: `game.board.radius`, `game.rules.movement.max_path_waypoints`, `game.rules.movement.max_support_distance`, `ui.visibility.planning_own_orders`, `ui.phase_transition.overlay_opacity`. Missing keys should raise `KeyError` with descriptive messages identifying which key is absent.

Error handling: If the config file doesn't exist, raise `FileNotFoundError` with the expected path. If YAML parsing fails, propagate the `yaml.YAMLError` with context.

**logging_config.py Implementation:**

Skill reference: `/logging`. Configure Loguru with three sinks:
1. STDERR for immediate development feedback (colored output)
2. debug.log for full trace (DEBUG level and above)
3. error.log for issues requiring attention (ERROR level and above)

Enable rotation per configuration (daily rotation, 30-day retention). The logging module must never use `print()` statements—this is enforced as a code standard.

**Verification:**
```bash
uv run python -c "
from syv_flet.config_loader import get_config
config = get_config()
assert config['game']['board']['radius'] == 20
print('Config loader: OK')
"
```

---

#### B.2 Hex Mathematics Implementation

**Why Second:** All spatial operations depend on hex math. Board generation, pathfinding, and coordinate conversion require these functions.

**Agent:** hex-engine-developer

**Skill Reference:** `/hex-grid-math` contains all formulas and algorithms.

**Implementation Order and Rationale:**

1. **is_valid(q, r, radius)** — First because board generation needs to filter valid coordinates. Uses the cubic constraint: `max(|q|, |r|, |s|) <= radius` where `s = -q - r`.

2. **neighbors(q, r)** — Second because adjacency is fundamental to all game mechanics. Returns six neighbors using direction vectors. Does NOT filter for validity—caller must check.

3. **distance(a, b)** — Third because movement and combat range depend on distance. Implements Manhattan hex distance: `(|dq| + |dr| + |ds|) // 2`.

4. **all_hexagons(radius)** — Fourth for board iteration. Generator that yields all valid (q, r) pairs within radius.

5. **round_hex(frac_q, frac_r)** — Fifth for click detection. Converts fractional coordinates to nearest hex using cubic rounding (round all three, fix the one with largest delta to satisfy q+r+s=0).

6. **hex_to_pixel(q, r, size, center_x, center_y)** — Sixth for rendering. Flat-top formula: `x = size * (3/2 * q)`, `y = size * (sqrt(3)/2 * q + sqrt(3) * r)`, then add center offsets.

7. **pixel_to_hex(x, y, size, center_x, center_y)** — Seventh for input. Inverse of hex_to_pixel. Subtract center offsets, apply inverse matrix, return fractional coordinates for rounding.

8. **line_hex(start, end)** — Eighth for visualization. Linear interpolation in cubic space with rounding.

9. **bfs_path(start, end, is_walkable)** — Ninth for movement validation. Standard BFS returning path list or None.

**Parallel Work:** test-writer creates `test_hex_math.py` with at least 50 test cases covering edge cases: center neighbors, boundary neighbors (fewer than 6 valid), distance symmetry, roundtrip pixel conversion, boundary validity.

**Verification:**
```bash
uv run pytest tests/engine/test_hex_math.py -v --tb=short
```

**Exit Condition:** All hex math tests pass with >95% coverage on hex_math.py.

---

#### B.3 Board Generation Implementation

**Why Third:** With hex math complete, we can generate the game board.

**Agent:** hex-engine-developer

**Implementation:**

`generate_board(radius)` iterates `all_hexagons(radius)` and creates a dictionary mapping `(q, r)` to `HexData` instances with default terrain (GRASS). For R=20, this produces exactly 1,261 hexes (formula: `3*R*(R+1) + 1`).

`validate_connectivity(board)` uses flood fill from origin (0, 0) to verify all hexes are reachable. Returns True if visited count equals board size. This catches generation bugs that might create disconnected regions.

**Why Connectivity Matters:** The Five-Hex Rule eliminates units too far from officers. If the board contains disconnected regions, units could be incorrectly eliminated. Validating connectivity at generation time prevents this class of bugs.

**Verification:**
```bash
uv run python -c "
from syv_flet.engine.board import generate_board, count_hexagons
board = generate_board(20)
assert len(board) == count_hexagons(20) == 1261
print('Board generation: OK')
"
```

---

#### B.4 Cycle-Tap State Machine Implementation

**Why Fourth:** Order placement is the primary user interaction during PLANNING. This must work before controller integration.

**Agent:** hex-engine-developer

**Skill Reference:** `/cycle-tap-mechanism` contains the complete state diagram and transition rules.

**TapState Enum:** IDLE, ORIGIN_SELECTED, DEFENSE_PENDING, ATTACK_ORDER_PLACED, MOVEMENT_PATH_BUILDING, MOVEMENT_ORDER_PLACED.

**Core Function `process_tap(state, q, r)`:**

This function implements the two-tier tap cycling system. Tier 1 handles origin hex cycling (select → defense → cancel). Tier 2 handles adjacent hex cycling (attack → movement path building).

Key transitions:
- IDLE + tap on friendly unit → ORIGIN_SELECTED
- ORIGIN_SELECTED + tap on same hex → DEFENSE_PENDING
- DEFENSE_PENDING + tap on same hex → IDLE (cancel)
- ORIGIN_SELECTED + tap on adjacent → ATTACK_ORDER_PLACED
- ATTACK_ORDER_PLACED + tap on same adjacent → MOVEMENT_PATH_BUILDING
- MOVEMENT_PATH_BUILDING + tap on adjacent to last waypoint → extend path (max 3 waypoints)
- MOVEMENT_PATH_BUILDING + tap on origin → MOVEMENT_ORDER_PLACED (confirm)

The function returns `(new_state, tap_state)` where new_state is the updated GameState and tap_state indicates the current tap cycling state for UI feedback.

**Validation Functions:**

`get_valid_adjacent(state, origin)` returns hexes adjacent to origin that are valid order targets (passable, within board).

`validate_path(path, state)` checks path constraints: no loops, all adjacent, within max waypoints, all hexes passable.

**Parallel Work:** test-writer creates `test_cycle_tap.py` testing all transition sequences.

---

#### B.5 Turn Resolver Implementation

**Why Fifth:** Resolution executes accumulated orders. This is the core game mechanic.

**Agent:** hex-engine-developer

**Implementation Order:**

1. **resolve_movements(state)** — Process MOVE orders. For each pending MOVE order, attempt to move unit along path. Handle collisions: if destination occupied, unit stops at last valid position. Mark order executed.

2. **resolve_combat(state)** — Process ATTACK orders. For each ATTACK, check if attacker and defender occupy adjacent hexes post-movement. Compare forces (unit type determines base force). Higher force wins, loser transitions to ROUTED. Ties result in both units remaining static (PRD requirement: deterministic, no randomness).

3. **apply_five_hex_rule(state)** — Check all units for connectivity to officers. For each unit, calculate minimum distance to any friendly officer. If distance > 5, unit status becomes ELIMINATED. This implements the supply line mechanic.

4. **resolve_turn(state)** — Orchestrate the above in sequence, return new state with all orders marked executed.

**Determinism Contract:** Given identical GameState input, resolve_turn MUST produce identical output. No random number generation, no time-dependent logic, no external state.

**Parallel Work:** test-writer creates `test_resolver.py` with combat scenarios, movement collisions, and five-hex rule cases.

---

#### B.6 Game Controller Implementation

**Why Sixth:** The controller orchestrates all engine components into a coherent API.

**Agent:** hex-engine-developer

**Skill Reference:** `/state-machine` defines FSM transitions and behavioral contracts.

**GameController Class:**

`__init__(state: GameState | None)` — Initialize with provided state or create fresh state with generated board. The controller holds a single GameState reference (Singleton Pattern for state).

`handle_click(q, r)` — Route clicks based on current_phase. During PLANNING, delegate to cycle_tap.process_tap(). During EXECUTION and RESET, ignore input. Return early if screen_state is PHASE_TRANSITION.

`advance_phase()` — Implement FSM transitions:
- PLANNING → EXECUTION: Call resolve_turn()
- EXECUTION → RESET: Apply cleanup
- RESET → PLANNING: Increment turn_number, reset to active_player 0

`switch_player()` — Called when player clicks "Siguiente Jugador". Toggle active_player (0↔1). Set screen_state to PHASE_TRANSITION. Set appropriate phase_transition_text. If both players have completed PLANNING (tracked internally), trigger advance_phase().

`get_state()` — Return current GameState for UI reading.

**Privacy Enforcement:** The controller does not filter data—it exposes complete state. Privacy filtering is a presentation concern handled in UI renderers.

**Parallel Work:** test-writer creates `test_controller.py` testing FSM transitions and state consistency.

---

#### B.7 Engine Integration Tests

**Why Seventh:** Verify engine components work together before UI integration.

**Agent:** test-writer

**test_integration.py Scenarios:**

1. **Complete 3-Turn Game:** Initialize game, place orders for both players across 3 turns, verify state consistency throughout.

2. **Combat Tie Resolution:** Create scenario where two units of equal force attack each other. Verify both remain static per PRD requirement.

3. **Five-Hex Rule Elimination:** Position unit far from all officers, advance to RESET, verify elimination.

4. **Privacy Isolation:** During PLANNING, verify that state contains both players' data (controller doesn't filter), preparing for UI filtering verification.

**Verification:**
```bash
uv run pytest tests/engine/test_integration.py -v
```

---

#### B.8 Engine Code Review Gate

**Why Last in Phase B:** Validate all engine code before UI development begins.

**Agent:** code-reviewer

**Checklist:**
- [ ] Zero Flet imports in `src/syv_flet/engine/` (verified via grep)
- [ ] All functions have complete type hints (verified via pyright)
- [ ] Zero comments in code (self-documenting names only)
- [ ] Zero magic numbers (all values from configs.yaml)
- [ ] All tests pass with >80% engine coverage
- [ ] Black formatting passes
- [ ] Ruff linting passes

**Verification Commands:**
```bash
grep -r "import flet" src/syv_flet/engine/ && echo "FAIL: Flet import found" || echo "Engine isolation: PASS"
uv run pyright src/syv_flet/engine/
uv run black src/syv_flet/engine/ --check
uv run ruff check src/syv_flet/engine/
uv run pytest tests/engine/ --cov=src/syv_flet/engine --cov-fail-under=80
```

**Exit Condition:** All checks pass. Engine is complete and ready for UI integration.

---

### Phase C: UI Implementation

Phase C builds the Flet presentation layer. The flet-ui-builder agent leads this phase. Work begins only after Phase B completion ensures stable engine interfaces.

---

#### C.1 Phase Transition Screen Implementation

**Why First in UI:** This screen appears first when the application launches. It's also the privacy gate—the most critical UI component for hot-seat gameplay.

**Agent:** flet-ui-builder

**Skill Reference:** `/ux-ui-flet-rendering` Section 2 (Layout Architecture)

**Implementation:**

PhaseTransitionScreen extends ft.Container. It renders a near-opaque black overlay covering the entire viewport. At center, a single button (reusable PhaseButton component) displays dynamic text.

Overlay styling from configs.yaml: `ui.phase_transition.overlay_color` (#000000), `ui.phase_transition.overlay_opacity` (0.95).

Button text sources from configs.yaml: `ui.phase_transition.button_text.start`, `.next_player`, `.new_round`. The screen receives `button_text` as a constructor parameter and `on_continue` callback.

**PhaseButton Component:** Reusable across screens. Styling from `ui.phase_button.*` config values: color, border_radius, hover_scale. Implements hover feedback (scale to 1.05).

**Privacy Guarantee:** The overlay_opacity of 0.95 ensures the game board is completely obscured. No game information leaks through the overlay.

---

#### C.2 Hex Renderer Implementation

**Why Second:** The hex grid is the foundation of the game screen. Other renderers layer on top.

**Agent:** flet-ui-builder

**Skill Reference:** `/hex-grid-flet-rendering`

**Implementation:**

HexRenderer maintains a cache of hex positions calculated once at initialization. For each hex in the board, it calculates pixel position via hex_to_pixel, using center offsets to position the grid within the canvas.

The renderer draws hexagon shapes using flat-top geometry. Vertices at angles 0°, 60°, 120°, 180°, 240°, 300° from center. Stroke and fill vary by terrain type (grass vs water).

**Caching Strategy:** The static grid draws once to a cached canvas layer. Subsequent frames reuse this cache until viewport resize triggers regeneration. This is critical for 60 FPS performance.

**Viewport Culling:** Before drawing each hex, check if pixel center falls within visible bounds (with margin for hex size). Skip hexes outside viewport.

**Center Offset Contract:** The hex_to_pixel center_x and center_y parameters must match those used by InputHandler's pixel_to_hex calls. Inconsistency causes click-position mismatch.

---

#### C.3 Unit Renderer Implementation

**Why Third:** Units render on top of the hex grid.

**Agent:** flet-ui-builder

**Implementation:**

UnitRenderer iterates `state.units` and draws unit icons at their hex positions. Icon selection based on unit_type (INFANTRY, OFFICER, CAPTAIN). Color based on owner (faction_colors from config).

**Privacy Filtering (Critical):** During PLANNING phase (`state.current_phase == GamePhase.PLANNING`), filter units:
```
if state.current_phase == GamePhase.PLANNING:
    visible_units = {uid: u for uid, u in state.units.items() if u.owner == state.active_player}
else:
    visible_units = state.units
```

This filtering happens in the renderer, NOT in GameState. The complete state always exists; visibility is presentation-only.

**Opacity:** Full opacity (1.0) for visible units.

---

#### C.4 Order Renderer Implementation

**Why Fourth:** Orders render as overlays on hexes, above units.

**Agent:** flet-ui-builder

**Implementation:**

OrderRenderer draws order icons (sword for ATTACK, arrow for MOVE, shield for DEFEND) and path visualizations (connected lines for movement waypoints).

**Privacy Filtering:** Same pattern as UnitRenderer. During PLANNING, show only active player's orders. During EXECUTION, show all orders.

**Opacity Rules:**
- PLANNING phase, own orders: 0.4 (ghost mode per config `ui.visibility.planning_own_orders`)
- EXECUTION phase, all orders: 1.0 (full visibility)
- Opponent orders during PLANNING: NOT RENDERED (0.0 means skip entirely, not draw transparent)

**Path Visualization:** For MOVE orders, draw line connecting waypoints. Style: dashed line in faction color.

---

#### C.5 Input Handler Implementation

**Why Fifth:** With rendering complete, input handling connects user actions to game logic.

**Agent:** flet-ui-builder

**Implementation:**

InputHandler wraps a GestureDetector that captures tap events on the canvas. On tap, it:
1. Extracts pixel coordinates (e.local_x, e.local_y)
2. Applies center offsets (same as renderer)
3. Calls pixel_to_hex to get fractional coordinates
4. Calls round_hex to get integer coordinates
5. Validates coordinates with is_valid
6. Calls GameController.handle_click(q, r)

**GestureDetector Coverage:** The detector must cover the entire canvas area. Use `expand=True` to ensure complete coverage.

**Coordinate Consistency Contract:** center_x and center_y must match HexRenderer. Extract these values from a shared source (game screen calculates once, passes to both).

---

#### C.6 State Binder Implementation

**Why Sixth:** The observer pattern connects engine state changes to UI updates.

**Agent:** flet-ui-builder

**Implementation:**

StateBinder implements the Observer Pattern. It holds a reference to GameState and a callback function. When state changes, it triggers UI update.

**Change Detection Options:**
1. **Polling:** Timer checks state periodically. Simple but wasteful.
2. **Callback injection:** Controller calls binder.notify() after mutations. Requires controller modification.
3. **Property comparison:** Binder compares current state to cached snapshot, updates on difference.

**Recommended Approach:** Callback injection. Modify GameController to accept an optional `on_state_change` callback. After any mutation (handle_click, advance_phase, switch_player), invoke the callback with new state.

**Selective Update:** Rather than redrawing everything, the binder identifies what changed:
- `selected_hex` changed → update selection highlight
- `orders` changed → update order renderer
- `screen_state` changed → switch screens
- `current_phase` changed → update visibility filters, re-render units and orders

---

#### C.7 Asset Loader Implementation

**Why Seventh:** Assets are needed for rendering but can load during screen composition.

**Agent:** flet-ui-builder

**Skill Reference:** `/assets-manager`

**Implementation:**

AssetLoader preloads critical assets at startup:
- All hex terrain tiles (74 files from assets/hexagons/Previews/)
- Frequently used icons (sword, shield, arrow)
- UI assets (button backgrounds if any)

Cache structure: `dict[str, ft.Image]` mapping relative path to loaded image.

**Loading Pattern:** Synchronous batch load at startup. Accept brief load time for smooth runtime.

**Fallback Strategy:** If asset load fails, render colored rectangle as placeholder and log error. Never crash on missing asset.

**Path Construction:** Paths come from configs.yaml (`assets.hexagons.path`, `assets.icons.path`). Combine with filename to get full relative path.

---

#### C.8 Game Screen Implementation

**Why Eighth:** The main gameplay view composes all renderers and handlers.

**Agent:** flet-ui-builder

**Skill Reference:** `/ux-ui-flet-rendering` Section 2 (GameScreen specification)

**Implementation:**

GameScreen extends ft.Container. It composes components in a Stack with z-ordering:

Layer 0 (Base): Static canvas with HexRenderer output (cached)
Layer 1 (Dynamic): Canvas with UnitRenderer + OrderRenderer output (redrawn on state change)
Layer 2 (Input): GestureDetector (transparent, captures taps)
Layer 3 (UI): Overlay with "Siguiente Jugador" button (visible only in PLANNING)

**Responsive Breakpoints:** Query page width. Select hex_size from config based on breakpoint:
- width > 1920: desktop_1920 (64px)
- width > 1280: desktop_1280 (56px)
- width > 768: tablet (48px)
- else: mobile (40px)

**Button Visibility:** The "Siguiente Jugador" button appears only during PLANNING phase. During EXECUTION, hide it (no user action needed—resolution proceeds automatically).

**Center Offset Calculation:** Determine canvas center based on viewport size. Pass center_x, center_y to both renderers and input handler.

---

#### C.9 Main Application Implementation

**Why Ninth:** The entry point wires everything together.

**Agent:** flet-ui-builder

**Implementation:**

main.py `main(page: ft.Page)` function:
1. Set page title ("SyV-Flet")
2. Load configuration via get_config()
3. Generate board via generate_board(radius from config)
4. Create GameState with generated board
5. Create GameController with state
6. Create StateBinder with update callback
7. Create PhaseTransitionScreen and GameScreen
8. Implement screen router based on state.screen_state
9. Wire button callbacks to controller.switch_player(), controller.advance_phase()
10. Add initial screen to page

**Screen Routing:**
```
if state.screen_state == ScreenState.PHASE_TRANSITION:
    display PhaseTransitionScreen
else:
    display GameScreen
```

**Update Callback:** When StateBinder triggers, check if screen_state changed and swap screens if needed. Otherwise, trigger re-render of current screen.

---

#### C.10 UI Code Review Gate

**Why Last in Phase C:** Validate UI implementation before integration testing.

**Agent:** code-reviewer

**Checklist:**
- [ ] No game logic in UI (presentation only—filtering is presentation)
- [ ] All config values from configs.yaml (no hardcoded colors, sizes)
- [ ] Responsive breakpoints implemented
- [ ] Privacy filtering in renderers verified
- [ ] Black and Ruff pass

**Verification:**
```bash
uv run black src/syv_flet/ui/ --check
uv run ruff check src/syv_flet/ui/
uv run pyright src/syv_flet/ui/
```

---

### Phase D: Integration and Verification

Phase D verifies the complete system and confirms MVP acceptance criteria.

---

#### D.1 Application Launch Verification

**Agent:** None (manual)

**Execution:**
```bash
uv run python -m syv_flet
```

**Expected Behavior:**
1. Window opens with title "SyV-Flet"
2. Phase Transition Screen displays with "Iniciar Partida" button
3. Click button → Game Screen appears
4. Hex grid renders correctly (1,261 hexes visible with scrolling/zoom)

**Failure Diagnosis:** If launch fails, check error messages. Common issues: missing config, import errors, Flet display issues (try `FLET_DISPLAY_WAYLAND=0` on Linux).

---

#### D.2 Manual End-to-End Test

**Agent:** None (manual)

**Test Sequence:**

1. Launch application
2. Click "Iniciar Partida"
3. As P1, tap a hex with a unit (should highlight as origin)
4. Tap adjacent hex (should show ATTACK order)
5. Click "Siguiente Jugador"
6. Verify Phase Transition Screen appears
7. Click button to continue as P2
8. Verify P1's orders are NOT visible
9. Place P2 orders
10. Click "Siguiente Jugador"
11. Verify EXECUTION phase shows ALL orders from both players
12. Verify resolution completes
13. Verify "Nuevo Turno" Phase Transition Screen appears
14. Click to start new turn
15. Verify back at PLANNING P1

**Privacy Verification:** During step 8, actively look for P1's orders. They must be completely invisible.

---

#### D.3 Automated Test Suite Verification

**Agent:** test-writer

**Execution:**
```bash
uv run pytest tests/ --cov=src/syv_flet --cov-report=term-missing --cov-report=html
```

**Coverage Targets:**
- Engine modules: >80%
- UI modules: >60%
- Overall: >70%

**Review Coverage Report:** Open htmlcov/index.html. Identify any uncovered critical paths. Add tests if needed.

---

#### D.4 Final Code Review

**Agent:** code-reviewer

**Complete `/code-standards` Checklist:**

- [ ] **Single Responsibility:** Each class/function has one reason to change
- [ ] **Open/Closed:** New order types can be added without modifying resolver
- [ ] **Liskov Substitution:** N/A (no inheritance hierarchies)
- [ ] **Interface Segregation:** Renderers don't depend on unused controller methods
- [ ] **Dependency Inversion:** UI depends on GameState abstraction, not concrete engine internals

- [ ] **Type Hints:** All functions, all methods, all parameters
- [ ] **Zero Comments:** Code is self-documenting
- [ ] **Pydantic Models:** All data structures are validated
- [ ] **No Magic Numbers:** grep for numeric literals in logic (should only find 0, 1 for player IDs)
- [ ] **No print():** grep for print( in src/
- [ ] **Engine Isolation:** No Flet imports in engine/

**Formatting and Linting:**
```bash
uv run black src/ tests/ --check
uv run ruff check src/ tests/
uv run pyright src/
```

---

#### D.5 MVP Acceptance Criteria Verification

**PRD Section 6 Checklist:**

- [ ] Board R=20 generates correctly (1,261 hexes, all connected)
- [ ] Pixel→hex input works at all responsive breakpoints
- [ ] Phase Transition Screen blocks all visibility between turns
- [ ] Each player sees ONLY their units/orders during PLANNING
- [ ] "Siguiente Jugador" button is the only way to progress
- [ ] EXECUTION shows all orders simultaneously
- [ ] Combat ties result in both units static (not eliminated)
- [ ] Five-Hex Rule eliminates isolated units during RESET
- [ ] Cycle-tap works completely:
  - [ ] Tap origin → selection
  - [ ] Tap origin 2x → DEFENSE
  - [ ] Tap origin 3x → CANCEL
  - [ ] Tap adjacent → ATTACK
  - [ ] Tap adjacent 2x → MOVEMENT path start
  - [ ] Tap successive adjacents → path extension
  - [ ] Tap origin to confirm → MOVEMENT order placed

---

#### D.6 Exclusion Verification

**Confirm NOT Implemented:**

- [ ] Save/Load games (state is volatile)
- [ ] Multiplayer online (hot-seat only)
- [ ] Configuration persistence (configs.yaml only)
- [ ] Undo/Replay functionality

**Why Verify Exclusions:** Prevents scope creep. If any of these features accidentally exist, they should be removed—they are not part of MVP and may contain bugs.

---

#### D.7 Git Commit

**Agent:** None (with user confirmation)

**Skill Reference:** `/git-workflow`

**Commit Message:**
```
feat: complete MVP implementation

- Hexagonal game engine with deterministic resolution
- Flet UI with hot-seat privacy protection
- Complete cycle-tap order system
- BDD test coverage >80% engine, >60% UI

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Part IV: Troubleshooting Reference

### Import and Module Issues

**"ModuleNotFoundError: No module named 'syv_flet'"**
- Cause: Running Python directly instead of through uv
- Fix: Use `uv run python -m syv_flet`

**"ModuleNotFoundError: No module named 'yaml'"**
- Cause: pyyaml not installed
- Fix: `uv add pyyaml` then `uv sync`

**"ImportError: cannot import name 'X' from 'syv_flet.engine'"**
- Cause: Missing export in `__init__.py`
- Fix: Add X to the `__all__` list and import statement in the package init

### Runtime Issues

**Hexagons misaligned with clicks**
- Cause: Different center offsets in renderer vs input handler
- Fix: Extract center calculation to shared location, pass to both components

**Orders not appearing**
- Cause: Visibility filter bug (wrong player or phase check)
- Fix: Add debug logging showing filter conditions and order ownership

**Canvas not responding to taps**
- Cause: GestureDetector not covering full area
- Fix: Ensure `expand=True` on GestureDetector, verify z-order (must be above canvas)

### Performance Issues

**Frame drops / stuttering**
- Cause: Static grid redrawing every frame
- Fix: Verify static canvas caching is implemented, check that cache invalidation isn't too aggressive

**Slow startup**
- Cause: Synchronous asset loading blocking UI
- Fix: Show splash screen while loading, or implement async load with placeholders

### Flet-Specific Issues

**"Visual glitches on Linux"**
- Cause: Wayland/GPU compatibility
- Fix: `FLET_DISPLAY_WAYLAND=0 uv run python -m syv_flet`

**"Window doesn't appear"**
- Cause: Flet debug mode issue
- Fix: `FLET_DEBUG=1 uv run python -m syv_flet` to see detailed logs

---

## Part V: Quick Reference

### Command Reference

```bash
# Environment
uv sync                                    # Install dependencies
uv sync --fresh                            # Clean reinstall

# Execution
uv run python -m syv_flet                  # Run application
FLET_DEBUG=1 uv run python -m syv_flet     # Run with debug

# Testing
uv run pytest tests/ -v                    # Run all tests
uv run pytest tests/engine/ -v             # Run engine tests only
uv run pytest --cov=src/syv_flet           # Run with coverage

# Quality
uv run black src/ tests/                   # Format code
uv run ruff check src/ tests/              # Lint code
uv run pyright src/                        # Type check
```

### File Count Summary

| Category | Count |
|----------|-------|
| Engine modules | 10 |
| UI modules | 11 |
| Test files | 12 |
| Config files | 1 |
| **Total Python files** | **34** |

### Agent Assignments Summary

| Phase | Primary Agent | Support Agent |
|-------|--------------|---------------|
| A (Foundation) | Manual + hex-engine-developer | — |
| B (Engine) | hex-engine-developer | test-writer |
| C (UI) | flet-ui-builder | — |
| D (Verification) | code-reviewer | test-writer |

### Design Pattern Summary

| Pattern | Location | Purpose |
|---------|----------|---------|
| Singleton (Logical) | GameState | Single source of truth |
| Observer | StateBinder | UI reacts to state changes |
| Command | OrderData | Reified orders for batch execution |
| State | GamePhase/ScreenState | Explicit phase transitions |
| Strategy | Order resolution | Type-specific order handling |
| Facade | GameController | Simplified API for UI |
| Factory | generate_board | Board creation encapsulation |
| Layered | Flet Stack | Rendering composition |

---

## Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-20 | Initial version with skeleton approach |
| 2.0 | 2026-01-20 | Complete rewrite with prose explanations, design patterns, explicit rationale, comprehensive agent integration |

---

**END OF IMPLEMENTATION PLAN**
