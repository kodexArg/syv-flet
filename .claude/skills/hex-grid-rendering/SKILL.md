---
name: hex-grid-rendering
description: Implement precise hexagonal grid rendering with mathematical accuracy. Use when building hex grid display, coordinate conversions, or solving pixel-perfect alignment issues.
allowed-tools: Read, Grep, Write, Edit, Bash
---

# Hexagonal Grid Rendering - Mathematical Precision

Ultra-precise technical guide for rendering SyV-Flet's hexagonal grid on Flet canvas with exact coordinate transforms.

## Executive Summary

This skill covers **rendering only**—the visual display of the hexagonal grid on `flet.canvas`. For game logic, see `board-implementation`. For UI/UX structure, see `hexagonal-grid-ui-ux`.

## Mathematical Foundation

### Coordinate System: Axial Projection

SyV-Flet uses **axial coordinates (q, r)** internally but renders with **offset coordinates (col, row)** for visual alignment.

**Relationship:**
```
Axial (q, r) ← Internal (lossless)
  ↓ (convert via offset rules)
Visual (col, row) → Screen pixels (x, y)
```

### Hex Orientation: Pointy Top (IMPORTANT)

```
        ╱╲
       ╱  ╲
      │ q,r│  ← "Pointy top" (vertices point up/down)
       ╲  ╱
        ╲╱

NOT "Flat top":
      ╱──╲
     │ q,r│
      ╲──╱
```

**Why Pointy Top?** Optimal for hexagonal navigation grids. Flat-top is better for tiling textures.

### Hex Size Definition

**Given:** `size = 64` (pixels, typical value)

```
Pointy Top dimensions:
- outer_radius (R) = size = 64px
- inner_radius (r) = size × √3/2 ≈ 55.4px
- width (x) = 2 × size = 128px
- height (y) = size × √3 ≈ 110.9px
```

**Visual:**
```
       width = 2R
      ├──────────┤
      │          │
      ├──────────┤ height = R√3
  (0,0)
```

## Coordinate Transformation Pipeline

### Step 1: Axial → Offset (Logical)

```python
def axial_to_offset(q: int, r: int) -> tuple[int, int]:
    """Convert axial (q, r) to offset (col, row) for layout."""
    # Using "Odd-R" offset (rows offset by 0.5 on odd)
    col = q + (r - (r & 1)) // 2
    row = r
    return col, row
```

**Why?** Offset coordinates are easier for grid-based calculations (corners, edges).

### Step 2: Offset → Pixel Center (Screen)

```python
def offset_to_pixel_center(col: int, row: int, size: float) -> tuple[float, float]:
    """Convert offset coordinates to pixel center position."""
    # Pointy-top hexagon layout
    x = size * (3/2 * col)
    y = size * (sqrt(3)/2 * col + sqrt(3) * row)
    return x, y
```

**Verify:**
- Hex at (0, 0) center: (0, 0)
- Hex at (1, 0) center: (1.5 × size, √3/2 × size)
- Hex at (0, 1) center: (0, √3 × size)

### Step 3: Pixel → Hex Center (Reverse Transform)

```python
import math

def pixel_to_hex(x: float, y: float, size: float) -> tuple[float, float]:
    """Convert pixel coordinates to hex offset coordinates (float)."""
    # Inverse of offset_to_pixel_center
    # Matrix inversion: 2x2 system

    q_float = (2/3 * x) / size
    r_float = (-1/3 * x + math.sqrt(3)/3 * y) / size
    return q_float, r_float

def round_hex(q: float, r: float) -> tuple[int, int]:
    """Round float hex to nearest integer hex (cube rounding)."""
    # Round in cube coordinate space for accuracy
    s = -q - r

    q_round = round(q)
    r_round = round(r)
    s_round = round(s)

    # Fix coordinate if rounding error introduced
    q_diff = abs(q_round - q)
    r_diff = abs(r_round - r)
    s_diff = abs(s_round - s)

    if q_diff > r_diff and q_diff > s_diff:
        q_round = -r_round - s_round
    elif r_diff > s_diff:
        r_round = -q_round - s_round
    # else: s is largest, already corrected by q and r

    return int(q_round), int(r_round)

def pixel_to_hex_rounded(x: float, y: float, size: float) -> tuple[int, int]:
    """Pixel to nearest hex (one-shot conversion)."""
    q_float, r_float = pixel_to_pixel(x, y, size)
    return round_hex(q_float, r_float)
```

