---
name: cycle-tap-mechanism
description: Conceptual guide to the cycle-tap order system. Explains order types, state transitions, and movement path mechanics. Use when understanding order placement logic, tap sequences, or designing order resolution.
allowed-tools: Read
---

# Cycle-Tap Order Mechanism

This skill explains the **conceptual foundation** of SyV-Flet's order placement system. No code here—only the logic, sequences, and order mechanics.

---

## 1. Order Categories

Orders in SyV-Flet are grouped into three functional categories:

### Category A: Static Orders (Defensive/Null)

**DEFENSE**
- Origin hex: Marked as defended
- Effect: Increases strength on this hex during combat
- Duration: Entire execution phase
- Path: No path (single hex only)
- Cycle behavior: Selected when player taps origin a 2nd time

**CANCEL**
- Origin hex: Order removed, placement resources returned
- Effect: Nullifies any pending orders on this unit
- Duration: Immediate
- Path: No path (single hex only)
- Cycle behavior: Selected when player taps origin a 3rd time (after DEFENSE)

### Category B: Attack Orders (Commitment)

**ATTACK**
- Origin hex: Source of attack
- Destination hex: Target (must be adjacent)
- Effect: Creates a "contested hex"—both units claim it, resolution determines occupant
- Duration: Until execution phase resolves
- Path: Direct line, 1 hex only (adjacent)
- Cycle behavior: Selected by cycling taps on adjacent hex (1st click on adjacent)

### Category C: Movement Orders (Path-Based)

**MOVEMENT**
- Origin hex: Starting position
- Path: Sequence of adjacent hexes (default max 3 hexes deep)
- Destination: Final hex in path
- Effect: Unit traverses path, stops at destination or blocked point
- Duration: Entire path executes in sequence during execution phase
- Cycle behavior: Selected by cycling taps on adjacent hex (2nd click on adjacent)
- Constraint: Can be interrupted by combat or obstacles

**DEPLOY**
- Origin hex: Starting position
- Path: Shorter safe movement (default max 1 hex, no combat risk)
- Destination: Final hex in path
- Effect: Unit moves safely without engaging in combat
- Duration: Path executes guaranteed during execution phase
- Cycle behavior: Selected by cycling taps on adjacent hex (1st click on adjacent if adjacent is 2 hexes away or more)
- Constraint: Safe but limited range

---

## 2. Tap Cycling: State Sequence

The tap sequence determines which order type is placed. Think of it as a **turn-based state machine** where each hex has an implicit state.

### Sequence 1: Origin Selection (Initial Tap)

```
STATE: IDLE
  ↓ (Player taps hex with friendly unit)
STATE: ORIGIN_SELECTED
  Visual: Double outline, faction color
  System: Neighbors now active for tapping
```

**Precondition:** Hex must contain a friendly unit
**Action:** Marks hex as origin, enables adjacent hexes for interaction

---

### Sequence 2: Origin Cycling (Taps on Same Origin)

```
STATE: ORIGIN_SELECTED
  ↓ (Player taps origin again)
STATE: DEFENSE_PENDING
  Visual: Shield icon on origin
  System: All adjacent orders cleared

STATE: DEFENSE_PENDING
  ↓ (Player taps origin a 3rd time)
STATE: IDLE (canceled)
  Visual: All highlights removed
  System: Origin and neighbors deselected, order returned to pool
```

**Behavior:**
- 1st tap on origin → Activate
- 2nd tap on origin → Switch to DEFENSE
- 3rd tap on origin → Cancel everything

**Cost:**
- Each state change in the origin cycle costs nothing (reversible until confirmed)

---

### Sequence 3: Adjacent Hexes (Attack & Movement Paths)

Once origin is selected, adjacent hexes enter a **path-building state**.

#### Subcase A: Adjacent Hex for ATTACK

```
STATE: ORIGIN_SELECTED + ADJACENT_HEX_HOVER
  ↓ (Player taps adjacent hex 1st time)
STATE: ATTACK_ORDER_PLACED
  Visual: Sword icon on adjacent, origin outlined
  System: Order confirmed, origin remains active
  Cost: 1 order consumed from pool
```

**Precondition:** Adjacent hex must be passable
**Action:** Creates ATTACK order from origin to adjacent
**Next Step:**
- Player can tap another adjacent → creates another ATTACK
- Player can tap origin → clears all adjacent orders, switch to DEFENSE
- Player can tap same adjacent again → cycles to MOVEMENT

#### Subcase B: Movement Path (Multi-Hex)

