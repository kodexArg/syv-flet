---
name: hex-grid-math
description: Complete reference for hexagonal grid coordinate systems and mathematical operations. Includes mathematical foundations, derivations, and tested algorithms.
allowed-tools: Read
---

# Hexagonal Grid Mathematics

**Author:** SyV-Flet Team
**Date:** January 16, 2026
**Level:** Technical (for game engine implementers)

---

## 1. Overview

The SyV-Flet board uses a **normalized cubic coordinate system** to represent hexagonal grids. This model provides simple and exact calculations for adjacency, distance, and rotation—critical operations in the game loop.

Although we internally use axial coordinates `(q, r)` for memory optimization, the underlying mathematics use cubic space `(q, r, s)` where **q + r + s = 0** always holds.

---

## 2. Mathematical Foundations

### 2.1. Cubic Space `(q, r, s)`

In a hexagonal grid, each hexagon can be represented as a point in 3D space where the three axes are linearly coupled:

```
Invariant: q + r + s = 0
```

This implies that `s = -q - r`, so we really only need two independent coordinates to uniquely specify a point.

**Geometric Interpretation:**
- Axis **q** (red): points right (East)
- Axis **r** (green): points down-left (South-West)
- Axis **s** (blue): points up-left (North-West)

The three axes are separated by 120° from each other and converge at the origin `(0, 0, 0)`.

### 2.2. Projection to Axial Coordinates `(q, r)`

To reduce memory and complexity, we store only two coordinates:

```
Grid point: (q, r)
Where implicitly: s = -q - r
```

**All operations are calculated using cubic logic, projecting the result back to axial if necessary.**

---

## 3. Fundamental Operations

### 3.1. Adjacency (Immediate Neighbors)

The 6 neighbors of hexagon `(q, r)` are obtained by adding constant direction vectors:

```python
DIRECTIONS = [
    (1, 0),    # East
    (1, -1),   # South-East
    (0, -1),   # South-West
    (-1, 0),   # West
    (-1, 1),   # North-West
    (0, 1),    # North-East
]

def neighbors(q, r):
    """Return list of 6 adjacent hexagons."""
    return [(q + dq, r + dr) for dq, dr in DIRECTIONS]
```

**Cubic Justification:** In cubic coordinates, direction vectors are:
```
(+1, 0, -1), (+1, -1, 0), (0, -1, +1),
(-1, 0, +1), (-1, +1, 0), (0, +1, -1)
```

Projected to axial: only `(q, r)` is used; `s` is recalculated as needed.

### 3.2. Distance (Hexagonal Manhattan)

The distance between two hexagons is the minimum number of steps to go from one to the other:

```python
def distance(a, b):
    """
    Calculate Manhattan distance in hexagonal grid.

    a, b: tuples (q, r)
    Returns: integer >= 0
    """
    aq, ar = a
    bq, br = b

    # Convert to cubic implicitly
    as_ = -aq - ar
    bs_ = -bq - br

    # Manhattan distance in 3D, divided by 2 (because we sum opposite differences)
    return (abs(aq - bq) + abs(ar - br) + abs(as_ - bs_)) // 2
```

**Examples:**
- `distance((0,0), (1,0))` = 1 (neighbors)
- `distance((0,0), (2,0))` = 2 (two steps)
- `distance((0,0), (1,-1))` = 1 (adjacent diagonal)

---

## 4. Pixel-Space Geometry
    
### 4.1. Orientation: Flat-Top

SyV-Flet strictly uses **Flat-Top** orientation.

```
      Score
      ╱   ╲
    ╱       ╲
   │  (q,r)  │
    ╲       ╱
      ╲   ╱
```

**Dimensions:**
*   **Size (`s`):** Distance from center to any vertex.
*   **Width:** `2 * size` (Max width, vertex to vertex).
*   **Height:** `sqrt(3) * size` (Max height, flat side to flat side).
*   **Horiz. Spacing:** `3/2 * size` (Distance between columns).
*   **Vert. Spacing:** `sqrt(3) * size` (Distance between rows).

### 4.2. Hex to Pixel (Forward)

Convert logical axial coordinates `(q, r)` to screen pixel `(x, y)`.

```python
import math

def hex_to_pixel(q: int, r: int, size: float) -> tuple[float, float]:
    """
    Flat-Top Orientation.
    x points right, y points down.
    """
    x = size * (3/2 * q)
    y = size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    return x, y
```

### 4.3. Pixel to Hex (Inverse)

Convert screen pixel `(x, y)` to fractional axial coordinates.

```python
def pixel_to_hex(x: float, y: float, size: float) -> tuple[float, float]:
    """
    Inverse of hex_to_pixel.
    Returns fractional (q, r) which must be rounded.
    """
    q = (2/3 * x) / size
    r = (-1/3 * x + math.sqrt(3)/3 * y) / size
    return q, r
```

### 4.4. Rounding

To get the nearest integer hex, convert fractional `(q, r)` to cubic `(q, r, s)`, round all three, and reset the one with the largest change to satisfy `q+r+s=0`.

```python
def round_hex(frac_q: float, frac_r: float) -> tuple[int, int]:
    frac_s = -frac_q - frac_r
    
    q = round(frac_q)
    r = round(frac_r)
    s = round(frac_s)
    
    q_diff = abs(q - frac_q)
    r_diff = abs(r - frac_r)
    s_diff = abs(s - frac_s)
    
    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s
    else:
        s = -q - r
        
    return q, r
```

---

## 5. Board Topology (Radius R=20)

