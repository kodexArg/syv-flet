#!/usr/bin/env python3
"""
Validate board implementation against SyV-Flet standards.

Checks:
- No Flet imports in engine/
- Proper separation of concerns
- Hex coordinate validity
- All functions have type hints
- Basic architecture compliance

Run: python .claude/skills/board-implementation/scripts/validate-board.py
"""
import ast
import sys
from pathlib import Path
from typing import Optional


class ValidationError:
    """Single validation error."""

    def __init__(self, severity: str, message: str, file: Optional[str] = None):
        self.severity = severity  # "error", "warning", "info"
        self.message = message
        self.file = file

    def __str__(self):
        prefix = {"error": "❌", "warning": "⚠", "info": "ℹ"}[self.severity]
        if self.file:
            return f"{prefix} {self.file}: {self.message}"
        return f"{prefix} {self.message}"


def check_no_flet_in_engine() -> list[ValidationError]:
    """Engine must not import from flet."""
    errors = []
    engine_path = Path("src/syv_flet/engine")

    if not engine_path.exists():
        return [ValidationError("warning", "src/syv_flet/engine/ not found")]

    for py_file in engine_path.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                    else:
                        module = node.names[0].name if node.names else ""

                    if "flet" in module or "ft" in module:
                        errors.append(
                            ValidationError(
                                "error",
                                f"Flet import in engine: {module}",
                                str(py_file),
                            )
                        )
        except Exception as e:
            errors.append(
                ValidationError(
                    "warning", f"Parse error in {py_file.name}: {e}", str(py_file)
                )
            )

    return errors


def check_type_hints() -> list[ValidationError]:
    """Functions should have type hints."""
    errors = []
    engine_path = Path("src/syv_flet/engine")

    if not engine_path.exists():
        return []

    for py_file in engine_path.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has return type
                    if node.returns is None and node.name != "__init__":
                        errors.append(
                            ValidationError(
                                "warning",
                                f"Missing return type hint: {node.name}()",
                                str(py_file),
                            )
                        )

                    # Check if parameters have type hints
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != "self":
                            errors.append(
                                ValidationError(
                                    "warning",
                                    f"Missing type hint: parameter '{arg.arg}' in {node.name}()",
                                    str(py_file),
                                )
                            )

        except Exception as e:
            errors.append(
                ValidationError(
                    "warning", f"Parse error in {py_file.name}: {e}", str(py_file)
                )
            )

    return errors


def check_hex_operations() -> list[ValidationError]:
    """Verify hexagonal coordinate operations exist."""
    errors = []
    board_path = Path("src/syv_flet/engine/board.py")

    if not board_path.exists():
        return [ValidationError("warning", "board.py not found")]

    try:
        with open(board_path) as f:
            content = f.read()

        required_methods = ["is_valid", "neighbors", "distance"]
        for method in required_methods:
            if f"def {method}" not in content:
                errors.append(
                    ValidationError(
                        "warning", f"Board.{method}() not implemented", str(board_path)
                    )
                )

    except Exception as e:
        errors.append(ValidationError("warning", f"Cannot read board.py: {e}"))

    return errors


def check_tests_exist() -> list[ValidationError]:
    """Verify tests exist for board."""
    errors = []
    test_path = Path("tests/test_board.py")

    if not test_path.exists():
        return [
            ValidationError("warning", "tests/test_board.py not found - add tests")
        ]

    return []


def main():
    """Run all validations."""
    print("Validating SyV-Flet board implementation...\n")

    all_errors = []

    # Run checks
    all_errors.extend(check_no_flet_in_engine())
    all_errors.extend(check_type_hints())
    all_errors.extend(check_hex_operations())
    all_errors.extend(check_tests_exist())

    if not all_errors:
        print("✅ All validations passed!")
        sys.exit(0)

    # Print results
    has_errors = False
    for error in all_errors:
        print(str(error))
        if error.severity == "error":
            has_errors = True

    print()

    if has_errors:
        print("❌ Validation failed (errors found)")
        sys.exit(1)
    else:
        print("⚠ Validation passed with warnings")
        sys.exit(0)


if __name__ == "__main__":
    main()