```
STATE: ATTACK_ORDER_PLACED or ADJACENT_EMPTY
  ↓ (Player taps same adjacent hex 2nd time)
STATE: MOVEMENT_PATH_STARTED
  Visual: Path highlighted, first destination marked
  System: Adjacent neighbors to this new hex now active
  Cost: 0 (path building is free until confirmed)
```

**Behavior:**
The adjacent hex becomes a **waypoint** in the path. User can now:

**Option 1: Continue Moving (Chain Adjacent Clicks)**

```
STATE: MOVEMENT_PATH_STARTED (at waypoint 1)
  ↓ (Player taps hex adjacent to waypoint 1)
STATE: MOVEMENT_PATH_EXTENDED
  Waypoint 2 marked
  Adjacent to waypoint 2 now active
  Cost: Still 0 (building phase)
```

**Constraints:**
- Default max 3 waypoints for MOVEMENT (not counting origin)
- Can't revisit same hex in path
- Can't move backward to origin

**Option 2: End Movement (Confirm Path)**

```
STATE: MOVEMENT_PATH_EXTENDED (at waypoint N)
  ↓ (Player taps origin)
STATE: MOVEMENT_ORDER_PLACED
  Visual: Path drawn from origin → waypoint 1 → waypoint 2 → ... → waypoint N
  Path icon on final destination
  System: Order confirmed, movement complete
  Cost: 1 order consumed from pool
```

**Option 3: Backtrack (Shrink Path)**

```
STATE: MOVEMENT_PATH_EXTENDED (at waypoint 2)
  ↓ (Player taps origin)
STATE: MOVEMENT_ORDER_PLACED (at waypoint 1)
  Path shortened to just origin → waypoint 1
  Waypoint 2 removed
  Adjacent to waypoint 1 now active again
  Cost: Still 0 (confirmation not yet made)
```

---

## 3. Order Type Placement Logic (Decision Tree)

Here's the conceptual flow for determining which order gets placed based on tap sequence:

```
PLAYER TAPS HEX (x, y)

├─ Is origin_hex == NULL?
│  ├─ YES: Is there a friendly unit at (x, y)?
│  │  ├─ YES → STATE: ORIGIN_SELECTED ✓
│  │  └─ NO → Silent fail, stay IDLE
│  │
│  └─ NO: Is (x, y) == origin_hex?
│     ├─ YES: Is there an adjacent order active?
│     │  ├─ YES (ATTACK/MOVEMENT placed)
│     │  │   └─ Clear adjacent orders, STATE: DEFENSE_PENDING ✓
│     │  └─ NO (nothing placed yet)
│     │      └─ If defense_pending, STATE: IDLE (cancel all) ✓
│     │      └─ Else, STATE: DEFENSE_PENDING ✓
│     │
│     └─ NO: Is (x, y) adjacent to origin_hex?
│        ├─ YES: What's the current adjacent state at (x, y)?
│        │  ├─ EMPTY
│        │  │  └─ Check origin order type
│        │  │     ├─ DEFENSE: Can't place adjacent orders → Fail
│        │  │     └─ ORIGIN: Can place ATTACK ✓ (goto ATTACK_ORDER_PLACED)
│        │  │
│        │  ├─ ATTACK_PLACED (previous tap)
│        │  │  └─ Cycle to MOVEMENT_PATH_START ✓
│        │  │
│        │  └─ MOVEMENT_PATH (active path building)
│        │     └─ Is (x, y) adjacent to last_waypoint?
│        │        ├─ YES: Extend path, add (x, y) as new waypoint ✓
│        │        └─ NO: Invalid, fail silently
│        │
│        └─ NO: Click outside valid area → Fail silently

```

---

## 4. Movement Path Mechanics (Detailed)

Movement orders have special behavior because they can span multiple hexes. Understanding path mechanics is critical.

### Path Building Phase (Order Construction)

A movement path is built **incrementally**. The user doesn't specify the full path upfront; instead, they click successive adjacent hexes to extend it.

```
Origin: (0, 0) [unit position]
  ↓
Click hex (1, 0) adjacent to origin
  → Waypoint 1: (1, 0)
  → Adjacent to (1, 0) now available
  ↓
Click hex (1, 1) adjacent to waypoint 1
  → Waypoint 2: (1, 1)
  → Adjacent to (1, 1) now available
  ↓
Click hex (0, 1) adjacent to waypoint 2
  → Waypoint 3: (0, 1)
  → No more adjacent clicks (max 3 waypoints)
  ↓
Click origin (0, 0) to confirm
  → Order complete: MOVEMENT from (0, 0) → (1, 0) → (1, 1) → (0, 1)
```

