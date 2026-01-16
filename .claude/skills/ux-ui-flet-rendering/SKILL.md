---
name: ux-ui-flet-rendering
description: Complete Flet UI/UX implementation. Covers screen layouts, buttons, visual feedback, and responsive design. Includes hexagonal grid as the central component (via hex-grid-flet-rendering).
allowed-tools: Read, Grep, Write, Edit, Bash
---

# UI/UX Flet Rendering

Complete guide for implementing SyV-Flet's user interface on Flet. Focuses on layout, controls, visual hierarchy, and responsive design.

## Design Philosophy: Radical Minimalism

**Core Principle:** Intentional void. Every pixel serves a tactical purpose. No decoration.

### Design Principles

1. **Negative Space as Protagonist** — 95% of screen is the hexagonal grid
2. **Clarity of Intent** — Only 2 visible control elements (Start Game, Next Turn)
3. **Focus on Essential** — Grid dominates, UI recedes
4. **Implicit Feedback** — Interactivity through subtle changes (hover, opacity, tone)
5. **Intentional Emptiness** — Absence creates meaning

## Layout Architecture

### Screen Structure

```
┌─────────────────────────────────────────────────┐
│                                                 │
│         HEXAGONAL GRID (95% of viewport)        │
│  [see hex-grid-flet-rendering for details]     │
│  • Scrolleable and zoomeable                    │
│  • Click detection → hex coordinates            │
│  • Order overlay rendering                      │
│                                                 │
├─────────────────────────────────────────────────┤
│  [Start Game]      [Cambiar Jugador]            │
│  (menu screen)     (during PLANIFICACIÓN)       │
└─────────────────────────────────────────────────┘
```

> **Grid Details:** See `hex-grid-flet-rendering` for rendering hexagons, scrolling implementation, and click-to-coordinate conversion. This skill focuses on the complete interface layout.

### Flet Stack Layers (Bottom to Top)

```python
ft.Stack([
    # Layer 1: Static hexagonal grid (canvas, drawn once)
    hex_grid_canvas,

    # Layer 2: Dynamic elements (units, effects)
    dynamic_canvas,

    # Layer 3: Gesture detection (tap, drag)
    gesture_detector,

    # Layer 4: UI overlays (buttons, info)
    ui_overlay_column
])
```

## Visual Elements

### Terrain (Hexagon Tiles)

**Source:** Kenney Hexagon Kit (`assets/hexagons/Previews/`)

| Terrain | File | Purpose | Passable |
|---------|------|---------|----------|
| Grass (Default) | `grass.png` | Standard terrain | ✓ Yes |
| Water | `water.png` | Obstacles/boundaries | ✗ No |
| Sand | `sand.png` | Variant terrain | ✓ Yes |
| Mountain | `mountain.png` (future) | High terrain | ✗ No |
| Snow | `snow.png` (future) | Special terrain | ✓ Yes |

**Tile Specifications:**
- **Size:** 64×64 px (default, scalable to 40-56px)
- **Format:** PNG with transparency
- **Color Depth:** RGBA (supports overlays)
- **Optimization:** Preload grid at startup, cache canvas

### Board Icons (Unit & Object Markers)

**Source:** Kenney Board Game Icons (`assets/icons/PNG/`)

**Usage:**
- Overlay icons on hexagons to represent units
- Use for visual distinction (Infantry, Officer, Captain)
- Future: Building markers, effect indicators

**Implementation:**
```python
# Example: Place icon on hex
unit_icon = ft.Image(
    src="assets/icons/PNG/unit-infantry.png",
    width=32,  # Half hex size for center placement
    height=32
)
# Position via Stack offset relative to hex center
```

### Typography

**Source:** Kenney Fonts (`assets/fonts/kenney_kenney-fonts/`)

**Usage:**
- Button labels ("Start Game", "Next Turn")
- UI text (turn number, player indicator)
- Future: Info panels, unit names

**Font Hierarchy:**
- **Display:** Large, bold (titles, main buttons)
- **Body:** Medium (labels, descriptions)
- **Caption:** Small (secondary info)

## UI Controls

### 1. Start Game Button

**Purpose:** Initiate new game (menu screen)

```python
start_btn = ft.Container(
    content=ft.Text("Start Game", size=24, weight="bold", color="white"),
    bgcolor="#4CAF50",  # Green accent (TBD)
    border_radius=50,   # Fully rounded (gomoso)
    padding=20,
    shadow=ft.BoxShadow(blur_radius=10, color="#000000aa"),
    on_click=lambda _: navigate_to_game()
)

# Position: Center of screen
ft.Column([
    ft.Container(height=300),  # Spacer
    ft.Row([
        ft.Container(width=500),  # Spacer
        start_btn,
        ft.Container()  # Spacer
    ], expand=True, alignment="center")
])
```

