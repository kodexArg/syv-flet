# Code Standard - SyV-Flet

**Version:** 1.0
**Date:** January 16, 2026
**Target:** Python 3.13+
**Level:** Developers (Claude Code)
**Criticality:** MAXIMUM — This document defines OBLIGATIONS, not suggestions.

---

## Preface

This project is in MVP phase but will scale significantly. Architecture must enable harmonious growth without destructive refactoring. All code written today must support 3-5x more complexity without structural changes.

**The enemy is accumulated technical debt.** Every line counts.

---

## 1. Fundamental Principles (Non-Negotiable)

### 1.1. S.O.L.I.D. Mandatory

| Principle | Application in SyV-Flet | Verification |
|-----------|----------------------|--------------|
| **S**ingle Responsibility | Each class: ONE purpose. `Board` only grid, `Unit` only entity. | Can this class change for only one reason? If 2+, split. |
| **O**pen/Closed | Open for extension, closed for modification. Stable engine, extensible UI. | Can I add new Order type without touching `combat.py`? |
| **L**iskov Substitution | Subclasses replace parents without breaking behavior. | Can `Infantry` replace `Unit` without failures? |
| **I**nterface Segregation | Specific interfaces, not fat ones. `Drawable`, `Movable`, not `GameEntity`. | Does client need all methods from this interface? |
| **D**ependency Inversion | Depend on abstractions, not concretions. Inject `Board`, not `SpecificBoard`. | Can I swap implementation without touching client? |

**Iterative Verification:** Every 200 new lines, review that each class has single responsibility.

### 1.2. Scalability Over Completeness

- Don't add features "just in case"
- Architecture that allows future features WITHOUT prior changes
- Use `Protocol` from `typing` for future contractuality
- Think: "What if we have 10 Order types instead of 7?"

---

## 2. File Structure (Extreme Minimalism)

### 2.1. Rule: One → One Purpose

❌ **BAD:**
```
src/syv-flet/engine/
  ├── models.py          ← Mixes Unit + Order + Board + State
  ├── utils.py           ← Distance, random, logging
  └── all.py             ← EVERYTHING in one file
```

✅ **GOOD:**
```
src/syv-flet/engine/
  ├── board.py           ← Board and hex topology (ONLY)
  ├── units.py           ← Unit, Officer, Captain (ONLY)
  ├── orders.py          ← Order enum, order contracts (ONLY)
  ├── combat.py          ← Combat resolution (ONLY)
  ├── state.py           ← GameState and turn machine (ONLY)
  └── types_.py          ← Shared TypeAlias, Protocol (OPTIONAL)
```

### 2.2. Criteria for New File

**Create file ONLY if:**

1. ✅ Module will be imported from 2+ places
2. ✅ Has 50+ lines of code
3. ✅ Clearly violates Single Responsibility in current module
4. ✅ Is part of library that can be reused

**DON'T create file if:**

- ❌ Only 2-3 utility functions (add to existing module)
- ❌ Class used only by owner (inner class)
- ❌ Generic "helpers" or "utils" (discriminate + distribute)

---

## 3. Code Style (Python 3.13+)

### 3.1. ZERO Comments (Zero-Comment Policy)

**Code must be self-explanatory.**

❌ **BAD:**
```python
def distance(a, b):
    # Calculate Manhattan distance in hexagons
    aq, ar = a
    bq, br = b
    # Convert to cubic
    as_ = -aq - ar
    bs_ = -bq - br
    # Distance = sum of differences
    return (abs(aq - bq) + abs(ar - br) + abs(as_ - bs_)) // 2
```

✅ **GOOD:**
```python
def distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Hexagonal Manhattan distance between two axial coordinates."""
    aq, ar = a
    bq, br = b
    as_ = -aq - ar
    bs_ = -bq - br
    return (abs(aq - bq) + abs(ar - br) + abs(as_ - bs_)) // 2
```

### 3.2. Docstrings (Semantic, Minimal)

**Location:** Public classes and functions only.

**Format:** One line, present tense, no implementation details.

❌ **BAD:**
```python
class Unit:
    """
    This class represents a military unit in the game.
    It has properties like position, health, type, etc.
    Methods include taking damage, moving, etc.
    """
    pass

def move_unit(u, q, r):
    """
    This function moves a unit from current to new position.
    It first validates, then updates internal state,
    and finally notifies observers.
    """
    pass
```

