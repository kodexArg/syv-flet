# SyV-Flet Documentation Index

**Complete Navigation Guide for Claude Code Skills and Project Documentation**

---

## 📖 Core Documentation (`/docs/`)

| File | Purpose | Status |
|------|---------|--------|
| **[PRD.md](./docs/PRD.md)** | Product Requirements Document (v2.0) | ✅ Complete |
| **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** | System design & folder structure | ✅ Complete |
| **[REQUIREMENTS.md](./docs/REQUIREMENTS.md)** | Dependencies & versions | ✅ Complete |
| **[STATES.md](./docs/STATES.md)** | Enumerations & state machines | ✅ Complete |

### Key Sections by Topic

**Game Design:**
- PRD § 3 — Mecánica de juego (coordenadas, unidades, resolución)
- PRD § 4 — Interfaz de usuario (minimalismo, privacidad, responsiveness)
- STATES.md — Todas las transiciones de estado (FSM visual)

**Architecture:**
- ARCHITECTURE.md § 1-2 — Design principles, folder structure
- ARCHITECTURE.md § 3-4 — Core layers, dependency injection
- ARCHITECTURE.md § 5 — State machine with `ScreenState` enum

**Hot-Seat Privacy Model:**
- PRD § 4.3 — Estados visuales (PLANNING privado, EXECUTION compartido)
- PRD § 7.6 — Fases del juego con tabla de visibilidad
- STATES.md § 7 — Combinaciones válidas (invariantes)

**Configuration:**
- ARCHITECTURE.md § 6 — Hardcoded values in `configs.yaml`
- REQUIREMENTS.md — Dependencies & setup

---

## 🎯 Claude Code Skills (`/skills/`)

### Foundation Skills (Use first)

| Skill | File | Key Topics | MVP Relevance |
|-------|------|-----------|----------------|
| **state-machine** | `state-machine/SKILL.md` | GamePhase + **ScreenState**, FSM, privacy rules | 🔴 CRITICAL |
| **hex-grid-math** | `hex-grid-math/SKILL.md` | Hex coordinates, distance, neighbors | 🟡 High |
| **cycle-tap-mechanism** | `cycle-tap-mechanism/SKILL.md` | Order placement, tap sequences, **privacy model** | 🔴 CRITICAL |

### UI/UX Skills

| Skill | File | Key Topics | MVP Relevance |
|-------|------|-----------|----------------|
| **ux-ui-flet-rendering** | `ux-ui-flet-rendering/SKILL.md` | **PhaseTransitionScreen**, layout, responsive design | 🔴 CRITICAL |
| **hex-grid-flet-rendering** | `hex-grid-flet-rendering/SKILL.md` | Canvas rendering, **privacy filtering**, click detection | 🔴 CRITICAL |

### Infrastructure Skills

| Skill | File | Key Topics | MVP Relevance |
|-------|------|-----------|----------------|
| **configuration-management** | `configuration-management/SKILL.md` | `configs.yaml` structure, loading, validation | 🟡 High |
| **code-standards** | `code-standards/SKILL.md` | SOLID, type hints, hexagonal architecture | 🟡 High |
| **testing-framework** | `testing-framework/SKILL.md` | BDD with pytest, **privacy model tests** | 🟡 High |
| **dev-environment** | `dev-environment/SKILL.md` | `uv` setup, Python environment | 🟢 Medium |
| **git-workflow** | `git-workflow/SKILL.md` | Conventional commits, branching | 🟢 Medium |
| **assets-manager** | `assets-manager/SKILL.md` | Kenney assets, caching, file organization | 🟢 Medium |
| **logging** | `logging/SKILL.md` | Loguru, log levels, rotation | 🟢 Medium |
| **fix-gaps** | `fix-gaps/SKILL.md` | Recursive gap resolution, checklist, feedback tracking | 🔵 Meta-Skill |
| **user-authentication** | `user-authentication/SKILL.md` | MVP Status: NOT IMPLEMENTED (hot-seat only) | ⚫ Out of scope |