**Styling:**
- **Shape:** Perfect circle (border_radius=50%)
- **Shadow:** Subtle drop shadow (gomoso effect)
- **Color:** Accent color (TBD - recommend: green, blue, or gold)
- **Feedback:** Opacity change on hover (0.8-1.0)
- **Size:** 100-120px diameter

### 2. Cambiar Jugador Button (Hot Seat)

**Purpose:** Switch player while hiding previous orders (game screen, PLANIFICACIÓN phase)

```python
change_player_btn = ft.Container(
    content=ft.Text("Cambiar", size=12, weight="bold", color="white"),
    bgcolor="#FF9800",  # Accent color (orange)
    border_radius=8,
    padding=ft.padding.symmetric(horizontal=12, vertical=8),
    shadow=ft.BoxShadow(blur_radius=6, color="#000000aa"),
    on_click=lambda _: switch_player(),
    # ALWAYS visible during PLANIFICACIÓN phase
    height=60
)

# Position: Bottom right (fixed, small)
ft.Stack([
    # ... grid and content ...
    ft.Positioned(
        bottom=16,
        right=16,
        child=change_player_btn
    )
])
```

**Styling:**
- **Discreto y minimalista** — Small, understated
- **Color:** Accent orange (or muted secondary)
- **Position:** Fixed bottom-right corner, **small offset**
- **Size:** 60px height, auto width (compact)
- **Visibility:** **ALWAYS visible during PLANIFICACIÓN**
- **Behavior:**
  - Click → Hides all orders from current player
  - Clears tap cycling state
  - Switches `player_current` flag in engine
  - Resets UI (clears hex highlights, hotspots)
  - Ready for next player to place orders
- **Responsive:**
  - Desktop: 60px height, bottom=20, right=20
  - Tablet: 50px height, bottom=16, right=16
  - Mobile: 45px height, full width at bottom

**During EJECUCIÓN Phase:**
- Button text changes to "Siguiente Turno" or "EJECUTAR"
- Advances to RESET phase after all orders resolve

### 3. Tap Cycling Visual Design

**Purpose:** Define visual styling for the tap cycling interaction

> **Logic Reference:** See `cycle-tap-mechanism` skill for complete conceptual explanation of tap cycling states, order types, and state transitions.

This section covers **visual design only**—how to represent each tap cycling state on the grid.

#### Visual Feedback During Tap Cycling

**Hex States and Visual Representations:**

| State | Outline | Fill | Icon | Label | Opacity |
|-------|---------|------|------|-------|---------|
| **Idle** | None | None | None | None | N/A |
| **Origin Selected** | Double, 3px, faction color | Light faction color | None | None | 0.2 fill |
| **Adjacent (idle)** | Single, 1px, gray | None | None | None | N/A |
| **Adjacent (hover)** | Single, 2px, gray | Light yellow | None | None | 0.15 fill |
| **Order: ATTACK** | Single, 2px, faction color | Light faction color | Sword icon | "ATTACK" | 0.4 (PLAN) / 1.0 (EXEC) |
| **Order: MOVEMENT** | Single, 2px, faction color | Light faction color | Path icon | "MOVEMENT" | 0.4 (PLAN) / 1.0 (EXEC) |
| **Order: DEPLOY** | Single, 2px, faction color | Light faction color | Shield icon | "DEPLOY" | 0.4 (PLAN) / 1.0 (EXEC) |
| **Defense (origin)** | Double, 3px, faction color | Light faction color | Shield icon | "DEFENSE" | 0.4 (PLAN) / 1.0 (EXEC) |

#### Visual Style Dictionary

```python
# Origin hex (selected, awaiting order)
STYLE_ORIGIN_SELECTED = {
    "outline_width": 3,
    "outline_color": "faction_color",      # Team A (blue) or Team B (red)
    "outline_style": "double",              # Double line
    "fill_color": "faction_color",
    "fill_opacity": 0.2,
    "shadow": "subtle_drop_shadow"
}

# Adjacent hex (hover feedback)
STYLE_ADJACENT_HOVER = {
    "outline_width": 2,
    "outline_color": "#CCCCCC",             # Neutral gray
    "fill_color": "#FFEB3B",                # Yellow highlight
    "fill_opacity": 0.15,
    "opacity_animation": 0.3,              # Fade pulse
    "duration_ms": 100
}

# Hex with order placed (all order types)
STYLE_HEX_WITH_ORDER = {
    "outline_width": 2,
    "outline_color": "faction_color",
    "fill_color": "faction_color",
    "fill_opacity": 0.1,
    "icon_size": "hex_size * 0.6",          # 60% of hex
    "icon_overlay": f"assets/icons/{order_type.lower()}.png",
    "label_text": order_type,
    "label_size": 10,
    "label_color": "white",
    "label_weight": "bold"
}

# Defense order on origin
STYLE_DEFENSE_ORDER = {
    "outline_width": 3,
    "outline_color": "faction_color",
    "fill_color": "faction_color",
    "fill_opacity": 0.2,
    "icon_overlay": "assets/icons/defense.png",
    "icon_size": "hex_size * 0.5",
    "label_text": "DEFENSE",
    "label_color": "white"
}
```