✅ **GOOD:**
```python
class Unit:
    """Military unit with position, state, and combat capability."""
    pass

def move_unit(unit: Unit, target: tuple[int, int]) -> None:
    """Relocate unit to target hexagon, validating movement rules."""
```

**ALLOWED docstring information:**
- WHAT it DOES (active verb)
- WHAT it RETURNS (if not obvious)
- WHAT it REQUIRES (if preconditions)

**FORBIDDEN information:**
- HOW it does it (implementation)
- Examples (except complex cases)
- Commit history

### 3.3. Type Hints (Mandatory)

**Python 3.13 allows `type` without importing `Type`:**

✅ **GOOD (Py3.13+):**
```python
from collections.abc import Sequence, Callable

def find_path(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Find shortest path between two hexagons."""
    pass

def callback_factory(cb: Callable[[int], bool]) -> Callable[[], None]:
    """Create a callback wrapper with state."""
    pass

class Observable[T]:
    """Generic observable container."""
    def notify(self, value: T) -> None: ...
```

**Supported in Py3.13:**
- `list[T]`, `dict[K, V]`, `tuple[T, ...]` (no `List` from typing)
- `Sequence`, `Callable` from `collections.abc`
- Generics with `class Foo[T]:`

### 3.4. Explicit Names

Don't use abbreviations except well-known cases.

| ❌ Avoid | ✅ Use |
|---------|--------|
| `u`, `un` | `unit` |
| `pos`, `p` | `position` |
| `q`, `r` | `(q, r)` OK (standard hex notation) |
| `res` | `result` or `resolution` |
| `upd` | `update` |
| `fxn` | `function` |
| `cb` | OK if context is clear (`on_click_callback`) |

---

## 4. Pydantic: Data Structures

**Use Pydantic V2+ for:**
- Automatic validation
- Serialization
- Documentation (schema)
- Type safety

### 4.1. Domain Models

✅ **GOOD:**
```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class UnitType(str, Enum):
    INFANTRY = "infantry"
    OFFICER = "officer"
    CAPTAIN = "captain"

class UnitState(str, Enum):
    ACTIVE = "active"
    ROUTED = "routed"
    RETREATING = "retreating"

class Unit(BaseModel):
    """Military unit with validated attributes."""
    id: str = Field(..., min_length=1)
    faction: str = Field(..., min_length=1)
    type: UnitType
    position: tuple[int, int]
    state: UnitState = Field(default=UnitState.ACTIVE)
    health: int = Field(default=100, ge=0, le=100)

    @field_validator("health")
    @classmethod
    def valid_health(cls, v: int) -> int:
        return max(0, min(100, v))

    model_config = {"frozen": False}
```

### 4.2. Validated Orders

```python
from typing import Protocol

class OrderData(BaseModel):
    """Base validated order structure."""
    unit_id: str
    target: tuple[int, int] | None = None
    modifier: int = Field(default=0, ge=-2, le=2)

class AttackOrder(OrderData):
    """Attack order targeting adjacent hexagon."""
    type: str = "attack"
    force_modifier: int = Field(default=1)

class MoveOrder(OrderData):
    """Movement order with distance constraint."""
    type: str = "move"
    max_distance: int = Field(default=3, ge=1, le=5)
```

### 4.3. Avoid Unnecessary Pydantic

**DON'T use Pydantic if:**
- Only need dict (use TypedDict)
- Internal, no validation needed
- Complex methods (use dataclass)

```python
from typing import TypedDict

class HexData(TypedDict):
    """Internal hex state (no validation needed)."""
    terrain: str
    occupant_id: str | None
    order: str | None
```

---

## 5. Modern Design Patterns (Python 3.13+)

### 5.1. Protocol (Structural Subtyping)

Instead of inheritance, use implicit interfaces:

✅ **GOOD:**
```python
from typing import Protocol

class Drawable(Protocol):
    """Anything that can be rendered."""
    def draw(self, canvas: "Canvas") -> None: ...

class Movable(Protocol):
    """Anything that can move."""
    def move_to(self, position: tuple[int, int]) -> None: ...

class Unit:
    """Military unit implementing Drawable and Movable."""
    def draw(self, canvas: Canvas) -> None: ...
    def move_to(self, position: tuple[int, int]) -> None: ...

def render_all(objects: list[Drawable]) -> None:
    """Render all drawable objects (works with any type implementing Drawable)."""
    for obj in objects:
        obj.draw()
```

**Advantage:** Unit does NOT explicitly inherit. If it implements methods, it IS `Drawable`. (Typed duck typing.)

### 5.2. Generics (Python 3.13)

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Observable(Generic[T]):
    """Generic observable container."""
    def __init__(self, value: T):
        self._value = value
        self._listeners: list[Callable[[T], None]] = []

    def subscribe(self, callback: Callable[[T], None]) -> None:
        """Add listener to value changes."""
        self._listeners.append(callback)

    def set_value(self, value: T) -> None:
        """Update value and notify listeners."""
        self._value = value
        for listener in self._listeners:
            listener(value)

class GameState(Observable[GamePhase]):
    """Specialization: game phase observable."""
    pass

phase = GameState(GamePhase.ORDER_INPUT)
phase.subscribe(lambda p: print(f"Phase changed to {p}"))
phase.set_value(GamePhase.RESOLUTION)
```

### 5.3. Pattern Matching (Python 3.10+)

```python
def handle_order(order: OrderData) -> None:
    """Process order based on type."""
    match order.type:
        case "attack":
            resolve_attack(order)
        case "move":
            validate_movement(order)
        case "support":
            apply_support(order)
        case _:
            raise ValueError(f"Unknown order type: {order.type}")
```

### 5.4. Context Managers for Resources

```python
from contextlib import contextmanager

@contextmanager
def board_snapshot(board: Board):
    """Capture and restore board state (for undo)."""
    saved_state = board.serialize()
    try:
        yield board
    finally:
        board.restore(saved_state)

# Usage
with board_snapshot(board):
    execute_turn(board)
```

---

## 6. Scalable Architecture (Open/Closed)

### 6.1. Extension Without Modification

**Problem:** Add order type → modify `combat.py`

**Solution: Registry Pattern**

```python
from typing import Callable, Protocol

class OrderResolver(Protocol):
    """Interface for order resolution."""
    def resolve(self, order: OrderData, state: GameState) -> None: ...

class AttackResolver:
    """Resolve attack orders."""
    def resolve(self, order: OrderData, state: GameState) -> None:
        pass

class MoveResolver:
    """Resolve move orders."""
    def resolve(self, order: OrderData, state: GameState) -> None:
        pass

ORDER_RESOLVERS: dict[str, OrderResolver] = {
    "attack": AttackResolver(),
    "move": MoveResolver(),
}

def register_resolver(order_type: str, resolver: OrderResolver) -> None:
    """Register new order resolver (extensibility)."""
    ORDER_RESOLVERS[order_type] = resolver

def resolve_order(order: OrderData, state: GameState) -> None:
    """Dispatch to appropriate resolver."""
    resolver = ORDER_RESOLVERS.get(order.type)
    if not resolver:
        raise ValueError(f"Unknown order type: {order.type}")
    resolver.resolve(order, state)
```

**Benefit:** Add new Order → create `NewOrderResolver` + `register_resolver()`. ZERO changes to `combat.py`.

### 6.2. Dependency Injection

**Don't hardcode dependencies:**

❌ **BAD:**
```python
class GameController:
    def __init__(self):
        self.board = Board(radius=20)  # Hardcoded
        self.state = GameState()
        self.logger = get_global_logger()
```

✅ **GOOD:**
```python
class GameController:
    """Game coordinator with injectable dependencies."""
    def __init__(
        self,
        board: Board,
        state: GameState,
        logger: Callable[[str], None],
    ):
        self.board = board
        self.state = state
        self.logger = logger
```

**Advantage:** Easy testing, swappable implementations.

### 6.3. Abstract Base Classes for Contracts

```python
from abc import ABC, abstractmethod

class GamePhaseHandler(ABC):
    """Contract for phase processing."""

    @abstractmethod
    def can_handle(self, phase: GamePhase) -> bool:
        """Check if this handler processes the phase."""
        pass

    @abstractmethod
    def execute(self, state: GameState) -> None:
        """Execute phase logic."""
        pass