## Drawing the Grid

### Approach 1: Static Canvas (Recommended for MVP)

Draw entire grid **once at startup**, cache it. Fastest, simplest.

```python
import flet as ft
from flet import canvas as cv
import math

class HexGridRenderer:
    def __init__(self, board_radius: int = 20, hex_size: float = 64):
        self.radius = board_radius
        self.hex_size = hex_size
        self.sqrt3 = math.sqrt(3)

    def create_static_canvas(self) -> cv.Canvas:
        """Create cached hexagon grid canvas."""
        shapes = []

        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                # Check if valid on hex board
                if abs(q + r) <= self.radius:
                    # Create hex path
                    hex_path = self.create_hex_path(q, r)
                    shapes.append(hex_path)

        # Create canvas with all hexagons
        canvas = cv.Canvas(
            shapes=shapes,
            width=2000,
            height=1500,
            expand=True
        )
        return canvas

    def create_hex_path(self, q: int, r: int) -> cv.Path:
        """Create SVG path for single hexagon."""
        # Get pixel center
        col, row = self.axial_to_offset(q, r)
        cx, cy = self.offset_to_pixel_center(col, row, self.hex_size)

        # Calculate 6 vertices (pointy top)
        vertices = []
        for i in range(6):
            angle = math.pi / 3 * i  # 60° increments
            vx = cx + self.hex_size * math.cos(angle)
            vy = cy + self.hex_size * math.sin(angle)
            vertices.append((vx, vy))

        # Convert to SVG path string
        path_data = f"M {vertices[0][0]},{vertices[0][1]}"
        for vx, vy in vertices[1:]:
            path_data += f" L {vx},{vy}"
        path_data += " Z"  # Close path

        # Create path with styling
        hex_path = cv.Path(
            data=path_data,
            stroke="black",
            stroke_width=1,
            fill="none"  # Will be filled with tile image
        )
        return hex_path

    @staticmethod
    def axial_to_offset(q: int, r: int) -> tuple[int, int]:
        col = q + (r - (r & 1)) // 2
        row = r
        return col, row

    def offset_to_pixel_center(self, col: int, row: int) -> tuple[float, float]:
        x = self.hex_size * (3/2 * col)
        y = self.hex_size * (self.sqrt3 / 2 * col + self.sqrt3 * row)
        return x, y
```

### Approach 2: Textured Hexagons (Kenney Assets)

Overlay texture tiles on grid:

```python
class TexturedHexGrid(HexGridRenderer):
    def __init__(self, board_radius: int, hex_size: float, asset_path: str):
        super().__init__(board_radius, hex_size)
        self.asset_path = asset_path  # e.g., "assets/hexagons/Previews/"

    def create_hex_visual(self, q: int, r: int, terrain: str) -> ft.Image:
        """Create visual hex tile with texture."""
        texture_file = f"{self.asset_path}{terrain}.png"

        col, row = self.axial_to_offset(q, r)
        cx, cy = self.offset_to_pixel_center(col, row)

        # Create image at hex center
        hex_image = ft.Image(
            src=texture_file,
            width=self.hex_size * 1.5,
            height=self.hex_size * 1.5,
            fit="contain"
        )

        # Position in Stack (offset to center)
        return ft.Positioned(
            left=cx - self.hex_size * 0.75,
            top=cy - self.hex_size * 0.75,
            child=hex_image
        )
```

## Interaction: Click → Hex Conversion

### Click Event Handler