#### Icon Assets Required

Place these in `assets/icons/PNG/` for order visualization:

| Order Type | Filename | Purpose | Size |
|-----------|----------|---------|------|
| ATTACK | `attack.png` | Offensive order marker | 64×64px |
| MOVEMENT | `movement.png` | Multi-hex path marker | 64×64px |
| DEPLOY | `deploy.png` | Safe movement marker | 64×64px |
| DEFENSE | `defense.png` | Defensive stance marker | 64×64px |

**Color Coding:**
- **Team A (Faction 1):** Blue (#2196F3)
- **Team B (Faction 2):** Red (#F44336)
- **Neutral/Hover:** Gray (#CCCCCC) or Yellow (#FFEB3B)

## Responsive Design

### Breakpoints

| Device | Width | Hex Size | Grid Layout | Cambiar Jugador Button |
|--------|-------|----------|----------------|--------|
| Desktop HD | 1920x1080+ | 64px | Full Grid | 60px height, bottom=20 right=20 |
| Desktop SD | 1280x720 | 56px | Full Grid | 60px height, bottom=20 right=20 |
| Tablet | 768-1024 | 48px | Scaled | 50px height, bottom=16 right=16 |
| Mobile | <768 | 40px | Zoom Default | 45px height, bottom=12 right=12 |

### Implementation

```python
def get_responsive_config(page_width: int, page_height: int) -> dict:
    """Return responsive settings based on viewport."""
    if page_width >= 1920:
        return {
            "hex_size": 64,
            "button_height": 60,
            "button_bottom": 20,
            "button_right": 20
        }
    elif page_width >= 1280:
        return {
            "hex_size": 56,
            "button_height": 60,
            "button_bottom": 20,
            "button_right": 20
        }
    elif page_width >= 768:
        return {
            "hex_size": 48,
            "button_height": 50,
            "button_bottom": 16,
            "button_right": 16
        }
    else:
        return {
            "hex_size": 40,
            "button_height": 45,
            "button_bottom": 12,
            "button_right": 12
        }
```

### Mobile Optimization

- **Touch Targets:** Minimum 44×44 px (buttons meet this on all breakpoints)
- **Tap Detection:** Use `on_tap` in GestureDetector with tolerance for fat-finger input
- **Scroll Performance:** Use FPS counter, optimize canvas batching
- **Zoom Control:** Pinch-to-zoom on grid (future feature)

## Order Visibility: Opacity and Phase Transitions

> **Conceptual Details:** See `cycle-tap-mechanism` skill section 7 for complete explanation of how order secrecy works during PLANIFICACIÓN and EJECUCIÓN phases.

### Visual Rendering by Phase

**PLANIFICACIÓN Phase (Secret Orders):**
- Current player's orders: Visible with opacity **0.4** (faint, transparent)
- Previous player's orders: **Completely hidden** (not rendered)
- Effect: Current player can see their own orders while building, but opponent's orders are secret
- Pool counter: Visible only to current player

**EJECUCIÓN Phase (All Orders Visible):**
- All orders from both players: Visible with opacity **1.0** (full)
- Faction colors distinguish teams (Team A blue, Team B red)
- Icon overlays, labels, and outlines fully visible
- Orders execute simultaneously (WEGO principle)

### Opacity Transitions

When switching from PLANIFICACIÓN to EJECUCIÓN:

```python
# Animation: Fade in all hidden orders
animation_duration = 200  # milliseconds
opacity_start = 0.0
opacity_end = 1.0
all_hexes.animate_opacity(opacity_end, duration_ms=animation_duration)

# Orders materialize on canvas as phase changes
# Team colors and icons become visible
```

### Changing Players (Hot Seat)

When "Cambiar Jugador" button is tapped:

```
# Before switch:
#  - Player A's orders visible (opacity 0.4) on canvas
#  - Pool counter shows available orders for Player A

# Button click effect:
#  - All current orders fade out (animate_opacity 0.0)
#  - Canvas clears completely
#  - State resets (origin_hex = NULL, adjacent_orders = {})

# After switch:
#  - Player B's turn begins
#  - New blank grid presented
#  - Player B's pool counter visible
#  - Player A's previous orders NOT visible (secret)
```

## Visual Feedback

### Hover Effects (During Tap Cycling)

```python
# On mouse over adjacent hex (during origin selected):
adjacent_hex.opacity = 0.7
adjacent_hex.bgcolor = "#FFEB3B"  # Highlight color

# On mouse leave:
adjacent_hex.opacity = 0.5
adjacent_hex.bgcolor = "transparent"
```

### State Transitions

| State | Visual | Duration |
|-------|--------|----------|
| Idle | No highlight | N/A |
| Origin Selected | Double outline, solid | Immediate |
| Adjacent (hover) | Single outline, +opacity | 100ms |
| Order on Adjacent | Icon + label visible | Immediate |
| Defense on Origin | Shield icon | Immediate |
| Confirmed (EJECUCIÓN) | Full opacity, faction color | 150ms fade-in |

### Animation Library

Use Flet's built-in animations:

```python
# Fade in orders when switching to EJECUCIÓN
control.animate_opacity(opacity=1.0, duration_ms=200)

# Highlight animation on selection
control.animate_scale(scale=1.05, duration_ms=100)
```

## Performance Considerations

### Canvas Optimization

1. **Static Canvas:** Draw grid once at startup
   ```python
   hex_canvas = cv.Canvas(shapes=draw_all_hexes(), cached=True)
   ```

2. **Dynamic Canvas:** Update only changed elements
   ```python
   # Only redraw units that moved, not entire grid
   dynamic_canvas.shapes = [update_unit_positions()]
   ```

3. **Gesture Layer:** Transparent overlay, minimal paint
   ```python
   gesture = ft.GestureDetector(on_tap=handle_tap, mouse_region=True)
   ```

### Frame Budget

- **Desktop:** 60 FPS = 16.7ms per frame
- **Mobile:** 30 FPS = 33.3ms per frame
- **Grid Render:** <5ms (static, cached)
- **Dynamic Update:** <5ms (units only)
- **UI Update:** <3ms (buttons, text)

## File References

| File | Purpose |
|------|---------|
| `src/syv_flet/ui/app.py` | Main Flet entry point |
| `src/syv_flet/ui/screens/game_screen.py` | Game view (grid + buttons) |
| `src/syv_flet/ui/components/hex_grid.py` | Hex grid widget |
| `src/syv_flet/ui/controllers/game_controller.py` | UI ↔ Engine bridge |
| `PRD.md` (Section 4) | Complete UI/UX specification |

## Related Skills & Documentation

- **hex-grid-flet-rendering** — Flet canvas, scrolling, click detection
- **cycle-tap-mechanism** — Order placement logic (pseudocode)
- **code-standards** — Code quality and SOLID principles
- **hex-grid-math** — Hexagonal coordinate mathematics
- **dev-environment** — Development setup and workflow

## Checklist: UI/UX Implementation

- [ ] Kenney assets copied to `assets/` directory
- [ ] Main menu screen with Start Game button (centered, gomoso)
- [ ] Game screen with hex grid (95% viewport)
- [ ] Cambiar Jugador button (bottom-right, 60px, always visible in PLANIFICACIÓN)
- [ ] Tap cycling state machine on hex centers (origin → adjacent → cycles)
- [ ] Origin hex: Double outline when selected, faction color
- [ ] Adjacent hexes: Single outline, semi-transparent, activate on hover
- [ ] Order icons visible on destination hexes with labels (DEPLOY/MOVE/ATTACK/SUPPORT)
- [ ] Defense order icon on origin when cycled to defense
- [ ] Orders hidden when switching players (Cambiar Jugador click)
- [ ] Orders invisible during PLANIFICACIÓN (opacity 0.4)
- [ ] Orders fully visible during EJECUCIÓN (opacity 1.0, both factions)
- [ ] Responsive sizing (64px desktop, 40px mobile)
- [ ] Cambiar Jugador button responsive (60px → 45px)
- [ ] Performance: 60 FPS desktop, 30 FPS mobile
- [ ] Touch-friendly on mobile (44×44px minimum)
- [ ] Unit icons overlay correctly on hexes
- [ ] Tap detection tolerant of fat-finger input
- [ ] All animations smooth (<200ms)
- [ ] State transitions clear (selection, hover, order placement)
