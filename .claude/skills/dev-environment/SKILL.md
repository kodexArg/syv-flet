---
name: dev-environment
description: Set up and configure the SyV-Flet development environment. Focuses on the `uv` workflow, standard commands, and structural patterns.
allowed-tools: Bash, Read, Write, Edit
---

# SyV-Flet Development Environment

## 1. Core Stack & Prerequisites

*   **Python Engine:** 3.12+ (CPython)
*   **Dependency Manager:** `uv` (Mandatory Replacement for `pip`/`poetry`)
*   **OS:** Linux / macOS / WSL2 (Windows not supported directly)
*   **Testing:** `pytest`
*   **Linting/Formatting:** `ruff` (Lint), `black` (Format)

## 2. The `uv` Workflow Pattern

We use `uv` for everything. Do not use `pip` or `python` directly unless inside a `uv run` context.

### Initialization
```bash
uv sync                 # Install/Sync dependencies from lockfile
uv sync --fresh         # Clean reinstall (nuke .venv)
```

### Execution Cycle
All commands must run through the `uv` context to ensure the correct environment variables and usage of `.venv`.

*   **Run App:** `uv run python -m syv_flet`
*   **Run Tests:** `uv run pytest`
*   **Format:** `uv run black .`
*   **Lint:** `uv run ruff check .`

> **Pattern:** `uv run <command>` is the universal entry point.

## 3. IDE Configuration Logic

Do not hardcode paths. Configure your IDE (VS Code, Neovim, etc.) to respect the project structure.

### VS Code Requirements
1.  **Interpreter:** Point to `${workspaceFolder}/.venv/bin/python`.
2.  **Formatter:** Set `black` as the default formatter.
3.  **Linter:** Enable `ruff`.
4.  **Debug Configuration:**
    *   **Type:** `python`
    *   **Module:** `syv_flet.main` (Entry point)
    *   **Env:** Set `FLET_DEBUG=1` for detailed logs.

### Neovim/Other Requirements
1.  **LSP:** Use `pylsp` or `pyright`.
2.  **Root:** Ensure the working directory is the project root (where `pyproject.toml` lives).

## 4. Environment Variables

Store local overrides in `.env` (gitignored). Provide a `.env.example` for reference.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FLET_DEBUG` | `0` | Enable Flet debug overlay and logging |
| `PYTHONUNBUFFERED` | `1` | Force stdout flushing (critical for container/logs) |
| `HEXSIM_LOG_LEVEL` | `INFO` | App-specific logging verbosity |

## 5. Structural Patterns

The project follows a `src`-based layout to prevent import side-effects.

```text
syv-flet/
├── .venv/                 # Managed by uv
├── src/
│   └── syv_flet/
│       ├── __init__.py
│       ├── main.py        # Entry point (def main(page: ft.Page))
│       ├── engine/        # Pure logic (Domain Layer)
│       └── ui/            # Flet components (Presentation Layer)
├── tests/                 # Mirror of src structure
├── pyproject.toml         # Dependencies & Tool Config
└── uv.lock                # Specific versions truth
```

### Module Resolution
*   **Source Root:** `src/`
*   **Import Pattern:** `from syv_flet.engine import board` (Absolute imports preferred)

## 6. Troubleshooting Logic

*   **"Module Not Found":**
    *   *Cause:* Running `python` directly instead of `uv run python`.
    *   *Fix:* Use `uv run`. verify `PYTHONPATH` includes `src`.

*   **"Import Mismatches":**
    *   *Cause:* `uv.lock` out of sync with `pyproject.toml` or manual pip usage.
    *   *Fix:* `uv sync`

*   **"Visual Glitches (Linux)":**
    *   *Cause:* Wayland/GPU issues with Flet/GTK.
    *   *Fix:* `FLET_DISPLAY_WAYLAND=0` or check dependencies (GStreamer/GTK).
