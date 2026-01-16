#!/usr/bin/env python3
"""
Prevent modifications to critical files.
Hook: PreToolUse (Write, Edit)

Protected patterns:
- Git internals (.git/)
- Package configuration (pyproject.toml, uv.lock)
- Secrets (.env, credentials, API keys)
- Hooks themselves

Usage: Called automatically by Claude Code before file modifications.
Returns: Exit code 2 to BLOCK the tool call
"""
import json
import sys
from pathlib import Path


PROTECTED_PATTERNS = [
    ".git/",
    ".gitignore",
    "pyproject.toml",
    "uv.lock",
    ".env",
    ".env.local",
    ".env.secret",
    "secrets",
    "credentials",
    "API_KEY",
    ".claude/hooks/",  # Don't auto-modify hooks
    ".claude/settings.json",  # Don't auto-modify settings
    "CLAUDE.md",  # Project instructions
]

ALLOW_PATTERNS = [
    ".claude/skills/",  # Skills are meant to be edited
    ".claude/README.md",  # Docs can be updated
    ".claude/docs/",  # Documentation
]


def is_protected(file_path: str) -> bool:
    """Check if file is protected from modification."""
    path = Path(file_path)
    path_str = str(path)

    # Check allow-list first
    for allow_pattern in ALLOW_PATTERNS:
        if allow_pattern in path_str:
            return False  # Not protected (allowed)

    # Check protect-list
    for protected_pattern in PROTECTED_PATTERNS:
        if protected_pattern in path_str:
            return True  # Protected

    return False  # Not protected (allowed)


def main():
    """Read tool input and check for protected files."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = input_data.get("tool_input", {}).get("file_path", "")

    if not file_path:
        sys.exit(0)

    if is_protected(file_path):
        print(f"🔒 Protected file (read-only): {file_path}", file=sys.stderr)
        print(
            f"   To modify, edit directly with your editor or ask explicitly.",
            file=sys.stderr,
        )
        # Exit code 2 = block this tool call
        sys.exit(2)

    # Exit code 0 = allow tool to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
