---
name: hex-grid-flet-rendering
description: Semantic Visualization Contracts for Flet. Defines the "WHAT" of rendering (layers, orientation, input mapping, visual states) without prescribing the "HOW" (code).
allowed-tools: Read
---

# Hex Grid Visualization Layer

## 1. Architectural Contract

The system renders the map using a **Layered Architecture** implemented via a Flet `Stack`.

| Layer | Component | Type | Responsibility |
| :--- | :--- | :--- | :--- |
| **0 (Base)** | `StaticGridCanvas` | Cached Canvas | Renders the immutable terrain grid (Grass, Water) ONE time. |
| **1 (Dynamic)** | `OrderLayerCanvas` | Dynamic Canvas | Renders ephemeral state: Selection highlights, Order paths, Icons. |
| **2 (Input)** | `GestureDetector` | Transparent Overlay | Captures Tap/Drag events and routes them to the Controller. |
| **3 (UI)** | `HUD Overlay` | Column/Stack | Renders floating UI elements (Turn counters, Phase buttons). |

## 2. Orientation Contract: Flat-Top

The grid **MUST** be rendered in **Flat-Top** orientation.

```
      TOP FLAT
      ──────
     ╱      ╲
    ╱        ╲
   │  (q,r)   │
    ╲        ╱
     ╲      ╱
      ──────
```

### Geometric Specifications
*   **Vertices (Angles):** 0°, 60°, 120°, 180°, 240°, 300°.
*   **Bounding Ratio:** Width > Height.
    *   `Width = Size * 2.0`
    *   `Height = Size * √3`

## 3. Rendering Contracts

### R.1 Hexagon Generation
*   **Input:** `Center(cx, cy)`, `Size(s)`.
*   **Output:** Closed Path with 6 vertices.
*   **Logic:** Generate points at `angle = n * 60°` for `n=0..5`.

### R.2 Coordinate Mapping (Axial <-> Pixel)
*   **Contract:** See `hex-grid-math` skill.
*   **Constraint:** The rendering layer MUST use the exact same transform formulas as the Math layer to ensure clicks map correctly to visuals.

### R.3 Viewport Culling
*   **Goal:** Only render hexes visible on screen.
*   **Logic:**
    1.  Calculate visible `(x, y)` bounds from Scroll Offset.
    2.  Expand bounds by `HexWidth` (safety margin).
    3.  Iterate `(q, r)` and checking if `PixelCenter(q, r)` is inside bounds.

## 4. Input Contracts

### I.1 Tap Handling
*   **Event:** User taps screen at `(evt.x, evt.y)`.
*   **Processing:**
    1.  **Inverse Transform:** Convert `Pixel(x, y)` -> `Axial(q, r)` (using `pixel_to_hex` from Math skill).
    2.  **Validation:** Check if `(q, r)` exists in `GameState.map`.
    3.  **Action:** Delegate `(q, r)` to `GameController.handle_click()`.

## 5. Visual State Contracts

The visual appearance of a hex changes based on the Game Phase and Interaction State.

### V.1 Selection States (Tap Cycling)

| State | Stroke Style | Fill Style | Opacity | Layer |
| :--- | :--- | :--- | :--- | :--- |
| **Idle** | `1px Black` | (Texture) | 1.0 | Static |
| **Origin Selected** | `3px FactionColor` (Double) | `FactionColor` | 0.2 | Dynamic |
| **Adjacent (Hover)** | `2px Gray` | `Yellow` | 0.15 | Dynamic |

### V.2 Order Visibility (Privacy)

The renderer must respect the `GameState` privacy rules (See `state-machine`).

| Phase | Player Context | Order Visibility | Opacity |
| :--- | :--- | :--- | :--- |
| **PLANNING** | Active Player | **Visible** | `0.4` (Ghost) |
| **PLANNING** | Opponent | **HIDDEN** | `0.0` (Invisible) |
| **EXECUTION** | (All) | **Visible** | `1.0` (Solid) |

### V.3 Order Icons

| Order Type | Icon Asset | Label Style |
| :--- | :--- | :--- |
| **ATTACK** | `icons/attack.png` | Bold White Text |
| **MOVE** | `icons/movement.png` | Bold White Text |
| **DEFEND** | `icons/defense.png` | Bold White Text |
| **DEPLOY** | `icons/deploy.png` | Bold White Text |

## 6. Performance Budget

*   **Static Grid:** Draw ONCE. Cache results.
*   **Dynamic Layer:** Re-draw ONLY on dirty state events (`SelectionChanged`, `OrderPlaced`).
*   **FPS Target:** 60fps (Desktop), 30fps (Mobile).


## Related Skills & Documentation

- **Mathematical Reference:** `hex-grid-math` skill (cubic coordinates, distance, adjacency)
- **UI/UX Container:** `ux-ui-flet-rendering` skill (complete interface layout)
- **Code Standards:** `code-standards` skill (SOLID principles, architecture)
- **Implementation:** `src/syv_flet/ui/components/hex_grid.py`