class OrderInputPhase(GamePhaseHandler):
    """Handle order input phase."""

    def can_handle(self, phase: GamePhase) -> bool:
        return phase == GamePhase.ORDER_INPUT

    def execute(self, state: GameState) -> None:
        pass

class ResolutionPhase(GamePhaseHandler):
    """Handle simultaneous resolution."""

    def can_handle(self, phase: GamePhase) -> bool:
        return phase == GamePhase.RESOLUTION

    def execute(self, state: GameState) -> None:
        pass
```

---

## 7. Modern Operators (Python 3.13+)

### 7.1. Walrus Operator (`:=`)

```python
if (distance := board.distance(unit.position, target)) <= max_movement:
    process_move(unit, target, distance)
```

### 7.2. Match Expressions

```python
def get_unit_strength_modifier(unit: Unit) -> int:
    """Get strength modifier based on unit type."""
    return match unit.type:
        case UnitType.INFANTRY: 1
        case UnitType.OFFICER: 2
        case UnitType.CAPTAIN: 3
```

### 7.3. Union Types (`|`)

```python
def find_unit(board: Board, identifier: str | int | tuple[int, int]) -> Unit | None:
    """Find unit by ID, position, or coordinates."""
    match identifier:
        case str(): return board.find_by_id(identifier)
        case int(): return board.find_by_owner_id(identifier)
        case (q, r): return board.find_at_position((q, r))
        case _: return None
```

### 7.4. Unpacking Improvements

```python
def process_units(*units: Unit, priority_target: Unit | None = None) -> None:
    """Process multiple units with optional priority."""
    match (units, priority_target):
        case ([], _):
            print("No units to process")
        case ([*rest, last], None):
            for unit in rest: process_normal(unit)
            process_priority(last)
        case (_, priority):
            process_priority(priority)
```

---

## 8. Code Verification (Checklist)

Before each commit:

- [ ] **Zero Comments** → Search for `#` (except docstrings and `# type: ignore`)
- [ ] **Docstrings** → Each public function/class has 1-line docstring
- [ ] **Type Hints** → All parameters and returns typed
- [ ] **SOLID** → Each class has single responsibility
- [ ] **Files** → Minimum necessary, no generic utils/helpers
- [ ] **Names** → Explicit, no abbreviations (q,r OK; u,pos no)
- [ ] **Pydantic** → Input data validated
- [ ] **Patterns** → Protocol, Generic, Match where applicable
- [ ] **Scalability** → Can I add feature without changing existing code?

---

## 9. Complete Examples (Before/After)

### 9.1. Example: Board (BAD → GOOD)

❌ **BAD:**
```python
class Board:
    def __init__(self, r):
        self.r = r
        self.hexes = {}  # dict of hexagons

    def valid(self, q, r):
        # Check if (q,r) is on board
        s = -q - r
        return max(abs(q), abs(r), abs(s)) <= self.r

    def neighbors(self, q, r):
        # Return 6 neighbors
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        result = []
        for dq, dr in dirs:
            nq, nr = q + dq, r + dr
            if self.valid(nq, nr):
                result.append((nq, nr))
        return result
```

✅ **GOOD:**
```python
from pydantic import BaseModel, Field

class Board(BaseModel):
    """Hexagonal game board with axial coordinate system."""
    radius: int = Field(..., gt=0, le=50)
    terrain: dict[tuple[int, int], str] = Field(default_factory=dict)

    def is_valid(self, q: int, r: int) -> bool:
        """Check if coordinates are within board bounds."""
        s = -q - r
        return max(abs(q), abs(r), abs(s)) <= self.radius

    def neighbors(self, q: int, r: int) -> list[tuple[int, int]]:
        """Hexagons adjacent to given coordinates."""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q + dq, r + dr) for dq, dr in directions if self.is_valid(q + dq, r + dr)]

    def distance(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        """Manhattan distance between two hexagons."""
        aq, ar = a
        bq, br = b
        as_, bs_ = -aq - ar, -bq - br
        return (abs(aq - bq) + abs(ar - br) + abs(as_ - bs_)) // 2

    model_config = {"frozen": False}
```

### 9.2. Example: Order Resolution (Extensible)

