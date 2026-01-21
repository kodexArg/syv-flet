# SyV-Flet Implementation Plan

**Purpose:** Strategic execution blueprint defining WHAT must be built, in WHAT order, and WHY that sequence matters.

**Scope:** MVP hot-seat gameplay on a single device with privacy protection.

**Philosophy:** This document articulates objectives and dependencies. Implementation details reside in skills. Agents consult skills for the "how."

**Status:** READY FOR EXECUTION
**Version:** 2.0 (Semantic)
**Last Updated:** January 20, 2026

---

## Part I: Foundational Concepts

### The Core Constraint

SyV-Flet must separate game logic completely from presentation. This architectural decision enables future evolution toward cloud multiplayer and server-side execution without rewriting the engine.

Dependencies flow strictly inward: UI depends on engine, engine depends on nothing game-specific. This prevents the engine from becoming entangled with Flet or any presentation framework.

### The Privacy Constraint

Hot-seat gameplay requires absolute certainty that one player cannot observe the opponent's orders during planning. This is achieved through two complementary barriers:

1. **Physical barrier:** The Phase Transition Screen completely obscures all game content between player turns
2. **Logical barrier:** Renderers filter game state during PLANNING phase, excluding opponent units and orders from display

Both barriers operate simultaneously. Neither alone is sufficient.

### The Sequencing Principle

Traditional development creates import failures and integration blockers. This plan employs structural sequencing: the complete file structure exists before any logic implementation.

Once all packages, modules, and `__init__.py` files exist with proper exports, imports succeed even when implementations raise `NotImplementedError`. This enables parallel agent work and prevents blocking on interface contracts.

---

## Part II: What Must Be Built

The system comprises three architectural layers:

### Layer 1: Core Abstractions (Skill: `/configuration-management`)

The configuration file establishes the single source of truth for all tunable parameters. Game rules, board dimensions, UI styling, asset paths, and logging behavior all live in configuration rather than code.

Why configuration exists first: All subsequent modules reference configuration values. Configuration must load successfully before any domain logic executes.

### Layer 2: Game Engine (Pure Python, UI-Agnostic)

The engine implements:
- **Hexagonal coordinate mathematics** for spatial operations
- **Board generation** creating the 1,261-hex topology
- **State container** holding the complete game state as hash maps
- **Order placement mechanism** implementing the cycle-tap interaction model
- **Turn resolution** executing orders deterministically
- **Game controller** orchestrating phase transitions and game flow

The engine is completely isolated from Flet. No presentation framework dependencies exist.

Why engine completeness matters: The engine must be feature-complete and tested before UI development begins. UI depends on stable engine interfaces; if engine logic changes during UI development, UI breaks.

### Layer 3: Presentation Layer (Flet-Specific)

The presentation layer implements:
- **Phase Transition Screen** providing the privacy barrier
- **Game Screen** rendering the tactical view
- **Hex renderer** drawing the board
- **Unit renderer** displaying unit positions with privacy filtering
- **Order renderer** visualizing orders with visibility rules
- **Input handler** converting taps to game actions
- **State observer** reacting to engine state changes
- **Asset manager** loading and caching game resources

The presentation layer reads engine state but never modifies it directly. Changes flow through the game controller only.

Why presentation builds after engine: Presentation components can only be tested meaningfully once the engine provides stable state they can read. Building presentation before engine completion forces either stubbing (creating false contracts) or rebinding later (wasting effort).

---

## Part III: Sequencing and Dependencies

### Dependency Graph

```
Configuration
    ↓
Logging System
    ↓
Engine Models (Enums → Data Models → GameState)
    ↓
Spatial Mathematics (Hex Coordinates)
    ↓
Board Generation & Validation
    ↓
Order Placement State Machine
    ↓
Turn Resolution & Combat
    ↓
Game Controller (Orchestration)
    ↓
Engine Integration Tests
    ↓
Presentation Layer (Screens, Renderers, Input)
    ↓
Main Application (Wiring)
    ↓
End-to-End Verification
```

### Phase Sequencing

#### Phase A: Structural Foundation

**Objective:** Create the complete file and module structure before implementing any logic.

**Why first:** Establishing structure prevents import errors during skeleton creation. Once all `__init__.py` files exist with exports, any module can import any other module, enabling parallel development.

**What gets created:**
1. Configuration file from template (contains all parameter definitions)
2. Package and module structure (all directories and `__init__.py` files)
3. Skeleton modules for all engine components
4. Skeleton modules for all presentation components
5. Test file scaffolding (all test modules with empty implementations)

**How to verify:** All Python imports succeed (even though implementations raise `NotImplementedError`). Pytest can collect all test files. No Flet imports exist in engine packages.