**Key Insight:** Each click adds ONE waypoint. Waypoints must be adjacent to the previous waypoint (or origin for first click).

### Path Costs (Order Pool)

- **Building phase:** Free (no cost)
- **Confirmation phase:** 1 order from pool
- **Cancellation:** Returns order to pool (if already confirmed)

### DEPLOY vs MOVEMENT (Distance-Based Default)

The system suggests order type based on distance:

```
If tapping adjacent hex is 1 step away:
  → Suggest DEPLOY (safe, short)
  → Player can tap again to change to MOVEMENT

If tapping adjacent hex is 2+ steps away:
  → Suggest MOVEMENT (longer path)
  → Player can tap to change to DEPLOY (if reverting)
```

This is just a **default**—tap cycling overrides it.

---

## 5. Path Constraints & Validation

Not all sequences are valid. The system validates paths at confirmation time.

### Valid Path Conditions

- **No loops:** Same hex can't appear twice
- **Connected:** Each waypoint adjacent to previous
- **Forward only:** Can't return to origin mid-path (only at end to confirm)
- **Length limit:** MOVEMENT max 3 waypoints, DEPLOY max 1 waypoint
- **Passable:** All hexes in path must be valid (not water, not out of bounds)
- **No unit collision:** Can't path through enemy-occupied hexes (except destination if ATTACK)

### Invalid Paths (Silent Fail)

```
Path: (0,0) → (1,0) → (1,0)  ← Loop (same hex twice)
Result: 2nd click on (1,0) ignored, stays in MOVEMENT_PATH state

Path: (0,0) → (1,0) → (3,3)  ← Not adjacent
Result: Click on (3,3) ignored, highlighting skipped

Path: (0,0) → (1,0) → WATER → (1,1)  ← Impassable in middle
Result: Click on WATER is ignored
```

---

## 6. Order Pool & Consumption

Each player has a fixed order pool (officers + captain = N orders).

### Pool State Tracking

```
Player A
  ├─ Total orders: 4  (1 officer + 3 captain)
  ├─ Used: 2
  │  ├─ Order 1: ATTACK (0,0) → (1,0)
  │  └─ Order 2: MOVEMENT (2,2) → (2,3) → (2,4)
  └─ Available: 2
```

### When Orders Consume Pool

- **Confirmation tap:** Takes 1 from available pool
- **Cancellation (3rd tap on origin):** Returns 1 to available pool
- **Changing adjacent order type:** No additional cost (same slot)

### When Pool Is Exhausted

```
If available == 0:
  ├─ Player can still use DEFENSE (no cost)
  ├─ Player can still use CANCEL to free orders
  └─ Player cannot place ATTACK, MOVEMENT, or DEPLOY
```

---

## 7. Hot Seat: Player Switching & Order Secrecy

### Switching Players

When "Cambiar Jugador" button tapped:

```
BEFORE SWITCH:
  Player A's orders visible (opacity 0.4) on canvas
  Player A's order pool: visible with counter

BUTTON CLICK:
  ├─ All Player A orders erased from canvas
  ├─ origin_hex = NULL (reset tap state)
  ├─ adjacent_orders = {} (clear path building)
  ├─ current_player = Player B
  └─ Canvas shows blank grid (clean slate)

AFTER SWITCH:
  Player B sees only their order pool counter
  Player B can place new orders
  Player A's previous orders NOT visible to Player B (secret)
```

### Order Visibility During PLANIFICACIÓN

```
During Player A's turn:
  ├─ Player A sees their orders (faintly, opacity 0.4)
  └─ Player A does NOT see Player B's previous orders

During Player B's turn:
  ├─ Player B sees their orders (faintly, opacity 0.4)
  └─ Player B does NOT see Player A's orders
```

### Order Visibility During EJECUCIÓN

```
Both players see ALL orders:
  ├─ Player A's orders (full opacity 1.0, team color A)
  ├─ Player B's orders (full opacity 1.0, team color B)
  └─ Path visualizations, attack indicators, etc.
```

---

## 8. Tap Cycling Quick Reference

| Hex Type | 1st Tap | 2nd Tap | 3rd Tap | Notes |
|----------|---------|---------|---------|-------|
| **Origin** | ORIGIN_SELECTED | DEFENSE_PENDING | CANCEL (IDLE) | Resets adjacent |
| **Adjacent (empty)** | ATTACK_ORDER | MOVEMENT_PATH_START | (continues path) | Origin must be active |
| **Adjacent (attack)** | — | MOVEMENT_PATH_START | (extends path) | Cycling changes type |
| **Adjacent (path)** | — | (extends path) | (continues extending) | Max 3 waypoints |

