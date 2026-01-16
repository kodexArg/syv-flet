---
name: hex-grid-math
description: Reference for hexagonal grid coordinate systems and mathematical operations. Use when implementing pathfinding, grid algorithms, coordinate conversions, distance calculations, or adjacency checks.
allowed-tools: Read, Grep
---

# Hexagonal Grid Coordinate Reference

When working with hex grid coordinates in SyV-Flet, use **cubic coordinate system** (q, r, s where q + r + s = 0).

## Quick Reference

### Cubic Coordinates
- **Format:** (q, r, s) where q + r + s = 0
- **Advantage:** All hex operations are linear transformations
- **In SyV-Flet:** Store as (q, r) pairs; compute s = -q - r when needed

### Common Operations

| Operation | Formula | Example |
|-----------|---------|---------|
| Distance | `max(\|q₁-q₂\|, \|r₁-r₂\|, \|s₁-s₂\|)` | Distance between two hexes |
| Adjacent | 6 neighbors around any hex | Pathfinding, visibility |
| Line Drawing | Bresenham-like algorithm | Movement paths, attacks |
| Ring | Hexes at distance N | Area effects |

### Pixel ↔ Coordinate Conversion
- **Offset-to-pixel:** `x = hex_size * (3/2 * q)`, `y = hex_size * (√3/2 * q + √3 * r)`
- **Pixel-to-offset:** Inverse transformation via matrix inversion
- **Rounding:** Use axial rounding (round to nearest axial coordinate)

## Before Implementing

**ALWAYS read the complete mathematical guide:**

```
.claude/docs/hexagonal-grid-coordinates.md
```

This document contains:
- Mathematical foundations and proofs
- Pixel ↔ coordinate conversions (exact code)
- Pathfinding algorithms (BFS, Dijkstra)
- Flood fill and line drawing
- SyV-Flet-specific implementations and optimizations

## Common Implementations

### Distance
```python
def hex_distance(a: tuple, b: tuple) -> int:
    q1, r1 = a
    q2, r2 = b
    s1, s2 = -q1 - r1, -q2 - r2
    return (abs(q1 - q2) + abs(r1 - r2) + abs(s1 - s2)) // 2
```

### Neighbors
```python
DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

def get_neighbors(q: int, r: int) -> list[tuple]:
    return [(q + dq, r + dr) for dq, dr in DIRECTIONS]
```

### Pixel to Hex (2x2 Matrix Inversion)
```python
import math

def pixel_to_hex(x: float, y: float, size: float) -> tuple:
    q = (2/3 * x) / size
    r = (-1/3 * x + math.sqrt(3)/3 * y) / size
    return round_hex(q, r)
```

Refer to `hexagonal-grid-coordinates.md` for complete, tested implementations.
