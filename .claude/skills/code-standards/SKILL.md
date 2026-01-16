---
name: code-standards
description: Code quality, form, and consistency standards. Ensures SOLID principles, coherent practices, and clean architecture. MUST be consulted for all code reviews and implementations.
allowed-tools: Read, Grep, Edit, Bash
---

# Code Standards

When reviewing or writing Python code for SyV-Flet, enforce these standards from `.claude/docs/03-code-standards.md`.

## Mandatory Standards

### 1. S.O.L.I.D. Principles (non-negotiable)
- **Single Responsibility:** One class = one reason to change
- **Open/Closed:** Open for extension, closed for modification
- **Liskov Substitution:** Subclasses must be substitutable
- **Interface Segregation:** Many specific interfaces, not one general
- **Dependency Inversion:** Depend on abstractions, not concretions

### 2. Code Quality
- **Zero-comment policy:** Code must be self-documenting
- **Semantic docstrings ONLY:** Using Pydantic/Protocol docstrings
- **Modern Python 3.13+:** Protocols, Generics, Pattern Matching
- **Type hints on ALL functions and methods**

### 3. Data Validation
- Use **Pydantic V2+** for all data models
- Validate at system boundaries
- Never trust external input
- Always trust internal functions (no excess validation) Avoid try/except blocks unless necessary

### 4. Architecture
- **Hexagonal architecture:** Engine + UI separation
- **Pure game logic:** `/engine` (Flet-agnostic, testable)
- **Flet interface layer:** `/ui` (presentation only)

## Review Checklist

When reviewing code:
- [ ] Single responsibility per class/function
- [ ] All functions have type hints
- [ ] No comments (code self-documents)
- [ ] Pydantic models for data
- [ ] No hardcoded values (use config/constants)
- [ ] Proper error handling
- [ ] Tests pass: `uv run pytest tests/`
- [ ] Formatting: `uv run black src/ tests/`
- [ ] Linting: `uv run ruff check src/ tests/`

## Common Issues

**Issue:** Flet imports in `/engine`
**Fix:** Move to `/ui` or create abstraction

**Issue:** No type hints
**Fix:** Add types for all parameters and return values

**Issue:** Comments explaining code
**Fix:** Rename variables/functions to self-document

**Issue:** Hardcoded values
**Fix:** Extract to constants or config

## Reference Documents

- Architecture: `.claude/docs/01-flet-architecture.md`
- Development Guide: `.claude/docs/02-development-guide.md`
- Code Standards: `.claude/docs/03-code-standards.md`
- Hex Coordinates: `.claude/docs/hexagonal-grid-coordinates.md`