**Duration:** Single pass, no iteration.

#### Phase B: Engine Implementation

**Objective:** Implement pure Python game logic with complete test coverage.

**Why after structure:** With interfaces defined, the hex-engine-developer agent can implement with confidence that function signatures won't change.

**What gets implemented (in dependency order):**

1. **Configuration system** — Load and validate configuration, establish caching mechanism
2. **Logging infrastructure** — Set up structured logging that will persist throughout all phases
3. **Hex mathematics** — All coordinate operations and spatial calculations
4. **Board generation** — Create the initial hex grid topology
5. **Model validation** — Ensure data integrity through Pydantic models
6. **Order placement** — Implement the cycle-tap state machine for order entry
7. **Turn resolution** — Execute orders and resolve combat deterministically
8. **Game controller** — Orchestrate phase transitions and game flow
9. **Integration tests** — Verify engine components work together

**Parallel activity:** test-writer creates BDD tests throughout Phase B, validating each component as it's implemented.

**How to verify:** Engine tests pass with >80% coverage. No Flet imports exist anywhere in engine code. All SOLID principles enforced through code review.

**Why this order matters:**
- Configuration must load first; everything depends on it
- Models must exist before logic that uses them
- Hex math must work before board generation uses it
- Board must exist before order validation
- Individual order validation must work before resolution
- Resolution must work before controller orchestration
- Integration tests verify the whole together

**Duration:** Iterative implementation with continuous testing. Estimated as the most time-intensive phase because game logic is substantial.

#### Phase C: Presentation Implementation

**Objective:** Build Flet UI that reads engine state and translates user input.

**Why after engine:** Presentation cannot be meaningfully tested until engine provides the state it renders. Building before engine completion creates artificial separation.

**What gets implemented (in dependency order):**

1. **Asset loading** — Establish caching for textures and icons
2. **Privacy gate screen** — The Phase Transition Screen that blocks visibility
3. **Hex rendering** — The foundation layer (static cache of board geometry)
4. **Unit rendering** — Display units with privacy filtering during PLANNING
5. **Order rendering** — Display orders with visibility rules
6. **Input handler** — Convert taps to hex coordinates and dispatch to controller
7. **State observer** — React to engine state changes and trigger re-renders
8. **Game screen** — Compose all renderers into the gameplay view
9. **Main application** — Wire components together and establish the Flet entry point

**Parallel activity:** test-writer begins integration tests, verifying that UI correctly renders filtered state.

**How to verify:** Application launches. All screens transition correctly. Privacy filtering prevents opponent visibility during PLANNING. Clicks map to correct hexagons.

**Why this order matters:**
- Assets must load before renderers use them
- Privacy gate appears first, establishes the privacy contract
- Static hex layer must render before dynamic elements (units, orders)
- Unit and order rendering must apply privacy rules correctly
- Input only works after renderers position elements correctly
- Observer pattern connects state changes to visual updates
- Main application wires everything

**Duration:** Iterative implementation with continuous manual verification. The UI builder works from `/ux-ui-flet-rendering` and `/hex-grid-flet-rendering` specifications.

#### Phase D: Verification and Acceptance

**Objective:** Confirm MVP meets all acceptance criteria.

**What gets verified:**

1. **Application launch** — No crashes on startup
2. **Hot-seat flow** — Complete game cycle (P1 planning → transition → P2 planning → execution → cleanup)
3. **Privacy protection** — Opponent orders completely invisible during opponent planning
4. **Order mechanics** — Cycle-tap works for all order types and sequences
5. **Combat resolution** — Deterministic outcomes, ties handled per spec
6. **Five-Hex Rule** — Isolated units eliminated in RESET phase
7. **Test coverage** — >80% engine, >60% UI, >70% overall
8. **Code quality** — SOLID principles enforced, no magic numbers, no comments, type hints everywhere

**How to verify:** Manual gameplay walkthroughs. Automated test suite passes. Code review validates standards.

**Why verification is last:** Only after engine is complete and presentation is built can the system be meaningfully tested end-to-end.

**Duration:** Single verification pass identifying any final issues.

---

## Part IV: Agent Orchestration

### Agents and Their Roles

**hex-engine-developer (Model: Opus)**
- Executes Phase B engine implementation entirely
- Consults `/hex-grid-math`, `/state-machine`, `/cycle-tap-mechanism` skills
- Enforces engine isolation (no Flet imports)
- Works in parallel with test-writer during Phase B

**flet-ui-builder (Model: Sonnet)**
- Implements Phase C presentation layer
- Consults `/ux-ui-flet-rendering`, `/hex-grid-flet-rendering`, `/assets-manager` skills
- Begins work only after engine interfaces stabilize
- Ensures privacy filtering in renderers

