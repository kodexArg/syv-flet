#!/usr/bin/env python3
"""
Auto-format Python files using Black and Ruff after edits.
Hook: PostToolUse (Write, Edit)

Usage: Called automatically by Claude Code after file modifications.
"""
import json
import sys
import subprocess
from pathlib import Path


def format_python_file(file_path: str) -> bool:
    """Format a Python file using Black and Ruff. Return True if formatted."""
    path = Path(file_path)

    # Only format Python files in src/ or tests/
    if not file_path.endswith(".py"):
        return True
    if "/src/" not in file_path and "/tests/" not in file_path:
        return True

    try:
        # Format with Black
        result_black = subprocess.run(
            ["black", file_path],
            check=False,
            capture_output=True,
            timeout=10,
        )

        # Lint and auto-fix with Ruff
        result_ruff = subprocess.run(
            ["ruff", "check", "--fix", file_path],
            check=False,
            capture_output=True,
            timeout=10,
        )

        if result_black.returncode == 0 or result_ruff.returncode == 0:
            print(f"✓ Formatted: {path.name}")
            return True

    except subprocess.TimeoutExpired:
        print(f"⚠ Format timeout: {path.name}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠ Format error: {e}", file=sys.stderr)
        return False

    return True


def main():
    """Read tool output and format files."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Format the file
    success = format_python_file(file_path)

    # Exit code 0: continue normally
    # Exit code 2: would block tool (not used for formatting)
    sys.exit(0 if success else 0)


if __name__ == "__main__":
    main()
