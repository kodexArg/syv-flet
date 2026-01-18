---
name: user-authentication
description: User authentication & account management strategy. MVP: NOT IMPLEMENTED. Hot-seat only. This skill documents the current state and future evolution plan.
allowed-tools: None
---

# User Authentication Strategy

## Current Status: NONE

There is **NO** user authentication system in SyV-Flet. No logins, no passwords, no sessions, no database of users.

## The Solution: Hot-Seat Transitions (Why we don't need Auth)

Since the game operates on a single device with two players (Hot-Seat), we solve "identity" and "secrecy" through **UI State Transitions** rather than cryptographic authentication.

### The Flow
The application manages the game loop through explicit transition screens that act as a "curtain":

1.  **Player 1 Phase**:
    -   Screen: **PLANIFICACIÓN** (Orders are secret).
    -   Player 1 inputs orders. Player 2 must look away.
    -   *Action*: Clicks "Terminate Turn".

2.  **Transition Screen (The Curtain)**:
    -   Screen: **INTERSTITIAL**.
    -   Message: "Pass device to Player 2".
    -   State: No game board visible. Secrets are hidden.

3.  **Player 2 Phase**:
    -   Screen: **PLANIFICACIÓN** (Orders are secret).
    -   Player 2 inputs orders. Player 1 must look away.
    -   *Action*: Clicks "Terminate Turn".

4.  **Execution Phase (Resolution)**:
    -   Screen: **EJECUCIÓN**.
    -   **Auth State**: Unified. Both players watch the screen.
    -   All orders are revealed and resolved simultaneously.
    -   *Action*: Animation completes -> Returns to Step 1 (Reset).

This mechanism ensures the integrity of the "Simultaneous Turn" mechanic without requiring distinct user accounts.