---

## 9. State Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ IDLE (no origin selected)                              │
│ • Grid blank, no highlights                            │
│ • All hexes clickable (those with friendly units)      │
│                                                         │
└────────────────┬────────────────────────────────────────┘
                 │ [click origin with unit]
                 ↓
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ ORIGIN_SELECTED                                        │
│ • Origin hex: double outline, faction color           │
│ • Adjacent hexes: light outline, semi-transparent     │
│ • Can tap origin again OR tap adjacent                │
│                                                         │
└────┬──────────────────────────────────────┬────────────┘
     │ [tap origin 2nd time]                │ [tap adjacent 1st time]
     ↓                                       ↓
┌──────────────────┐          ┌─────────────────────────────┐
│ DEFENSE_PENDING  │          │ ATTACK_ORDER_PLACED         │
│ • Shield icon    │          │ • Sword icon on destination │
│ • Adjacent clear │          │ • Can repeat on other adjs  │
│ • Can cancel     │          │ • Origin remains active     │
└────┬─────────────┘          └──────┬──────────────────────┘
     │ [tap origin 3rd]               │ [tap same adjacent 2nd]
     ↓                                ↓
┌──────────────┐          ┌────────────────────────────────┐
│ IDLE (reset) │          │ MOVEMENT_PATH_BUILDING         │
└──────────────┘          │ • Path drawn with waypoints   │
                          │ • Can extend path (tap adjacent)
                          │ • Can backtrack (tap origin)   │
                          │ • Confirm by tapping origin    │
                          └──────┬─────────────────────────┘
                                 │ [tap origin to confirm]
                                 ↓
                          ┌────────────────────────────────┐
                          │ MOVEMENT_ORDER_PLACED          │
                          │ • Full path visible            │
                          │ • Order consumed from pool     │
                          │ • Origin becomes selectable    │
                          │   for new orders               │
                          └────────────────────────────────┘
```

---

## 10. Examples

### Example 1: Simple ATTACK

```
Player A's turn:
1. Tap hex (2, 3) with own infantry unit
   → ORIGIN_SELECTED at (2, 3)

2. Tap adjacent hex (3, 3)
   → ATTACK_ORDER_PLACED: ATTACK (2,3) → (3,3)
   → Pool: 4 → 3 available

3. Tap "Cambiar Jugador"
   → All orders hidden, Player B's turn begins
```

### Example 2: Multi-Hex MOVEMENT

```
Player B's turn:
1. Tap hex (5, 5) with own cavalry unit
   → ORIGIN_SELECTED at (5, 5)

2. Tap adjacent hex (5, 6)
   → ATTACK_ORDER_PLACED: ATTACK (5,5) → (5,6)
   → Pool: 4 → 3 available

3. Tap same hex (5, 6) again
   → MOVEMENT_PATH_BUILDING: path = [(5,6)]
   → Adjacent to (5, 6) now active

4. Tap hex (4, 6) adjacent to last waypoint
   → path = [(5,6), (4,6)]
   → Adjacent to (4, 6) now active

5. Tap hex (4, 5) adjacent to (4, 6)
   → path = [(5,6), (4,6), (4,5)]
   → Max 3 waypoints reached for MOVEMENT

6. Tap origin (5, 5) to confirm
   → MOVEMENT_ORDER_PLACED: (5,5) → (5,6) → (4,6) → (4,5)
   → Pool: 3 → 2 available
```

### Example 3: DEFENSE + Cancellation

```
Player A's turn:
1. Tap hex (0, 0) with own officer
   → ORIGIN_SELECTED at (0, 0)

2. Tap origin (0, 0) again
   → DEFENSE_PENDING: shield icon on (0, 0)

3. Realize mistake, tap origin (0, 0) third time
   → CANCEL: All orders cleared, back to IDLE
   → Pool unchanged

4. Tap "Cambiar Jugador" to end turn without placing orders
```

---

## 11. Summary

The cycle-tap mechanism is a **two-tier system**:

1. **Tier 1: Origin Cycling** (single hex, 3-state)
   - Determines if unit will defend or cancel

2. **Tier 2: Adjacent Cycling** (multi-hex, order-building)
   - Determines order type and path for ATTACK/MOVEMENT/DEPLOY

All interactions are **non-destructive until confirmation**—players can change their mind at any point before the "Cambiar Jugador" button is pressed.

Orders are **secret during PLANIFICACIÓN** (opacity 0.4) and **public during EJECUCIÓN** (opacity 1.0, both factions visible).
