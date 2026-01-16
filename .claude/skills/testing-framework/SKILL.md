---
name: testing-framework
description: Write and run tests using pytest with coverage tracking. Use when creating unit tests, checking code coverage, validating functionality, or ensuring test-driven development.
allowed-tools: Bash, Read, Grep, Write, Edit
---

# SyV-Flet Testing Framework

SyV-Flet uses `pytest` with coverage tracking. **Use `uv`, never pip.**

## Quick Start

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src

# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
```

## Writing Tests

Use this standard structure:

```python
import pytest
from src.syv_flet.engine.board import Board

class TestBoard:
    def setup_method(self):
        """Fixture: runs before each test."""
        self.board = Board(width=8, height=8)

    def test_board_initialization(self):
        """Verify board initializes correctly."""
        assert self.board.width == 8
        assert len(self.board.tiles) == 64

    def test_board_get_tile(self):
        """Test tile retrieval by coordinates."""
        tile = self.board.get_tile(q=0, r=0)
        assert tile is not None

    def test_board_invalid_coordinates(self):
        """Test edge case: invalid coordinates."""
        with pytest.raises(ValueError):
            self.board.get_tile(q=1000, r=1000)
```

## Coverage Goals

- **Target:** 80%+ coverage for `engine/`
- **UI coverage:** Focus on critical controllers
- **Commands:**
  ```bash
  uv run pytest tests/ --cov=src.syv_flet.engine
  uv run pytest tests/ --cov-report=html
  open htmlcov/index.html
  ```

## Common Commands

```bash
# Run specific file
uv run pytest tests/test_board.py -v

# Run specific test class
uv run pytest tests/test_board.py::TestBoard -v

# Run specific test
uv run pytest tests/test_board.py::TestBoard::test_initialization -v

# Run by keyword
uv run pytest tests/ -k "hex" -v

# Run last failed
uv run pytest --lf

# Run failed first
uv run pytest --ff

# Watch mode (requires pytest-watch)
uv run pytest tests/ --watch
```

## Test Organization

```
tests/
├── test_board.py          # Board logic
├── test_units.py          # Unit entities
├── test_combat.py         # Combat mechanics
├── test_compass.py        # Compass logic
├── test_geometry.py       # Math utilities
├── test_ui_controller.py  # UI controllers (mocked Flet)
└── conftest.py            # Shared fixtures
```

## Example: Unit Test with Fixtures

```python
# tests/conftest.py
import pytest
from src.syv_flet.engine.board import Board
from src.syv_flet.engine.units import Unit, UnitType

@pytest.fixture
def board():
    return Board(width=20, height=20)

@pytest.fixture
def unit():
    return Unit(
        id="unit_1",
        faction="team_a",
        type=UnitType.INFANTRY,
        pos=(0, 0)
    )

# tests/test_units.py
def test_unit_takes_damage(unit):
    unit.take_damage(10)
    assert unit.health == 90

def test_unit_dies(unit):
    unit.take_damage(100)
    assert unit.is_alive == False
```

## Debugging Tests

```bash
# Show print statements
uv run pytest tests/test_board.py -v -s

# Drop into debugger on failure
uv run pytest tests/ --pdb

# Show local variables on failure
uv run pytest tests/ -l

# Verbose traceback
uv run pytest tests/ --tb=long
```

## Performance

- **Fast tests:** < 100ms total
- **Slow tests:** Mark with `@pytest.mark.slow` and run separately
  ```python
  @pytest.mark.slow
  def test_pathfinding_large_board():
      ...

  # Run: uv run pytest tests/ -m "not slow"
  ```

## CI/CD Integration

See `.claude/docs/02-development-guide.md` for Git hooks and CI setup.

Before commit:
```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run black src/ tests/
uv run ruff check --fix src/ tests/
```
