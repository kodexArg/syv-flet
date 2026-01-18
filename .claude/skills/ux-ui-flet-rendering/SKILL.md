---
name: ux-ui-flet-rendering
description: Design specifications and visual contracts for Flet UI. Focuses on "Radical Minimalism," layout architecture, and visual feedback states without prescribing implementation code.
allowed-tools: Read
---

# UI/UX Flet Rendering

## 1. Design Philosophy: Radical Minimalism

**Core Principle:** Intentional void. Every pixel serves a tactical purpose. No decoration.

### Principles
*   **Negative Space as Protagonist:** 95% of screen is the hexagonal grid.
*   **Clarity of Intent:** Only 2 visible control elements (`Start/Next Button`, `Phase Transition`).
*   **Implicit Feedback:** Interactivity through subtle changes (hover, opacity, tone).

## 2. Layout Architecture

The application uses a **Two-Screen Model** managed by a high-level router or stack.

### Screen 1: PhaseTransitionScreen (The Privacy Gate)
**Purpose:** Blocks vision between turns (Hotseat privacy) and announces phase changes.
*   **Visuals:**
    *   **Background:** Black Overlay (`#000000`), Opacity 0.95.
    *   **Content:** Single Centered Component -> `PhaseButton`.
    *   **Text:** Dynamic ("Iniciar Partida", "Siguiente Jugador", "Nuevo Turno").

### Screen 2: GameScreen (The Tactical View)
**Purpose:** The active gameplay area.
*   **Layering (Z-Index Stack):**
    1.  **Static Canvas:** Background grid (drawn once, cached).
    2.  **Dynamic Canvas:** Units, terrain effects (re-drawn on state change).
    3.  **Interaction Layer:** Gesture detection (tap, drag).
    4.  **UI Overlay:** Floating buttons and info panels.
*   **Visible Controls:**
    *   `ChangePlayerButton`: Fixed bottom-right. Visible ONLY in PLANNING phase.

## 3. Visual Contracts

### Component: `PhaseButton`
*   **Shape:** Perfect Circle/Pill (Max rounded corners).
*   **Color:** Accent Green (or Contextual).
*   **Shadow:** Deep, cushioned drop shadow (High blur).
*   **Feedback:** Scale up (1.05x) on hover.

### Component: `HexGrid` Visual States
The grid must visually reflect the state of the `cycle-tap-mechanism`.

| State | Visual Contract | Opacity |
| :--- | :--- | :--- |
| **Idle** | Default Grid | 1.0 |
| **Origin Selected** | Double Outline + Faction Color Fill | 0.2 (Fill) |
| **Adjacent (Hover)** | Single Outline + Highlight Color (Yellow) | 0.15 (Fill) |
| **Order: ATTACK** | Faction Color + Icon: `sword` | 0.4 (Plan) / 1.0 (Exec) |
| **Order: MOVE** | Faction Color + Icon: `path/arrow` | 0.4 (Plan) / 1.0 (Exec) |
| **Order: DEFENSE** | Faction Color + Icon: `shield` | 0.4 (Plan) / 1.0 (Exec) |

> **Note:** "Faction Color" refers to the specific color assigned to the active player (e.g., Blue vs Red).

### Component: `OrderVisibility` (Privacy Logic)
*   **PLANNING Phase:**
    *   **Current Player:** Orders visible at **0.4 Opacity** (Ghost mode).
    *   **Opponent:** Orders **HIDDEN** (0.0 Opacity).
*   **EXECUTION Phase:**
    *   **All Players:** Orders visible at **1.0 Opacity** (Solid).

## 4. Responsive Logic

The UI must adapt strictly to these breakpoints without overflowing.

| Device Class | Width Trigger | Hex Size | UI Scaling |
| :--- | :--- | :--- | :--- |
| **Desktop HD** | > 1920px | 64px | Large Buttons (60px) |
| **Laptop** | > 1280px | 56px | Standard Buttons (60px) |
| **Tablet** | > 768px | 48px | Compact Buttons (50px) |
| **Mobile** | < 768px | 40px | Minimal Buttons (45px), Full Width Bottom |

## 5. Asset Standards

*   **Format:** PNG (Transparent).
*   **Source:** Kenney Assets (Hexagons, Game Icons, Fonts).
*   **Resolution:** 64x64px (Base). Scaled down for mobile.

## 6. Performance Budget

*   **Static Grid:** Must use caching (draw once).
*   **Dynamic Layer:** Update only changed hexes (dirty rects).
*   **Target FPS:** 60 (Desktop), 30 (Mobile).
