---
name: hexagonal-grid-ui-ux
description: Implement SyV-Flet UI/UX with hexagonal grid interface, minimalist design, and Kenney assets. Use when building screens, styling buttons, responsive layouts, or visual feedback systems.
allowed-tools: Read, Grep, Write, Edit, Bash
---

# SyV-Flet Hexagonal Grid UI/UX

Comprehensive guide for implementing the minimalist, grid-focused UI/UX of SyV-Flet.

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
│   HEXAGONAL GRID (95% of viewport)              │
│   ┌────────────────────────────────────────┐    │
│   │ [Grass Default, Water = Impassable]    │    │
│   │                                        │    │
│   │ [Board Icons Overlaid on Hexes]        │    │
│   │                                        │    │
│   │ [Interactive Edges with Hotspots]      │    │
│   │                                        │    │
│   │ [Scrolleable + Zoomeable]              │    │
│   └────────────────────────────────────────┘    │
│                                                 │
├─────────────────────────────────────────────────┤
│  [Start Game]  │  [Next Turn]   [? Info]       │
│  (centered)    │  (hidden until order placed)  │
└─────────────────────────────────────────────────┘
```

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

### 2. Next Turn Button

**Purpose:** Confirm order and advance turn (game screen)

```python
next_turn_btn = ft.Container(
    content=ft.Text("NEXT TURN", size=16, weight="bold", color="white"),
    bgcolor="#2196F3",  # Secondary color
    border_radius=50,
    padding=15,
    shadow=ft.BoxShadow(blur_radius=8, color="#000000aa"),
    on_click=lambda _: execute_turn(),
    visible=False  # Hidden until order placed
)

# Position: Bottom right (fixed)
ft.Stack([
    # ... grid and content ...
    ft.Positioned(
        bottom=20,
        right=20,
        child=next_turn_btn
    )
])
```

**Styling:**
- **Identical to Start Game** but secondary color
- **Position:** Fixed bottom-right corner
- **Visibility:** Hidden by default, shown when order ready
- **Transition:** Fade in (animate visibility)

### 3. Hex Edge Interactivity

**Purpose:** Order placement via clicking hex edges

```python
# On hex click:
# 1. Highlight selected unit
# 2. Show hotspots on 6 adjacent edges (if passable)
# 3. Highlight edge on hover → order preview
# 4. Click to confirm → show Next Turn button

class HexInteraction:
    def on_hex_tap(self, q: int, r: int):
        """User taps hexagon."""
        unit = self.board.get_unit_at(q, r)
        if unit:
            self.show_hotspots(unit, q, r)

    def show_hotspots(self, unit, q, r):
        """Display 6 neighbor options."""
        neighbors = self.board.neighbors(q, r)
        for direction, (nq, nr) in enumerate(neighbors):
            if self.board.is_valid(nq, nr):
                self.draw_hotspot(nq, nr, direction)

    def on_hotspot_hover(self, nq, nr):
        """Preview order."""
        # Highlight edge + destination
        # Show order type (MOVE, ATTACK, etc.)

    def on_hotspot_click(self, nq, nr):
        """Execute order."""
        # Store order in engine
        # Show Next Turn button
        # Wait for confirmation
```

## Responsive Design

### Breakpoints

| Device | Width | Hex Size | Layout | Button Position |
|--------|-------|----------|--------|-----------------|
| Desktop HD | 1920x1080+ | 64px | Full Grid | Bottom Right |
| Desktop SD | 1280x720 | 56px | Full Grid | Bottom Right |
| Tablet | 768-1024 | 48px | Scaled | Center Bottom |
| Mobile | <768 | 40px | Zoom Default | Full Width Bottom |

### Implementation

```python
def get_responsive_config(page_width: int, page_height: int) -> dict:
    """Return responsive settings based on viewport."""
    if page_width >= 1920:
        return {"hex_size": 64, "button_pos": "bottom-right"}
    elif page_width >= 1280:
        return {"hex_size": 56, "button_pos": "bottom-right"}
    elif page_width >= 768:
        return {"hex_size": 48, "button_pos": "center-bottom"}
    else:
        return {"hex_size": 40, "button_pos": "full-width-bottom"}
```

### Mobile Optimization

- **Touch Targets:** Minimum 44×44 px (buttons)
- **Scroll Performance:** Use FPS counter, optimize canvas batching
- **Zoom Control:** Pinch-to-zoom on grid (future feature)

## Visual Feedback

### Hover Effects

```python
# On mouse over hex edge:
edge.opacity = 0.7  # Reduce opacity to show selection
edge.bgcolor = "#FFEB3B"  # Highlight color (yellow)

# On mouse leave:
edge.opacity = 1.0
edge.bgcolor = "transparent"  # Reset
```

### State Transitions

| State | Visual | Duration |
|-------|--------|----------|
| Idle | Normal opacity | N/A |
| Hover | Opacity +0.3 brightness | 100ms |
| Selected | Highlight color + glow | 150ms |
| Active Order | Animated pulse | Loop |
| Confirmed | Fade out + disable | 200ms |

### Animation Library

Use Flet's built-in animations:

```python
control.animate_opacity(opacity=0.7, duration_ms=150)
control.animate_scale(scale=1.05, duration_ms=100)
control.animate_rotation(angle=math.radians(45), duration_ms=200)
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

## Related Skills & Docs

- **hex-grid-rendering** — Mathematical precision for grid rendering
- **board-implementation** — Engine-side board logic
- **01-flet-architecture.md** — Layered architecture overview
- **03-code-standards.md** — Mandatory code quality

## Checklist: UI/UX Implementation

- [ ] Kenney assets copied to `assets/` directory
- [ ] Main menu screen with Start Game button (centered, gomoso)
- [ ] Game screen with hex grid (95% viewport)
- [ ] Next Turn button (bottom-right, hidden until order)
- [ ] Hex interactivity (click to select unit, edges for orders)
- [ ] Hotspot hover effects (opacity change, color highlight)
- [ ] Responsive sizing (64px desktop, 40px mobile)
- [ ] Performance: 60 FPS desktop, 30 FPS mobile
- [ ] Touch-friendly on mobile (44×44px minimum)
- [ ] Unit icons overlay correctly on hexes
- [ ] All animations smooth (<200ms)