```python
class HexGridInput:
    def __init__(self, renderer: HexGridRenderer):
        self.renderer = renderer

    def on_tap(self, e: ft.TapEvent) -> tuple[int, int]:
        """Convert tap position to hex coordinates."""
        # Get click position (local to canvas)
        click_x = e.local_x
        click_y = e.local_y

        # Convert to hex (with rounding)
        q, r = self.renderer.pixel_to_hex_rounded(
            click_x, click_y,
            self.renderer.hex_size
        )

        # Validate on board
        if self.renderer.is_valid_hex(q, r):
            return q, r
        else:
            return None  # Click outside valid hexes
```

### Gesture Detector Setup

```python
gesture = ft.GestureDetector(
    on_tap=lambda e: handle_hex_tap(e),
    mouse_region=True,
    expand=True
)

def handle_hex_tap(e: ft.TapEvent):
    """Handle hex click with coordinate conversion."""
    hex_coords = hex_grid_input.on_tap(e)
    if hex_coords:
        q, r = hex_coords
        controller.on_hex_selected(q, r)
```

## Edge Hotspots (Order Placement)

Hexagons have 6 edges. Orders are placed on edges (not hex centers).

### Edge Coordinate System

```
        Edge0 (top-right)
           ╱╲
          ╱  ╲
  Edge5  │ HEX│ Edge1
    (NW) │    │ (NE)
         ╲  ╱
          ╲╱
       Edge4 (bot-left)

Edges numbered 0-5 clockwise from top
Each edge connects to a neighbor hex
```

### Calculate Edge Position

```python
def get_edge_position(q: int, r: int, edge_number: int,
                      hex_size: float) -> tuple[float, float]:
    """Get pixel position of hex edge midpoint."""
    col, row = axial_to_offset(q, r)
    cx, cy = offset_to_pixel_center(col, row, hex_size)

    # Get two vertices of this edge
    angle1 = math.pi / 3 * edge_number
    angle2 = math.pi / 3 * (edge_number + 1)

    vx1 = cx + hex_size * math.cos(angle1)
    vy1 = cy + hex_size * math.sin(angle1)
    vx2 = cx + hex_size * math.cos(angle2)
    vy2 = cy + hex_size * math.sin(angle2)

    # Midpoint of edge
    edge_x = (vx1 + vx2) / 2
    edge_y = (vy1 + vy2) / 2

    return edge_x, edge_y
```

### Show Hotspot on Click

```python
def show_edge_hotspots(q: int, r: int):
    """Draw interactive hotspots on 6 edges."""
    neighbors = board.neighbors(q, r)

    for edge_num, (nq, nr) in enumerate(neighbors):
        if board.is_valid(nq, nr):  # Only passable edges
            edge_x, edge_y = get_edge_position(q, r, edge_num, hex_size)

            # Create clickable hotspot
            hotspot = ft.Container(
                width=20, height=20,
                border_radius=10,  # Circle
                bgcolor="#FFEB3B",
                opacity=0.3,
                on_click=lambda _, e=edge_num: place_order(q, r, e)
            )

            # Position in Stack
            positioned = ft.Positioned(
                left=edge_x - 10,
                top=edge_y - 10,
                child=hotspot
            )

            hex_stack.controls.append(positioned)
```

## Performance Optimization

### Caching Strategy

```python
class CachedHexGrid:
    def __init__(self, radius: int, hex_size: float):
        self._cache = {}  # (q, r) → hex_path
        self.radius = radius
        self.hex_size = hex_size

    def get_hex(self, q: int, r: int) -> cv.Path:
        """Get cached hex or create if missing."""
        key = (q, r)
        if key not in self._cache:
            self._cache[key] = self.create_hex_path(q, r)
        return self._cache[key]

    def invalidate(self, q: int = None, r: int = None):
        """Clear cache (rarely needed)."""
        if q is None:
            self._cache.clear()
        else:
            self._cache.pop((q, r), None)
```

### Viewport Culling

Only render hexes visible on screen:

