#!/usr/bin/env python3
"""
Validate bash commands against project standards.
Hook: PreToolUse (Bash)

Validations:
- Warn against using pip (use 'uv add' instead)
- Warn against dangerous commands (rm -rf /, etc.)
- Ensure uv commands follow project conventions
- Suggest better alternatives

Usage: Called automatically by Claude Code before bash execution.
Returns: Exit code 0 (warning only, still execute)
         Exit code 2 (block dangerous command)
"""
import json
import sys
import re


# Patterns that should be warned about
WARNINGS = [
    {
        "pattern": r"pip\s+(install|uninstall|add)",
        "message": "Use 'uv add' or 'uv sync' instead of pip",
        "block": True,
    },
    {
        "pattern": r"python\s+-m\s+pip",
        "message": "Use 'uv add' instead of 'python -m pip'",
        "block": True,
    },
    {
        "pattern": r"python3?\s+-m\s+pip",
        "message": "Use 'uv add' instead of 'pip'",
        "block": True,
    },
    {
        "pattern": r"(sudo\s+)?rm\s+-rf\s+/",
        "message": "Dangerous: Cannot delete system root",
        "block": True,
    },
    {
        "pattern": r"(sudo\s+)?chmod\s+-R\s+777",
        "message": "Insecure: chmod 777 exposes files to everyone",
        "block": False,
    },
    {
        "pattern": r"git\s+push\s+--force",
        "message": "Dangerous: Use '--force-with-lease' instead of '--force'",
        "block": False,
    },
    {
        "pattern": r"git\s+reset\s+--hard",
        "message": "Destructive: Hard reset loses uncommitted work",
        "block": False,
    },
]

# Commands that are allowed despite pattern matches
SAFE_COMMANDS = [
    "uv pip list",  # List packages (read-only)
    "uv pip freeze",  # Freeze packages (read-only)
]


def validate_command(command: str) -> tuple[bool, list[str]]:
    """
    Validate bash command.
    Returns: (should_block, warnings)
    """
    warnings = []
    should_block = False

    # Check safe commands first
    for safe_cmd in SAFE_COMMANDS:
        if command.strip().startswith(safe_cmd):
            return False, []

    # Check each pattern
    for rule in WARNINGS:
        if re.search(rule["pattern"], command):
            warnings.append(rule["message"])
            if rule["block"]:
                should_block = True

    return should_block, warnings


def main():
    """Read tool input and validate command."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")

    if not command:
        sys.exit(0)

    should_block, warnings = validate_command(command)

    if warnings:
        for warning in warnings:
            print(f"⚠ {warning}", file=sys.stderr)

        # Print command for reference
        print(f"  Command: {command}", file=sys.stderr)

        # Block if dangerous
        if should_block:
            print(f"❌ Command blocked (unsafe)", file=sys.stderr)
            sys.exit(2)

    # Exit code 0 = allow command to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