---

## 📁 Documentation Structure

```
.claude/
├── INDEX.md (this file)
├── README.md
│
├── docs/
│   ├── PRD.md (v2.0) ................. Product requirements + privacymodel
│   ├── ARCHITECTURE.md ............... System design + folder structure
│   ├── REQUIREMENTS.md ............... Dependencies & versions
│   └── STATES.md ..................... Enumerations & FSM
│
├── skills/
│   ├── state-machine/ ................ FSM with ScreenState (NEW)
│   ├── ux-ui-flet-rendering/ ......... PhaseTransitionScreen (NEW)
│   ├── hex-grid-flet-rendering/ ...... Canvas privacy filtering
│   ├── hex-grid-math/ ................ Hex math operations
│   ├── cycle-tap-mechanism/ .......... Order placement + privacy model
│   ├── configuration-management/ ..... configs.yaml strategy
│   │   └── example-config.yaml (UPDATED)
│   ├── code-standards/ ............... SOLID principles
│   ├── testing-framework/ ............ BDD testing
│   ├── dev-environment/ .............. uv setup
│   ├── git-workflow/ ................. Commits & branching
│   ├── assets-manager/ ............... Kenney assets
│   ├── logging/ ....................... Loguru config
│   ├── fix-gaps/ ..................... Recursive gap resolution (NEW)
│   │   ├── SKILL.md
│   │   ├── checklist.yaml
│   │   └── feedback.md
│   └── user-authentication/ .......... MVP: NOT IMPLEMENTED
│
└── agents/
    ├── flet-ui-builder.md ............ (reference)
    ├── test-writer.md ................ (reference)
    ├── code-reviewer.md .............. (reference)
    └── hex-engine-developer.md ....... (reference)
```

---

## 🔑 Key Concepts (Quick Reference)

### Privacy Model (Hot-Seat Core Feature)

**Two Layers:**
1. **Physical Barrier** → `PhaseTransitionScreen` (dark overlay, blocks vision)
2. **Visual Filtering** → Canvas renders only `active_player` units during PLANNING

**Result:** Player cannot see opponent's orders until simultaneous EXECUTION.

**Configuration:**
- See `PRD.md § 4.3` — Visual states by phase
- See `STATES.md § 2` — ScreenState enum
- See `example-config.yaml` — `ui.visibility` + `ui.phase_transition`

### State Machine (7 States)

```
START → [PHASE_TRANSITION: "Iniciar Partida"]
    ↓ click
[GAMEPLAY] PLANNING (P1, private)
    ↓ "Siguiente Jugador"
[PHASE_TRANSITION: "Siguiente Jugador"]
    ↓ click
[GAMEPLAY] PLANNING (P2, private)
    ↓ "Siguiente Jugador"
[GAMEPLAY] EXECUTION (shared)
    ↓ auto
[RESET] (silent cleanup)
    ↓ auto
[PHASE_TRANSITION: "Nuevo Turno"]
    ↓ click
[GAMEPLAY] PLANNING (P1, turn_number++)
```

**Master Reference:** STATES.md § 6

### Configuration (Single File)

All hardcoded values live in **`configs.yaml`** (at project root).

**Never put magic numbers in Python source code.**

- Game rules: `game.board.radius`, `game.rules.movement.*`
- UI colors: `ui.faction_colors.*`, `ui.phase_button.*`
- Visibility: `ui.visibility.planning_own_orders`, `ui.visibility.execution_all_orders`
- Assets: `assets.hexagons.path`, `assets.icons.path`

See `example-config.yaml` for complete schema.

---

## 🎬 How to Use This Documentation

### For Implementation (Writing Code)