### 5.1. Valid Hexagons

A hexagonal board of radius R contains all points `(q, r, s)` where:

```
max(|q|, |r|, |s|) <= R
```

In axial coordinates:

```python
def is_valid(q, r, R):
    """Check if (q, r) is within board of radius R."""
    s = -q - r
    return max(abs(q), abs(r), abs(s)) <= R
```

### 5.2. Cardinality

The total number of hexagons in a board of radius R is:

```
Total = 3*R*(R+1) + 1

For R=20: Total = 3*20*21 + 1 = 1,261
```

**Derivation:** A hexagonal board of radius R is a concentric hexagon. Its perimeter grows linearly with R, and its area grows with R². The formula results from summing the area of all "rings" from center to radius R.

### 5.3. Iteration over Board

```python
def all_hexagons(R):
    """Generate all valid coordinates on the board."""
    for q in range(-R, R+1):
        for r in range(max(-R, -q-R), min(R, -q+R) + 1):
            yield (q, r)
```

---

## 6. Common Algorithms

### 6.1. Straight Line Between Two Hexagons

To draw a line from `(q1, r1)` to `(q2, r2)`:

```python
def line_hex(start, end):
    """
    Return list of hexagons in straight line between start and end.

    Uses cubic interpolation with rounding.
    """
    q1, r1 = start
    q2, r2 = end

    dist = distance(start, end)
    result = []

    for i in range(dist + 1):
        t = i / max(1, dist)  # Avoid division by zero

        # Linear interpolation in cubic
        q = q1 + (q2 - q1) * t
        r = r1 + (r2 - r1) * t
        s = -q - r

        # Round to nearest hexagon
        q, r, s = round_hex(q, r, s)

        result.append((int(q), int(r)))

    return result
```

### 6.2. Pathfinding

To find shortest path between two points, use BFS:

```python
from collections import deque

def bfs_hex(start, end, is_walkable):
    """
    BFS on hexagonal grid.

    is_walkable: function(q, r) -> bool
    """
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (q, r), path = queue.popleft()

        if (q, r) == end:
            return path

        for nq, nr in neighbors(q, r):
            if (nq, nr) not in visited and is_walkable(nq, nr):
                visited.add((nq, nr))
                queue.append(((nq, nr), path + [(nq, nr)]))

    return None  # No path exists
```

### 6.3. Flood Fill (Connectivity)

To verify no unreachable islands exist:

```python
def flood_fill(start, is_valid, R):
    """
    Expand from start until reaching all connected hexagons.

    Returns set of reachable coordinates.
    """
    visited = set()
    queue = deque([start])

    while queue:
        hex_current = queue.popleft()

        if hex_current in visited:
            continue

        visited.add(hex_current)

        for neighbor in neighbors(*hex_current):
            if neighbor not in visited and is_valid(*neighbor, R):
                queue.append(neighbor)

    return visited
```

---

## 7. Use Cases in SyV-Flet

### 7.1. Movement Phase

When processing a **MOVE** order (distance 3):

```
1. Calculate distance from current → target hexagon
2. If distance > 3: reject order (invalid)
3. Generate shortest path (BFS)
4. Check collisions at each step
5. Update unit's final position
```

### 7.2. Five-Hexagon Rule

To eliminate isolated units:

```
For each unit U:
  min_dist = min(distance(U, officer) for officer in List_Officers)
  if min_dist > 5:
    Delete U
```

### 7.3. Neighbor Detection for Combat

When resolving combat at hexagon `(q, r)`:

```
Combatants = [all units at (q, r) or in neighbors(q, r)]
Apply combat resolution
```

---

## 8. References and Extensions

### Recommended Reading

- **Red Blob Games "Hexagonal Grids"**: Industry standard reference. Contains detailed formulas and visuals.
  - https://www.redblobgames.com/grids/hexagons/

- **Mathematical Games - Hexagonal Grid Representations** (Donald Knuth): Rigorous analysis of different representations.

### Unimplemented Variants

- **Pointy-Top Hexagons:** Alternative orientation (point upward). Requires different pixel↔hex formulas.
- **Offset Coordinates:** Alternative to cubic/axial. Less mathematically elegant.
- **Hexagon Rotation:** Not used in SyV-Flet but possible with cubic transformations.

---

## 9. Implementation Notes (Flet)

### Efficient Rendering

```python
# Precalculate pixel positions for each valid hexagon
pixel_cache = {}
for q, r in all_hexagons(R):
    pixel_cache[(q, r)] = hex_to_pixel(q, r, size, center_x, center_y)

# In render loop: only consult cache (O(1))
for hex_coords, pixel_pos in pixel_cache.items():
    draw_hexagon(pixel_pos, size, color)
```

### Click Detection

```python
def on_click(event):
    # Convert click pixels to logical coordinates
    q, r = pixel_to_hex(event.x, event.y, size, center_x, center_y)

    # Verify validity
    if is_valid(q, r, R):
        # Process order/selection
        process_click(q, r)
```

---

## Quick Reference Table

| Operation | Complexity | Use Case |
|-----------|-----------|----------|
| Distance | O(1) | Check if in range |
| Neighbors | O(1) | Find adjacent hexes |
| Line | O(distance) | Visibility, projectiles |
| Ring | O(distance) | Area effects |
| Pixel-Hex | O(1) | Click detection |
| BFS Pathfinding | O(board_size) | Movement validation |
| Flood Fill | O(board_size) | Connectivity check |

---

**END OF DOCUMENT**