✅ **GOOD (Open/Closed):**
```python
from typing import Protocol
from abc import abstractmethod

class OrderResolver(Protocol):
    """Contract for resolving any order type."""
    def resolve(self, order: OrderData, state: GameState) -> None: ...

class AttackResolver:
    """Resolve attack orders."""
    def resolve(self, order: OrderData, state: GameState) -> None:
        attacker = state.get_unit(order.unit_id)
        if not attacker: raise ValueError("Unit not found")
        target = state.get_unit_at(order.target)
        if not target: raise ValueError("No target at position")

class MoveResolver:
    """Resolve movement orders."""
    def resolve(self, order: OrderData, state: GameState) -> None:
        unit = state.get_unit(order.unit_id)
        if not unit: raise ValueError("Unit not found")
        dist = state.board.distance(unit.position, order.target)
        if dist > 3: raise ValueError("Movement too far")
        unit.position = order.target

class OrderDispatcher:
    """Dispatch orders to appropriate resolvers."""
    def __init__(self, resolvers: dict[str, OrderResolver]):
        self._resolvers = resolvers

    def resolve(self, order: OrderData, state: GameState) -> None:
        """Execute order using registered resolver."""
        resolver = self._resolvers.get(order.type)
        if not resolver: raise ValueError(f"Unknown order: {order.type}")
        resolver.resolve(order, state)

    def register(self, order_type: str, resolver: OrderResolver) -> None:
        """Register new order type (extensibility)."""
        self._resolvers[order_type] = resolver
```

---

## 10. Anti-Patterns (PROHIBITED)

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Godclass (1000+ lines) | Violates S → Split responsibilities | Refactor immediately |
| Circular imports | `engine imports ui imports engine` | Use Protocol, inject dependencies |
| Global state `GLOBAL_BOARD = Board()` | Impossible to test | Pass via constructor |
| Magic numbers `if x > 5: ...` | What does 5 mean? | Constant with name: `MAX_ISOLATED_DISTANCE = 5` |
| Comments explaining "why" | Shouldn't need them | Code + expressive names |
| Bare except `(except:)` | Swallows all errors | Be specific: `except ValueError:` |
| Type `Any` without reason | Loses type checking | Use `Protocol` or `Generic[T]` |

---

## 11. Quick Reference

```python
# Modern Python 3.13+ template
from typing import Protocol, TypeVar, Generic, Callable
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from enum import Enum
from contextlib import contextmanager

T = TypeVar("T")

class MyEnum(str, Enum):
    """Enumeration of values."""
    VALUE_A = "value_a"

class MyProtocol(Protocol):
    """Interface contract."""
    def method(self, x: int) -> str: ...

class MyModel(BaseModel):
    """Data with validation."""
    field: int = Field(default=10, ge=0)
    model_config = {"frozen": False}

class MyGeneric(Generic[T]):
    """Generic container."""
    def __init__(self, value: T): self.value = value

def my_function(x: int, y: str) -> dict[str, int]:
    """Do something semantic."""
    return {"result": x}

@contextmanager
def my_context(resource):
    """Resource management."""
    try:
        yield resource
    finally:
        pass

match value:
    case int(): print("integer")
    case str(): print("string")
    case _: print("other")
```

---

## Conclusion

**This code is:**
- ✅ Scalable: New features without refactor
- ✅ Maintainable: No technical debt, change-agnostic
- ✅ Testeable: Dependency injection, protocols
- ✅ Readable: Explicit names, types, minimal docstrings
- ✅ Modern: Python 3.13+ patterns

**Priorities (in order):**
1. **SOLID principles**
2. **Scalability** (Open/Closed)
3. **Type safety** (complete hints)
4. **Readability** (names, protocols, generics)
5. **Performance** (when bottleneck)

**Success measured by:** How many lines DID I NEED to change to add feature X?
Answer: Few or zero.

---

**CLAUDE CODE INTEGRATION:**

This document is a **skill** that Claude Code must consult before writing Python. Activate:

- When starting `.py` file writing
- When reviewing existing Python code
- When suggesting refactoring
- When designing architecture

**Recommended command:**
```
/code-standards [section]
```

Example: `/code-standards solid` → Shows S.O.L.I.D. application in SyV-Flet.