1. **Start here:** [PRD.md](./docs/PRD.md) (what to build)
2. **Then review:** [ARCHITECTURE.md](./docs/ARCHITECTURE.md) (how to structure)
3. **Deep dive by component:**
   - Game engine → `state-machine` + `hex-grid-math` + `cycle-tap-mechanism`
   - UI rendering → `ux-ui-flet-rendering` + `hex-grid-flet-rendering`
   - Configuration → `configuration-management` + `example-config.yaml`
4. **Validate against:** [code-standards](./skills/code-standards/SKILL.md) SOLID principles

### For Code Review

1. Check against [code-standards SKILL](./skills/code-standards/SKILL.md)
2. Verify state machine matches [STATES.md](./docs/STATES.md)
3. Ensure privacy model follows [PRD § 4.3](./docs/PRD.md) + `cycle-tap-mechanism`
4. Validate configuration keys exist in [example-config.yaml](./skills/configuration-management/example-config.yaml)

### For Testing

1. Reference [testing-framework SKILL](./skills/testing-framework/SKILL.md) (BDD style)
2. Test privacy model: PLANNING private vs EXECUTION shared (see STATES.md § 7)
3. Test FSM transitions (7 states, see STATES.md § 6)
4. Test configuration loading (see configuration-management)

---

## 📊 What's New (v2.0 Update)

✨ **Privacy Model for Hot-Seat:**
- Added `ScreenState` enum (PHASE_TRANSITION, GAMEPLAY)
- Added `PhaseTransitionScreen` component (dark overlay)
- Added `PhaseButton` reusable component (dynamic text)
- Updated cycle-tap-mechanism with privacy documentation
- Updated configuration for overlay + visibility settings

**Files Modified:**
- ✅ PRD.md (v1.1 → v2.0, sections 4.2, 4.4, 7.1, 7.6)
- ✅ ARCHITECTURE.md (screens, components, FSM)
- ✅ STATES.md (added ScreenState, FSM diagram)
- ✅ state-machine SKILL (ScreenState enum, visibility matrix)
- ✅ ux-ui-flet-rendering SKILL (two-screen model)
- ✅ cycle-tap-mechanism SKILL (section 7: privacy model)
- ✅ example-config.yaml (phase_transition, visibility, phase_button)
- ✅ README.md (skills table updated)

**No Breaking Changes:**
- Engine logic unchanged (still deterministic, order-based)
- Board hexagon math unchanged
- Only adds visual layer (privacy filtering + screen gating)

---

## ❓ FAQ

**Q: Where do I find the privacy model documentation?**
A: See PRD.md § 4.3 (visual states) + STATES.md § 2 (ScreenState) + cycle-tap-mechanism § 7 (two-layer model)

**Q: Where are all the config values defined?**
A: `example-config.yaml` in `skills/configuration-management/` shows the schema. The actual `configs.yaml` file goes at project root.

**Q: How does the FSM work?**
A: 7 states total. See STATES.md § 6 (diagram) + ARCHITECTURE.md § FSM section (transiciones con screen_state).

**Q: Can I change the privacy behavior?**
A: Edit `example-config.yaml`:
  - `ui.visibility.planning_own_orders` (default 0.4)
  - `ui.visibility.planning_opponent_orders` (default 0.0 = hidden)
  - `ui.phase_transition.overlay_opacity` (default 0.95)

**Q: What's the difference between GamePhase and ScreenState?**
A: GamePhase (PLANNING/EXECUTION/RESET) controls LOGIC. ScreenState (PHASE_TRANSITION/GAMEPLAY) controls UI DISPLAY. They're orthogonal.

---

## 📞 Contact / Maintenance

**Last Updated:** 18 de Enero, 2026 (v2.0)
**Maintained By:** Claude Code (Automated)
**Language:** 100% English (docs) + Spanish (examples)
**License:** Project source code (future). Docs are internal reference.

---

**Navigation:** [README.md](./README.md) | [PRD.md](./docs/PRD.md) | [ARCHITECTURE.md](./docs/ARCHITECTURE.md)