**test-writer (Model: Sonnet)**
- Creates BDD tests during Phase B in parallel with implementation
- Creates integration tests during Phase C
- Follows `/testing-framework` conventions
- Validates continuous coverage targets

**code-reviewer (Model: Haiku)**
- Gates Phase B completion via code review
- Gates Phase C completion via code review
- Validates `/code-standards` compliance
- Verifies architectural boundaries

### Execution Timeline

| Phase | Lead Agent | Support Agent | Prerequisite | Gate |
|-------|-----------|---------------|--------------|------|
| A | Manual | — | None | All imports succeed |
| B | hex-engine-developer | test-writer | A complete | >80% coverage, no Flet imports |
| C | flet-ui-builder | test-writer | B complete | UI launches, privacy works |
| D | code-reviewer | test-writer | C complete | All acceptance criteria met |

---

## Part V: Why the Order Matters

### Configuration First

Configuration must load before any code references parameters. If configuration loading fails, all subsequent code fails. Establishing this foundation first prevents cascading failures.

### Engine Before Presentation

The engine defines the contracts that presentation depends on. If engine implementation changes after presentation is built, presentation breaks. Building engine first ensures presentation is built against stable contracts.

### Structure Before Logic

Creating the complete file structure before implementing logic allows all modules to import successfully. This prevents import errors from blocking parallel development.

### Individual Components Before Integration

Testing individual components before they're combined ensures each works correctly in isolation. Integration testing then verifies the system works as a whole.

### Verification Last

Only after engine is complete, presentation is built, and everything is integrated can the system be verified end-to-end. Verification cannot begin before all pieces exist.

---

## Part VI: Acceptance Criteria

The MVP is complete when:

1. **Application launches** without errors, displaying the Phase Transition Screen with "Iniciar Partida" button
2. **Board generates** with exactly 1,261 connected hexagons
3. **Hot-seat cycle works** — Player 1 plans → Phase Transition → Player 2 plans → Execution → Cleanup → Phase Transition → Back to Player 1
4. **Privacy protection functions** — During Player 1 planning, Player 1's units and orders visible at reduced opacity, Player 2's units and orders completely hidden
5. **Order placement works** — Cycle-tap mechanism implements all order types (ATTACK, MOVE, DEFEND, DEPLOY, CANCEL)
6. **Combat resolves** — Deterministic force comparison, ties result in both units static
7. **Five-Hex Rule applies** — Units without officers within 5 hexes are eliminated
8. **Test coverage** — >80% engine, >60% UI, >70% overall
9. **Code standards** — SOLID principles, type hints, no comments, no magic numbers, no Flet imports in engine

---

## Part VII: Key Design Decisions

### Why Pydantic Models

Data validation at boundaries prevents invalid state from corrupting the system. Pydantic validates on construction, ensuring consistency.

### Why Hash Maps for State

Direct O(1) access to units and orders is critical for 60 FPS performance. Hash maps enable instant lookups.

### Why Skeleton-First

Establishing interfaces before implementation prevents import errors and enables parallel development.

### Why Engine Isolation

Separating game logic from presentation allows either to be replaced or evolved independently. This supports future cloud deployment.

### Why Privacy Layers

Physical (screen overlay) + logical (renderer filtering) barriers ensure privacy cannot be circumvented through UI exploration or code review.

---

## Part VIII: Risk Mitigation

**Risk: Import cycles between components**
- Mitigation: Structure established in Phase A prevents this. All imports flow inward.

**Risk: Engine changes during UI development**
- Mitigation: Engine is complete before UI begins. UI doesn't influence engine.

**Risk: Privacy vulnerability discovered late**
- Mitigation: Privacy filtering is implemented in Phase C renderers with explicit filtering logic that code review validates.

**Risk: Performance issues in Flet rendering**
- Mitigation: Canvas caching strategy established in Phase C avoids redrawing static geometry every frame.

**Risk: Determinism broken by late engine changes**
- Mitigation: Engine integration tests run continuously throughout Phase B, catching non-deterministic behavior immediately.

---

## Document Philosophy

This plan describes **WHAT** must be built and **WHEN** it should be built, with clear rationale for the sequencing.

Implementation details—the **HOW**—reside in skills:
- `/hex-grid-math` — How to implement hex coordinates
- `/state-machine` — How to implement FSM transitions
- `/cycle-tap-mechanism` — How to implement order placement
- `/ux-ui-flet-rendering` — How to implement UI layout
- `/code-standards` — How to maintain code quality
- `/testing-framework` — How to write BDD tests

Agents consult these skills when implementing. They don't need the "how" from this plan; they need clarity on objectives and dependencies, which this plan provides.

---

**END OF IMPLEMENTATION PLAN**
