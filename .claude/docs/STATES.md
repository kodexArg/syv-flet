# SyV-Flet - Enumeraciones de Estado

**Documento de Referencia:** Define todos los enums que controlan el estado del juego.

---

## 1. Fases de Juego

### GamePhase (str, Enum)

Controla el flujo lógico del turno (agnóstico a pantalla/visibilidad).

```python
class GamePhase(str, Enum):
    PLANNING = "planning"      # Jugadores colocan órdenes (privado)
    EXECUTION = "execution"    # Resolución simultánea (compartido)
    RESET = "reset"            # Limpieza y cambio de turno (silencioso)
```

| Fase | Duración | Entrada | Salida |
|------|----------|---------|--------|
| **PLANNING** | Variable (1-N jugadores) | Inicial O post-RESET | EXECUTION (ambos listos) |
| **EXECUTION** | Automática (resolución) | Post-PLANNING ambos | RESET (auto-transición) |
| **RESET** | Automática (limpieza) | Post-EXECUTION | PHASE_TRANSITION screen |

---

## 2. Pantalla / Visibilidad

### ScreenState (str, Enum)

**NEW:** Controla QUÉ pantalla se renderiza (orthogonal a GamePhase).

```python
class ScreenState(str, Enum):
    PHASE_TRANSITION = "phase_transition"  # Dark overlay + centered button (privacy gate)
    GAMEPLAY = "gameplay"                  # Interactive grid + controls
```

| Pantalla | Cuándo | Propósito | Qué se Ve |
|----------|--------|-----------|-----------|
| **PHASE_TRANSITION** | Entre turnos | Barrera privacidad + anunciador | Nada (overlay oscuro) |
| **GAMEPLAY** | Durante PLANNING/EXECUTION | Grid interactivo | Unidades/órdenes (filtrado) |

**Nota:** `ScreenState` es orthogonal a `GamePhase`. Ejemplo: `GamePhase=EXECUTION` + `ScreenState=GAMEPLAY` = ejecución simultánea visible.

---

## 3. Unidades

### UnitType (str, Enum)

```python
class UnitType(str, Enum):
    INFANTRY = "infantry"     # Soldado básico (1 strength)
    OFFICER = "officer"       # Líder (2 strength, genera pool de órdenes)
    CAPTAIN = "captain"       # Comandante (3 strength, genera pool de órdenes)
```

**Pool de Órdenes:** `(Officers × 1) + (Captains × 3)` = total disponible por turno.

### UnitStatus (str, Enum)

Máquina de estados de unidades durante EXECUTION y POST-RESET.

```python
class UnitStatus(str, Enum):
    ACTIVE = "active"         # Operativa, puede recibir órdenes
    ROUTED = "routed"         # En desbandada (tras combate perdedor)
    RETREAT = "retreat"       # En retirada ordenada (siguiente turno)
    ELIMINATED = "eliminated" # Muerta (fuera del tablero)
```

**Transiciones:**

```
ACTIVE ──[lost combat]──> ROUTED
ROUTED ──[next turn]───> RETREAT
RETREAT ──[next turn]──> ELIMINATED
Any ────[5-Hex Rule]───> ELIMINATED (si aislada)
```

---

## 4. Terreno

### TerrainType (str, Enum)

```python
class TerrainType(str, Enum):
    GRASS = "grass"            # Transitable (default)
    WATER = "water"            # Impasable (obstáculo)
```

**MVP incluye:** GRASS, WATER.
**Futuro:** SAND, MOUNTAIN, SNOW (extensión).

---

## 5. Órdenes

### OrderType (str, Enum)

```python
class OrderType(str, Enum):
    ATTACK = "attack"          # Ataca hex adyacente (ocupado enemigo)
    MOVE = "move"              # Movimiento multi-hex (max 3 waypoints)
    DEPLOY = "deploy"          # Deploy seguro (1 hex, sin combate)
    DEFEND = "defend"          # Defensa (+bonificación en hex origen)
    CANCEL = "cancel"          # Cancela orden previa (devuelve a pool)
```

| Orden | Costo | Rango | Efecto |
|-------|-------|-------|--------|
| ATTACK | 1 orden | Adyacente (1 hex) | Combate determinista |
| MOVE | 1 orden | Multi-hex (≤3) | Movimiento con riesgo |
| DEPLOY | 1 orden | Cercano (1 hex) | Movimiento seguro |
| DEFEND | 0 órdenes | Origen | +defensa, sin mover |
| CANCEL | Devuelve 1 | Origen | Invalida orden previa |

---

## 6. Transiciones de Estado (Mapa Mental)

### FSM Completo (7 Estados)

```
START
  ↓
[PHASE_TRANSITION] "Iniciar Partida"
  ↓ click
[GAMEPLAY] PLANNING (active_player=0, privado)
  ↓ "Siguiente Jugador"
[PHASE_TRANSITION] "Siguiente Jugador"
  ↓ click
[GAMEPLAY] PLANNING (active_player=1, privado)
  ↓ "Siguiente Jugador" [both done?]
[GAMEPLAY] EXECUTION (ambos, compartido)
  ↓ auto (post-ejecución)
[HIDDEN] RESET (limpieza silenciosa)
  ↓ auto
[PHASE_TRANSITION] "Nuevo Turno"
  ↓ click
[GAMEPLAY] PLANNING (active_player=0, turn_number++)
  [repeat]
```

---

## 7. Combinaciones Válidas (Invariantes)

| GamePhase | ScreenState | Validez | Nota |
|-----------|-------------|---------|------|
| PLANNING | PHASE_TRANSITION | ✓ | Transición entre jugadores |
| PLANNING | GAMEPLAY | ✓ | Jugador activo colocando órdenes |
| EXECUTION | GAMEPLAY | ✓ | Ejecución simultánea visible |
| EXECUTION | PHASE_TRANSITION | ✗ | Nunca debe ocurrir |
| RESET | GAMEPLAY | ✓ | Limpieza interna (no visible) |
| RESET | PHASE_TRANSITION | ✓ | Transición a siguiente turno |

---

## 8. Referencia Rápida

```python
# Crear GameState con enums
from enum import Enum

game_state = GameState(
    current_phase=GamePhase.PLANNING,
    screen_state=ScreenState.GAMEPLAY,
    active_player=0,
    # ...
)

# Validar combo
if game_state.current_phase == GamePhase.PLANNING:
    # Acepta input solo si ScreenState == GAMEPLAY
    if game_state.screen_state == ScreenState.GAMEPLAY:
        # handle_click(...)
        pass
```
