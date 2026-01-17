---
name: user-authentication
description: User authentication & account management strategy. MVP: NOT IMPLEMENTED. Hot-seat only. This skill documents the current state and future evolution plan.
allowed-tools: None
---

# User Authentication Strategy

**Current Status (MVP):** NOT IMPLEMENTED

---

## MVP Scope: Hot-Seat Multiplayer

The SyV-Flet MVP supports **local multiplayer only** (hot-seat):

- Two players share one device
- No user registration
- No login system
- No persistent user profiles
- No online matchmaking
- No accounts whatsoever

**Example workflow:**
```
Player 1 (local) → clicks "Start Game" → places orders
Player 2 (local) → clicks "Cambiar Jugador" → hides Player 1's orders
Player 2 places orders → executes turn
Loop until game ends
```

---

## What This Means

✓ **Implemented:**
- Game save/load (local file, no user account)

✗ **NOT Implemented (never in MVP):**
- User registration / signup
- Login / password authentication
- Online accounts
- Persistent player profiles
- Ranked matchmaking
- Friend lists

---

## Future: Network Multiplayer (Post-MVP)

When SyV-Flet evolves to support **remote multiplayer** (player A vs player B over network), this skill will be updated to specify:

- Authentication system (OAuth2 / JWT / custom)
- Backend service (if applicable)
- Session management
- User profiles (if needed)

**This skill will be completely rewritten at that point.**

---

## For AI Assistants

If you are reading this:

- **Do NOT implement login/registration in MVP**
- **Do NOT add authentication middleware**
- **Do NOT create user database schemas**
- **Do NOT add account management UI**

The game is single-device only. Player identities are transient (Player 1 / Player 2 per session).

If requirements change, this skill's header will indicate a new status. Until then: **authentication does not exist in scope.**

---

## File Structure (Empty for MVP)

```
src/syv_flet/
├── auth/                  ← Placeholder (unused in MVP)
│   └── __init__.py
```

This folder exists for future expansion but contains nothing functional.

---

## Related Documentation

- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — System design (no auth layer)
- [PRD.md](../../docs/PRD.md) — Product spec (mentions "single device / hot seat")
- Configuration: [configuration-management skill](../configuration-management/SKILL.md)
