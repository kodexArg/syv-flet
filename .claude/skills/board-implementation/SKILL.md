---
name: board-implementation
description: Implement game board systems using hexagonal architecture. Use when building board logic, tile systems, grid operations, or board-UI integration.
allowed-tools: Read, Grep, Write, Edit, Bash
---

# Board Implementation Guide

The board is the core game structure. Implementation must follow hexagonal architecture:
- **Pure Logic:** `src/syv_flet/engine/board.py` (Flet-agnostic, fully testable)
- **UI Layer:** `src/syv_flet/ui/components/hex_grid.py` (Flet rendering)

## Architectural Pattern

```
User Input (UI)
    ↓
GameController (Bridge)
    ↓
Engine.board.method() (Pure Logic)
    ↓
Observer Event
    ↓
HexGridWidget.update() (Visual Update)
```

**Key Rule:** Engine layer **NEVER imports Flet**. All dependencies flow downward only.

## Board API Reference

### Initialization
```python
from src.syv_flet.engine.board import Board

board = Board(width: int, height: int, hex_size: int = 40)
```

### Core Methods

| Method | Returns | Purpose |
|--------|---------|---------|
| `is_valid(q, r)` | bool | Check if coordinates exist on board |
| `neighbors(q, r)` | list[tuple] | Get 6 adjacent hexagons |
| `distance(a, b)` | int | Hex distance between two coordinates |
| `get_tile(q, r)` | Tile \| None | Retrieve tile at position |
| `set_tile(q, r, tile)` | None | Place tile at position |
| `get_unit_at(q, r)` | Unit \| None | Get unit occupying hex |
| `all_tiles()` | list[Tile] | Get all tiles on board |

### Hex Coordinate System

- **Format:** Axial coordinates (q, r)
- **Conversion:** See `.claude/docs/hexagonal-grid-coordinates.md`
- **Distance formula:** `max(|q1-q2|, |r1-r2|, |s1-s2|) / 2` where s = -q - r

## Implementation Examples

### 1. Basic Board Creation

```python
# src/syv_flet/engine/board.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Tile:
    q: int
    r: int
    terrain: str
    unit: Optional["Unit"] = None

class Board:
    def __init__(self, radius: int = 20):
        self.radius = radius
        self.tiles: dict[tuple[int, int], Tile] = {}
        self._initialize()

    def _initialize(self):
        """Create all hex tiles within radius."""
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:
                    self.tiles[(q, r)] = Tile(q, r, terrain="grass")

    def is_valid(self, q: int, r: int) -> bool:
        return (q, r) in self.tiles
```

### 2. Path Finding

```python
from collections import deque

def get_path(self, start: tuple, goal: tuple, max_range: int) -> list[tuple]:
    """BFS pathfinding within range."""
    if self.distance(start, goal) > max_range:
        return []

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (q, r), path = queue.popleft()

        if (q, r) == goal:
            return path

        for neighbor in self.neighbors(q, r):
            if neighbor not in visited and self.is_valid(*neighbor):
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []
```

### 3. Unit Placement

```python
def place_unit(self, unit: "Unit", q: int, r: int) -> bool:
    """Place unit on board. Return True if successful."""
    if not self.is_valid(q, r):
        raise ValueError(f"Invalid coordinates: ({q}, {r})")

    tile = self.tiles[(q, r)]
    if tile.unit is not None:
        return False  # Tile occupied

    tile.unit = unit
    unit.position = (q, r)
    return True
```

## Testing Board Logic

```python
# tests/test_board.py
import pytest
from src.syv_flet.engine.board import Board, Tile

class TestBoard:
    def setup_method(self):
        self.board = Board(radius=3)

    def test_board_initialization(self):
        """Verify board has correct dimensions."""
        assert len(self.board.tiles) > 0

    def test_is_valid(self):
        assert self.board.is_valid(0, 0)
        assert not self.board.is_valid(100, 100)

    def test_neighbors(self):
        neighbors = self.board.neighbors(0, 0)
        assert len(neighbors) == 6

    def test_distance(self):
        d = self.board.distance((0, 0), (1, 0))
        assert d == 1

    def test_place_unit(self):
        from src.syv_flet.engine.units import Unit, UnitType
        unit = Unit("u1", "team_a", UnitType.INFANTRY, (0, 0))
        success = self.board.place_unit(unit, 1, 0)
        assert success
        assert self.board.get_unit_at(1, 0) == unit
```

## UI Integration

### Hex Grid Widget

```python
# src/syv_flet/ui/components/hex_grid.py
import flet as ft
from flet import canvas as cv

class HexGridWidget(ft.Stack):
    def __init__(self, board, hex_size: int = 40):
        super().__init__()
        self.board = board
        self.hex_size = hex_size

        # Static grid (drawn once)
        self.grid_canvas = cv.Canvas(
            shapes=self._create_grid(),
            width=1200,
            height=600
        )

        # Dynamic elements
        self.units_container = ft.Stack()
        self.gesture = ft.GestureDetector(on_tap=self._on_tap)

        self.controls = [self.grid_canvas, self.units_container, self.gesture]

    def _create_grid(self) -> list:
        """Draw all hexagons once."""
        shapes = []
        for (q, r), tile in self.board.tiles.items():
            x, y = self._hex_to_pixel(q, r)
            shapes.append(self._hex_shape(x, y))
        return shapes

    def _on_tap(self, e: ft.TapEvent):
        """Convert pixel coordinates to hex."""
        q, r = self._pixel_to_hex(e.local_x, e.local_y)
        if self.board.is_valid(q, r):
            self.on_hex_clicked(q, r)

    def _hex_to_pixel(self, q: int, r: int) -> tuple:
        """Convert hex to screen coordinates."""
        x = self.hex_size * (3/2 * q)
        y = self.hex_size * (sqrt(3)/2 * q + sqrt(3) * r)
        return x + 600, y + 300  # Center on screen
```

## Validation Script

```bash
# Run before commit
python .claude/skills/board-implementation/scripts/validate-board.py
```

This checks:
- No circular dependencies
- Proper separation (engine ≠ UI)
- Hex coordinate validity
- All methods have type hints
- Tests pass with 80%+ coverage

## Checklist Before Implementation

- [ ] Read `.claude/docs/hexagonal-grid-coordinates.md`
- [ ] All board logic in `engine/board.py` (FLET-FREE)
- [ ] Unit tests in `tests/test_board.py`
- [ ] 80%+ test coverage
- [ ] UI layer in `ui/components/hex_grid.py`
- [ ] All functions type-hinted
- [ ] No comments (self-documenting code)
- [ ] Validation script passes
- [ ] `uv run pytest` passes locally

## Reference

- Architecture: `.claude/docs/01-flet-architecture.md`
- Hex Math: `.claude/docs/hexagonal-grid-coordinates.md`
- Code Standards: `.claude/docs/03-code-standards.md`
