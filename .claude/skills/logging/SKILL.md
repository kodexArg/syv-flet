# Logging Strategy & Observability

## Philosophy (WHY)
The logging system is the nervous system of the application. In a future multiplayer environment (potentially containerized via Docker), uncontrolled output (stdout/stderr) or poor file management can lead to catastrophic failures:
- **Disk exhaustion**: Unrotated logs filling the container filesystem.
- **Buffer overflows**: Excessive `print` statements clogging the I/O streams.
- **Lost Context**: Errors without stack traces or user state make debugging impossible.

Therefore, we treat logging as a critical infrastructure component, not just a debugging tool.

## Technical Specification (WHAT)
We use **Loguru** as the exclusive logging engine (as defined in `REQUIREMENTS.md`). It is chosen for:
1.  **Thread-safe** logging (critical for Flet/Asyncio).
2.  **Automatic Rotation & Retention** (prevents "exploding dockers" by managing file sizes).
3.  **Exception Catching**: Use of `@logger.catch` to ensure robustness.

## Implementation Guidelines

### 1. No `print()` allowed
- Development artifacts (`print`) must never reach production code.
- They bypass the rotation/filtering logic and risk destabilizing the container runtime environment.

### 2. Configuration
- The logging config must be **centralized** (Single Source of Truth).
- Config must define:
    - **Sinks**: Console (STDERR) for immediate feedback, File for persistence.
    - **Levels**: Tunable via `configs.yaml`.
    - **Rotation**: Required (e.g., 10 MB or Daily) to ensure resource limits are respected.

### 3. Usage Pattern
- **INFO**: High-level game flow events (Turn start, Game End, Player Connect).
- **DEBUG**: Detailed state transitions (silenced in Production).
- **ERROR**: Handled exceptions that require attention.
- **CRITICAL**: Unrecoverable state corruptions.

### 4. Context (Multiplayer Readiness)
- In a future multiplayer context, simple text logs are insufficient.
- The system must support **Context Injection** (binding `game_id`, `user_id` to the logger context) so that interleaved logs from multiple concurrent sessions can be isolated and analyzed.
