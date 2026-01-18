---
name: testing-framework
description: Testing approach and practices. Tests are written with Behavior-Driven Development (BDD) using pytest. Quick reference for testing standards.
allowed-tools: Bash, Read
---

# Testing Framework

SyV-Flet testing uses **Behavior-Driven Development (BDD)** with pytest.

---

## Core Principle

Every test describes a **use case**, not implementation details.

```
Test name = User behavior or system outcome
Example: "test_user_can_place_attack_order"
NOT: "test_attack_order_object_creation"
```

---

## Test Organization

```
tests/
├── test_cycle_tap.py           (Tap cycling behavior)
├── test_order_placement.py     (Order mechanics)
├── test_movement_paths.py      (Movement resolution)
├── test_combat_resolution.py   (Combat logic)
├── test_board_state.py         (Board operations)
└── conftest.py                 (Shared fixtures)
```

---

## BDD Approach

Write tests that describe what the user **does** and what **happens**:

- **Given:** Initial game state
- **When:** User performs action
- **Then:** Expected outcome occurs

---

## Running Tests

- Run all tests: `uv run pytest tests/ -v`
- Check coverage: `uv run pytest tests/ --cov=src`
- Run specific test file: `uv run pytest tests/test_cycle_tap.py`

---

## Coverage Target

- **Engine logic:** 80%+ coverage required
- **UI layer:** Focus on critical controllers
- **No coverage for:** Integration stubs, mock setup code

---

## Test Fixtures

Fixtures describe game states, not test utilities:

- `board_empty` – Blank game board
- `player_with_units` – Player with starting units
- `pending_orders` – Pre-populated order pool
- `mid_execution_state` – Game in EJECUCIÓN phase

---

## Assertions

Tests assert **outcomes**, not intermediate states:

- ✓ Correct: `assert order_placed.type == "ATTACK"`
- ✓ Correct: `assert player.available_orders == 2`
- ✗ Wrong: `assert _internal_state_modified == True`

---

## Note

This is a **quick reference** for testing philosophy. Detailed implementation follows BDD conventions: test names are descriptive, test suites are organized by use case, and fixtures represent game states.

For comprehensive pytest documentation, see official pytest docs.