```python
def get_visible_hexes(viewport_x, viewport_y, viewport_w, viewport_h,
                      hex_size: float) -> list[tuple]:
    """Get hexes within viewport bounds."""
    # Rough bounds (expand slightly for safety)
    min_col = int(viewport_x / (1.5 * hex_size)) - 1
    max_col = int((viewport_x + viewport_w) / (1.5 * hex_size)) + 1
    min_row = int(viewport_y / (sqrt(3) * hex_size)) - 1
    max_row = int((viewport_y + viewport_h) / (sqrt(3) * hex_size)) + 1

    visible = []
    for col in range(min_col, max_col):
        for row in range(min_row, max_row):
            q, r = offset_to_axial(col, row)
            if abs(q + r) <= board_radius:
                visible.append((q, r))

    return visible
```

## Integration with Flet

### Complete Example: Hex Grid Widget

```python
import flet as ft
from flet import canvas as cv

class FletHexGridWidget(ft.UserControl):
    def __init__(self, board_radius: int = 20, hex_size: float = 64):
        super().__init__()
        self.renderer = HexGridRenderer(board_radius, hex_size)
        self.input_handler = HexGridInput(self.renderer)

    def build(self):
        self.canvas = self.renderer.create_static_canvas()

        self.gesture = ft.GestureDetector(
            content=self.canvas,
            on_tap=self.on_tap,
            mouse_region=True,
            expand=True
        )

        return self.gesture

    def on_tap(self, e: ft.TapEvent):
        hex_coords = self.input_handler.on_tap(e)
        if hex_coords:
            self.on_hex_clicked(*hex_coords)
            print(f"Hex clicked: {hex_coords}")

    def on_hex_clicked(self, q: int, r: int):
        """Override in subclass."""
        pass
```

## Reference: Complete Coordinate Functions

```python
import math

sqrt3 = math.sqrt(3)

def axial_to_offset(q: int, r: int) -> tuple[int, int]:
    col = q + (r - (r & 1)) // 2
    row = r
    return col, row

def offset_to_axial(col: int, row: int) -> tuple[int, int]:
    q = col - (row - (row & 1)) // 2
    r = row
    return q, r

def offset_to_pixel_center(col: int, row: int, size: float) -> tuple[float, float]:
    x = size * (3/2 * col)
    y = size * (sqrt3 / 2 * col + sqrt3 * row)
    return x, y

def pixel_to_hex(x: float, y: float, size: float) -> tuple[float, float]:
    q_float = (2/3 * x) / size
    r_float = (-1/3 * x + sqrt3/3 * y) / size
    return q_float, r_float

def round_hex(q: float, r: float) -> tuple[int, int]:
    s = -q - r
    q_round = round(q)
    r_round = round(r)
    s_round = round(s)

    q_diff = abs(q_round - q)
    r_diff = abs(r_round - r)
    s_diff = abs(s_round - s)

    if q_diff > r_diff and q_diff > s_diff:
        q_round = -r_round - s_round
    elif r_diff > s_diff:
        r_round = -q_round - s_round

    return int(q_round), int(r_round)

def pixel_to_hex_rounded(x: float, y: float, size: float) -> tuple[int, int]:
    q_float, r_float = pixel_to_hex(x, y, size)
    return round_hex(q_float, r_float)
```

## Validation Checklist

- [ ] Pointy-top orientation verified (vertices up/down)
- [ ] Coordinate transforms tested (axial ↔ offset ↔ pixel)
- [ ] Pixel-to-hex click detection accurate within 1 hex
- [ ] Static canvas renders all hexes (no missing)
- [ ] Edge hotspots align with hex geometry
- [ ] Performance: <5ms canvas render, 60 FPS on desktop
- [ ] Textures load correctly from `assets/hexagons/Previews/`

## Files

- **Mathematical Reference:** `.claude/docs/hexagonal-grid-coordinates.md`
- **UI/UX Container:** `hexagonal-grid-ui-ux` skill
- **Implementation:** `src/syv_flet/ui/components/hex_grid.py`
