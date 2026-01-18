# SyV-Flet Build Workflow

**Propósito:** Guía operativa paso a paso para construir el MVP. Este documento orquesta skills, valida progreso, y resuelve problemas comunes.

**Estado:** ACTIVO — Listo para ejecución

---

## Convenciones de Este Documento

```
→ SKILL: /skill-name        # Invoca skill automático
→ CHECK: comando            # Verifica estado antes de continuar
→ FIX: problema → solución  # Troubleshooting inline
→ EXIT: condición           # Criterio de salida de fase
→ NOTE: información         # Aclaración importante
```

---

## Fase 0: Validación del Entorno

**Objetivo:** Confirmar que el sistema está listo para desarrollo.

### 0.1 Verificar Prerrequisitos del Sistema

```bash
python3 --version          # Debe ser 3.12+ (3.13 recomendado)
uv --version               # Debe estar instalado
```

→ FIX: `uv` no encontrado → `curl -LsSf https://astral.sh/uv/install.sh | sh`
→ NOTE: PRD especifica Python 3.13+, pero 3.12 es el mínimo soportado en pyproject.toml

### 0.2 Verificar Dependencia YAML

→ NOTE: El proyecto requiere `pyyaml` para cargar `configs.yaml`. Verificar que está en `pyproject.toml`:

```toml
dependencies = [
    "flet>=0.24.0",
    "loguru>=0.7.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.0",           # REQUERIDO para configs.yaml
]
```

→ FIX: Si falta pyyaml → `uv add pyyaml`

### 0.3 Sincronizar Dependencias

```bash
uv sync
```

→ CHECK: `.venv/` existe y contiene packages
→ FIX: Error de lockfile → `uv lock --upgrade`

### 0.4 Verificar Imports Críticos

```bash
uv run python -c "import flet; import pydantic; import loguru; import yaml; print('OK')"
```

→ SKILL: `/dev-environment` para troubleshooting avanzado
→ EXIT: Todos los imports exitosos (incluyendo yaml)

---

## Fase 1: Configuración Base

**Objetivo:** Establecer la infraestructura de configuración centralizada.

### 1.1 Crear configs.yaml

→ SKILL: `/configuration-management`

Crear archivo `configs.yaml` en raíz del proyecto. **Usar estructura completa de `example-config.yaml`:**

```yaml
# configs.yaml - Single Source of Truth
# Estructura sincronizada con .claude/skills/configuration-management/example-config.yaml

game:
  board:
    radius: 20                        # 3*R*(R+1) + 1 = 1,261 hexes

  rules:
    movement:
      max_path_waypoints: 3           # Max hexes en MOVE (sin contar origen)
      max_support_distance: 5         # Regla 5 Hexágonos
    combat:
      tie_behavior: "static"          # Empate: unidades estáticas
    orders:
      max_order_history: 500          # FIFO deque limit

ui:
  hex_sizes:
    desktop_hd: 64                    # > 1920px
    laptop: 56                        # > 1280px
    tablet: 48                        # > 768px
    mobile: 40                        # < 768px

  faction_colors:
    player_1: "#2196F3"               # Azul
    player_2: "#F44336"               # Rojo
    neutral: "#CCCCCC"                # Gris (hover)
    highlight: "#FFEB3B"              # Amarillo (selección)

  visibility:
    planning_own_orders: 0.4          # Ghost mode
    planning_opponent_orders: 0.0     # Oculto
    execution_all_orders: 1.0         # Visible

  phase_transition:
    overlay_color: "#000000"
    overlay_opacity: 0.95
    button_text:
      start: "Iniciar Partida"
      next_player: "Siguiente Jugador"
      new_round: "Nuevo Turno"

  phase_button:
    color: "#4CAF50"
    border_radius: 50
    hover_scale: 1.05

assets:
  hexagons:
    path: "assets/hexagons/Previews/"
    default_terrain: "grass.png"
    obstacle_terrain: "water.png"
  icons:
    path: "assets/icons/PNG/"
    default_size: 64
  fonts:
    path: "assets/fonts/kenney_kenney-fonts/"

display:
  target_fps:
    desktop: 60
    mobile: 30
  canvas:
    static_cache: true
    culling_enabled: true

logging:
  level: "DEBUG"
  directory: "logs/"
  files:
    debug: "debug.log"
    error: "error.log"
    daily_rotation: true
    max_days_retention: 30
```

→ CHECK: `configs.yaml` existe y es YAML válido
→ CHECK: `uv run python -c "import yaml; yaml.safe_load(open('configs.yaml'))"`
→ EXIT: Archivo creado y parseado sin errores

### 1.2 Crear Config Loader

Crear `src/syv_flet/config_loader.py`:

- Cargar YAML al inicio
- Validar keys requeridas
- Exponer como diccionario o dataclass

→ SKILL: `/code-standards` para estructura del loader
→ NOTE: Alternativa type-safe: usar `pydantic-settings` para validación automática
→ EXIT: `uv run python -c "from syv_flet.config_loader import load_config; print(load_config())"` funciona

### 1.3 Configurar Logging Centralizado

→ SKILL: `/logging`

Verificar que `logging_config.py` existe y configura Loguru correctamente.

→ CHECK: Sinks configurados (stderr, debug.log, error.log)
→ CHECK: Rotación configurada según `configs.yaml`
→ EXIT: Logs aparecen en consola y archivos

---

## Fase 2: Estructura de Directorios

**Objetivo:** Crear el árbol de carpetas completo.

→ NOTE: Crear `__init__.py` PRIMERO en cada directorio antes de los módulos.

### 2.1 Crear Árbol Engine

```
src/syv_flet/
├── __init__.py              # Ya existe
├── config_loader.py         # Fase 1.2
├── logging_config.py        # Ya existe
├── main.py                  # Fase 5.7
├── __main__.py              # Fase 5.7 (REQUERIDO para -m)
├── engine/
│   ├── __init__.py          # Exportar clases públicas
│   ├── models/
│   │   ├── __init__.py      # Exportar: GameState, HexData, UnitData, OrderData, enums
│   │   ├── enums.py
│   │   ├── hex_data.py
│   │   ├── unit_data.py
│   │   ├── order_data.py
│   │   └── game_state.py
│   ├── hex_math.py
│   ├── board.py
│   ├── cycle_tap.py
│   ├── resolver.py
│   └── controller.py
```

→ CHECK: Todos los `__init__.py` creados con exports apropiados
→ EXIT: `uv run python -c "from syv_flet.engine.models import GameState, HexData"` no falla

### 2.2 Crear Árbol UI

```
src/syv_flet/
├── ui/
│   ├── __init__.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── phase_transition.py
│   │   └── game_screen.py
│   ├── rendering/
│   │   ├── __init__.py
│   │   ├── hex_renderer.py
│   │   ├── unit_renderer.py     # Renderizado de unidades
│   │   └── order_renderer.py
│   ├── input_handler.py
│   ├── state_binder.py
│   └── assets.py                # Asset loader (Fase 6.2)
```

→ CHECK: Estructura UI completa
→ EXIT: Importaciones básicas funcionan

### 2.3 Crear Árbol Tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidos
├── engine/
│   ├── __init__.py
│   ├── test_models.py       # Tests de Pydantic models
│   ├── test_hex_math.py
│   ├── test_board.py
│   ├── test_cycle_tap.py
│   ├── test_resolver.py
│   ├── test_controller.py   # Tests del GameController
│   └── test_integration.py  # Tests E2E del engine
└── ui/
    ├── __init__.py
    └── test_screens.py
```

→ SKILL: `/testing-framework` para estructura de fixtures
→ NOTE: Estructura nested (`tests/engine/`) coincide con `src/syv_flet/engine/`
→ EXIT: `uv run pytest --collect-only` no muestra errores

---

## Fase 3: Modelos de Datos (Pydantic)

**Objetivo:** Definir todos los modelos de dominio con validación estricta.

### 3.1 Definir Enums

→ SKILL: `/state-machine`

Crear `src/syv_flet/engine/models/enums.py`:

```python
from enum import Enum

class GamePhase(str, Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    RESET = "reset"

class ScreenState(str, Enum):
    PHASE_TRANSITION = "phase_transition"
    GAMEPLAY = "gameplay"

class TerrainType(str, Enum):
    GRASS = "grass"
    WATER = "water"

class UnitType(str, Enum):
    INFANTRY = "infantry"
    OFFICER = "officer"
    CAPTAIN = "captain"

class UnitStatus(str, Enum):
    ACTIVE = "active"
    ROUTED = "routed"
    RETREAT = "retreat"
    ELIMINATED = "eliminated"

class OrderType(str, Enum):
    ATTACK = "attack"
    MOVE = "move"
    DEPLOY = "deploy"
    DEFEND = "defend"
    CANCEL = "cancel"
```

→ CHECK: Enums importables
→ EXIT: Validación de tipos funciona

### 3.2 Definir HexData

Crear `src/syv_flet/engine/models/hex_data.py`:

- Campos: `terrain`, `occupant_id`, `last_order_id`, `attributes`
- Invariante: máximo 1 unidad por hex

→ EXIT: Modelo serializable a JSON

### 3.3 Definir UnitData

Crear `src/syv_flet/engine/models/unit_data.py`:

- Campos: `unit_id`, `owner`, `unit_type`, `position`, `status`
- Validador: `owner in {0, 1}`
- Validador: `unit_id` es string único

→ NOTE: `unit_id` es REQUERIDO para indexar en diccionario de GameState
→ EXIT: Transiciones de estado validadas

### 3.4 Definir OrderData

Crear `src/syv_flet/engine/models/order_data.py`:

- Campos: `order_id`, `unit_id`, `order_type`, `coords`, `turn`, `executed`
- Validador: coords según order_type
- Validador: `order_id` es string único

→ NOTE: `order_id` es REQUERIDO para indexar en diccionario de GameState
→ EXIT: Órdenes serializables

### 3.5 Definir GameState

→ SKILL: `/state-machine`

Crear `src/syv_flet/engine/models/game_state.py`:

- Campos core: `map`, `units`, `orders`, `current_phase`, `screen_state`, `active_player`, `turn_number`
- Campos ephemeral: `selected_hex`, `order_path`, `phase_transition_text`
- Diccionarios indexados: `units: dict[str, UnitData]`, `orders: dict[str, OrderData]`

→ CHECK: GameState es la raíz única de estado
→ EXIT: `GameState()` se puede instanciar con defaults

### 3.6 Tests de Modelos

→ SKILL: `/testing-framework`

Crear `tests/engine/test_models.py` con tests BDD:

```python
def test_given_valid_coords_when_creating_hex_then_succeeds():
    ...

def test_given_invalid_owner_when_creating_unit_then_raises():
    ...

def test_given_unit_without_id_when_creating_then_raises():
    ...
```

→ CHECK: `uv run pytest tests/engine/test_models.py`
→ EXIT: 100% de tests de modelos pasan

---

## Fase 4: Motor Hexagonal

**Objetivo:** Implementar toda la matemática y lógica del tablero.

### 4.1 Implementar Hex Math

→ SKILL: `/hex-grid-math`

Crear `src/syv_flet/engine/hex_math.py`:

```python
from typing import Iterator

def neighbors(q: int, r: int) -> list[tuple[int, int]]: ...
def distance(a: tuple[int, int], b: tuple[int, int]) -> int: ...
def hex_to_pixel(
    q: int,
    r: int,
    size: float,
    center_x: float = 0.0,
    center_y: float = 0.0
) -> tuple[float, float]: ...
def pixel_to_hex(
    x: float,
    y: float,
    size: float,
    center_x: float = 0.0,
    center_y: float = 0.0
) -> tuple[int, int]: ...
def round_hex(frac_q: float, frac_r: float) -> tuple[int, int]: ...
def is_valid(q: int, r: int, radius: int) -> bool: ...
def all_hexagons(radius: int) -> Iterator[tuple[int, int]]: ...
def line_hex(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]: ...
def bfs_path(start: tuple, end: tuple, is_walkable: callable) -> list | None: ...
```

→ NOTE: `center_x/y` son offsets para centrar el grid en el viewport
→ CHECK: Todas las funciones son puras (sin side effects)
→ FIX: Errores de redondeo → Revisar fórmula round_hex (usar método cubic)
→ EXIT: Tests de distance y neighbors pasan

### 4.2 Tests Hex Math Exhaustivos

→ SKILL: `/testing-framework`

Crear `tests/engine/test_hex_math.py` con mínimo 50 casos:

- Vecinos del centro (0,0) → 6 vecinos
- Vecinos de borde (20, 0) → menos de 6 vecinos válidos
- Distancias conocidas: distance((0,0), (1,0)) == 1
- Conversiones pixel↔hex roundtrip
- Validación de hexes fuera del radio

→ CHECK: `uv run pytest tests/engine/test_hex_math.py -v`
→ EXIT: 100% tests pasan, coverage >95%

### 4.3 Implementar Board Generation

Crear `src/syv_flet/engine/board.py`:

```python
def generate_board(radius: int) -> dict[tuple[int, int], HexData]: ...
def validate_connectivity(board: dict) -> bool: ...
def count_hexagons(radius: int) -> int:
    return 3 * radius * (radius + 1) + 1  # R=20 → 1,261
```

- Generar 1,261 hexágonos (R=20)
- Terrain default: GRASS
- Verificar sin islas (flood fill)

→ CHECK: Board contiene exactamente `3*R*(R+1)+1` hexes
→ EXIT: Board generado y conectado

### 4.4 Implementar Cycle-Tap Logic

→ SKILL: `/cycle-tap-mechanism`

Crear `src/syv_flet/engine/cycle_tap.py`:

Estados del FSM (referencia completa en skill):
- `IDLE` → ninguna selección
- `ORIGIN_SELECTED` → unidad seleccionada
- `DEFENSE_PENDING` → defensa preparada
- `ATTACK_ORDER_PLACED` → ataque confirmado
- `MOVEMENT_PATH_BUILDING` → construyendo path
- `MOVEMENT_ORDER_PLACED` → movimiento confirmado

Transiciones según tap sequences definidas en skill.

→ FIX: Transición incorrecta → Revisar diagrama Section 9 del skill
→ EXIT: Todos los tap sequences producen órdenes correctas

### 4.5 Implementar Turn Resolver

Crear `src/syv_flet/engine/resolver.py`:

```python
def resolve_turn(state: GameState) -> GameState: ...
```

Secuencia de resolución:
1. Procesar MOVEs (BFS pathfinding, detección de colisiones)
2. Procesar ATTACKs (comparación de fuerzas, determinista)
3. Aplicar Regla 5 Hexágonos (eliminar unidades aisladas)
4. Marcar órdenes como `executed: True`

→ CHECK: Resolución es determinista (misma entrada = misma salida)
→ EXIT: Tests de combate y movimiento pasan

### 4.6 Implementar Game Controller

→ SKILL: `/state-machine`

Crear `src/syv_flet/engine/controller.py`:

```python
class GameController:
    def __init__(self, state: GameState): ...
    def handle_click(self, q: int, r: int) -> None: ...
    def handle_origin_tap(self, q: int, r: int) -> None: ...
    def handle_adjacent_tap(self, q: int, r: int) -> None: ...
    def advance_phase(self) -> None: ...
    def switch_player(self) -> None: ...
    def get_state(self) -> GameState: ...
```

- Orquesta cycle_tap, resolver, y transiciones
- Respeta la Visibility Matrix del state-machine
- Delega todo el estado a GameState (Controller es stateless)

→ CHECK: Controller no tiene estado propio (delega a GameState)
→ EXIT: Flujo PLANNING→EXECUTION→RESET→PLANNING funciona

### 4.7 Tests Integración Engine

Crear `tests/engine/test_integration.py`:

- Test de partida completa (3 turnos)
- Test de empate (ambas unidades estáticas)
- Test de Regla 5 Hexágonos
- Test de privacy (órdenes ocultas entre jugadores)

→ SKILL: `/testing-framework` para fixtures complejos
→ EXIT: Tests de integración pasan

---

## Fase 5: Capa UI (Flet)

**Objetivo:** Renderizar el juego y capturar input.

### 5.1 Implementar Phase Transition Screen

→ SKILL: `/ux-ui-flet-rendering`

Crear `src/syv_flet/ui/screens/phase_transition.py`:

- Overlay negro (opacity 0.95 de `configs.yaml`)
- Botón centrado con texto dinámico:
  - `"Iniciar Partida"` (inicio)
  - `"Siguiente Jugador"` (entre turnos PLANNING)
  - `"Nuevo Turno"` (post-RESET)
- Responsive a breakpoints

→ CHECK: Screen bloquea visibilidad completamente
→ EXIT: Botón dispara callback de avance

### 5.2 Implementar Hex Renderer

→ SKILL: `/hex-grid-flet-rendering`

Crear `src/syv_flet/ui/rendering/hex_renderer.py`:

- Dibujar hexágonos flat-top en Canvas
- Cachear grid estático (draw once)
- Viewport culling (solo hexes visibles)
- Usar `center_x/y` para centrar grid

→ FIX: Hexágonos desalineados → Verificar `hex_to_pixel` usa mismos center offsets
→ EXIT: Grid de 1,261 hexes renderiza correctamente

### 5.3 Implementar Unit Renderer

→ SKILL: `/hex-grid-flet-rendering`

Crear `src/syv_flet/ui/rendering/unit_renderer.py`:

- Renderizar unidades según UnitType (iconos distintos)
- Colores por faction (player_1: azul, player_2: rojo)
- Filtrar según Visibility Matrix en PLANNING

→ CHECK: Unidades del oponente NO visibles en PLANNING
→ EXIT: Unidades renderizan con iconos y colores correctos

### 5.4 Implementar Order Renderer

→ SKILL: `/hex-grid-flet-rendering`

Crear `src/syv_flet/ui/rendering/order_renderer.py`:

- Renderizar iconos (sword=ATTACK, arrow=MOVE, shield=DEFENSE)
- Paths de movimiento como líneas conectadas
- Opacity: 0.4 en PLANNING (ghost), 1.0 en EXECUTION
- Filtrar según Visibility Matrix

→ CHECK: PLANNING muestra solo órdenes del jugador activo
→ EXIT: EXECUTION muestra todas las órdenes

### 5.5 Implementar Input Handler

Crear `src/syv_flet/ui/input_handler.py`:

- Capturar taps en canvas via GestureDetector
- Convertir pixel→hex via `pixel_to_hex` (con center offsets)
- Delegar a GameController

→ FIX: Clicks no detectados → Verificar GestureDetector cubre todo el canvas
→ EXIT: Taps se convierten a coordenadas correctas

### 5.6 Implementar State Binder

Crear `src/syv_flet/ui/state_binder.py`:

- Observar cambios en GameState (polling o callback)
- Re-renderizar solo componentes afectados (dirty rects)
- Trigger update en: selection change, order placed, phase change

→ CHECK: UI se actualiza automáticamente con cambios de estado
→ EXIT: Cambio de fase actualiza pantalla

### 5.7 Implementar Game Screen

→ SKILL: `/ux-ui-flet-rendering`

Crear `src/syv_flet/ui/screens/game_screen.py`:

- Componer: HexRenderer + UnitRenderer + OrderRenderer + InputHandler + Overlay
- Z-order correcto (static → dynamic → interaction → UI)
- Responsive layout según breakpoints
- Botón "Siguiente Jugador" visible SOLO en PLANNING

→ CHECK: Todas las capas se renderizan en orden correcto
→ EXIT: Screen interactivo funcionando

### 5.8 Implementar Entry Points

Crear `src/syv_flet/main.py`:

```python
import flet as ft
from syv_flet.engine.controller import GameController
from syv_flet.engine.models import GameState

def main(page: ft.Page):
    page.title = "SyV-Flet"
    # Initialize controller, screens, bindings
    ...

if __name__ == "__main__":
    ft.app(target=main)
```

Crear `src/syv_flet/__main__.py` (REQUERIDO para `python -m`):

```python
from syv_flet.main import main
import flet as ft

ft.app(target=main)
```

→ CHECK: `uv run python -m syv_flet` lanza la aplicación
→ EXIT: Aplicación abre sin errores

---

## Fase 6: Assets

**Objetivo:** Cargar y cachear recursos visuales.

### 6.1 Verificar Inventario de Assets

→ SKILL: `/assets-manager`

```bash
ls -la assets/hexagons/Previews/ | wc -l    # Espera ~74
ls -la assets/icons/PNG/ | head             # Verificar estructura
ls -la assets/fonts/                        # Verificar fonts
```

→ FIX: Assets faltantes → Descargar de kenney.nl
→ EXIT: Todos los assets requeridos presentes

### 6.2 Implementar Asset Loader

Crear `src/syv_flet/ui/assets.py`:

- Precargar hexagon tiles al startup
- Cache in-memory (dict path→Image)
- Lazy-load iconos menos frecuentes
- Paths desde `configs.yaml`

→ CHECK: No hay stutter en primer render
→ EXIT: Assets cargados en <2 segundos

---

## Fase 7: Integración y Testing

**Objetivo:** Verificar que todo funciona junto.

### 7.1 Test End-to-End Manual

Ejecutar gameplay loop completo:

1. Iniciar partida (botón "Iniciar Partida")
2. P1 coloca órdenes (tap origin → tap adjacent)
3. P1 presiona "Siguiente Jugador"
4. Phase Transition Screen aparece
5. P2 coloca órdenes
6. P2 presiona "Siguiente Jugador"
7. EXECUTION muestra resolución (todas las órdenes visibles)
8. RESET aplica limpieza (Regla 5 Hexágonos)
9. Phase Transition Screen con "Nuevo Turno"
10. Vuelta a PLANNING P1

→ FIX: Pantalla no actualiza → Revisar state_binder callbacks
→ EXIT: Loop completo sin crashes

### 7.2 Tests Automatizados Completos

```bash
uv run pytest tests/ --cov=src/syv_flet --cov-report=term-missing
```

→ SKILL: `/testing-framework`
→ CHECK: Coverage >80% en engine, >60% en UI
→ EXIT: Todos los tests pasan

### 7.3 Code Review

→ SKILL: `/code-standards`

Verificar:

- [ ] SOLID principles aplicados
- [ ] Type hints en TODAS las funciones y métodos
- [ ] Zero magic numbers (todo en configs.yaml)
- [ ] Zero comments (código autodocumentado)
- [ ] Pydantic models con validación estricta
- [ ] No `print()` statements (usar logger)
- [ ] No imports de Flet en `/engine`

→ CHECK: `uv run black src/ tests/ --check`
→ CHECK: `uv run ruff check src/ tests/`
→ EXIT: Code review aprobado

---

## Fase 8: Performance y Polish

**Objetivo:** Optimizar y pulir la experiencia.

### 8.1 Profiling de Rendering

```bash
uv run python -m cProfile -o profile.stats -m syv_flet
```

→ CHECK: 60 FPS en desktop, 30 FPS en mobile
→ FIX: Frame drops → Verificar canvas caching está activo

### 8.2 Responsive Testing

Probar en todos los breakpoints:

- Desktop HD: >1920px (hex_size: 64)
- Laptop: >1280px (hex_size: 56)
- Tablet: >768px (hex_size: 48)
- Mobile: <768px (hex_size: 40)

→ FIX: Layout roto → Ajustar breakpoints en configs.yaml
→ EXIT: UI funcional en todas las resoluciones

---

## Fase 9: Validación MVP

**Objetivo:** Confirmar que el MVP cumple el PRD.

### 9.1 Checklist de Criterios de Aceptación

Verificar contra PRD Sección 6:

- [ ] Tablero R=20 generado (1,261 hexes conectados)
- [ ] Input pixel→hex funcional en todas las resoluciones
- [ ] Privacidad hot-seat:
  - [ ] Phase Transition Screen bloquea visibilidad
  - [ ] Cada jugador ve SOLO sus unidades/órdenes en PLANNING
  - [ ] Botón "Siguiente Jugador" gate-keeps transición
- [ ] Resolución simultánea visible en EXECUTION
- [ ] Empates = unidades estáticas (no eliminación)
- [ ] Regla 5 Hexágonos aplicada en RESET
- [ ] Cycle-tap completo:
  - [ ] Tap origin → selección
  - [ ] Tap origin 2x → DEFENSE
  - [ ] Tap origin 3x → CANCEL
  - [ ] Tap adjacent → ATTACK
  - [ ] Tap adjacent 2x → MOVEMENT path
  - [ ] Tap origin para confirmar path

→ EXIT: Todos los criterios marcados ✓

### 9.2 Verificar Exclusiones

Confirmar que NO está implementado:

- [ ] Save/Load (estado volátil)
- [ ] Multiplayer online
- [ ] Persistencia de configuración
- [ ] Undo/Replay

→ EXIT: MVP limpio sin features fuera de scope

---

## Troubleshooting Global

### "ModuleNotFoundError: syv_flet"

**Causa:** Ejecutando python directamente sin uv
**Fix:** Usar `uv run python -m syv_flet`

### "ModuleNotFoundError: yaml"

**Causa:** Falta dependencia pyyaml
**Fix:** `uv add pyyaml` y luego `uv sync`

### "Flet visual glitches en Linux"

**Causa:** Problemas Wayland/GPU
**Fix:** `FLET_DISPLAY_WAYLAND=0 uv run python -m syv_flet`

### "Flet no muestra debug info"

**Causa:** FLET_DEBUG no activado
**Fix:** `FLET_DEBUG=1 uv run python -m syv_flet`

### "Tests fallan con import errors"

**Causa:** PYTHONPATH no incluye src/
**Fix:** `uv run pytest` (uv configura paths automáticamente)

### "Pydantic ValidationError en modelos"

**Causa:** Datos inválidos al instanciar modelos
**Fix:** Verificar tipos y valores contra el schema del modelo

### "Hexágonos no se alinean"

**Causa:** Error en hex_to_pixel o center offsets inconsistentes
**Fix:** Verificar que `center_x/y` son iguales en render e input

### "Clicks no detectan hex correcto"

**Causa:** Error en pixel_to_hex o round_hex
**Fix:** Añadir logs de debug: `logger.debug(f"Click: ({x},{y}) → Hex: ({q},{r})")`

### "Órdenes no aparecen"

**Causa:** Visibility filtering incorrecto
**Fix:** Verificar `active_player` y `current_phase` antes de render

### "Canvas no responde a taps (mobile)"

**Causa:** GestureDetector no cubre área completa
**Fix:** Verificar que GestureDetector tiene `expand=True`

---

## Invocación de Skills por Fase

| Fase | Skills Primarios | Skills de Soporte |
|------|------------------|-------------------|
| 0 | `/dev-environment` | — |
| 1 | `/configuration-management`, `/logging` | `/code-standards` |
| 2 | — | `/code-standards` |
| 3 | `/state-machine` | `/testing-framework`, `/code-standards` |
| 4 | `/hex-grid-math`, `/cycle-tap-mechanism`, `/state-machine` | `/testing-framework` |
| 5 | `/ux-ui-flet-rendering`, `/hex-grid-flet-rendering` | `/assets-manager` |
| 6 | `/assets-manager` | — |
| 7 | `/testing-framework`, `/code-standards` | — |
| 8 | `/ux-ui-flet-rendering` | — |
| 9 | — | — |

---

## Notas de Ejecución

1. **Secuencial hasta Fase 4:** Las fases 0-4 son prerrequisitos estrictos
2. **Paralelo en Fase 5-6:** UI y Assets pueden desarrollarse simultáneamente
3. **Testing continuo:** Ejecutar `uv run pytest` después de cada sub-fase
4. **Git commits:** Commit al completar cada fase → `/git-workflow`
5. **`__init__.py` primero:** Siempre crear `__init__.py` antes de módulos en nuevos directorios

---

**Estado del Documento: REVISADO Y CORREGIDO**

Correcciones aplicadas:
- ✓ Añadida dependencia pyyaml
- ✓ Añadido __main__.py para -m
- ✓ Añadidos test_models.py, test_controller.py, test_integration.py
- ✓ Añadidos unit_id y order_id a modelos
- ✓ Corregida firma hex_to_pixel con center offsets
- ✓ Sincronizado configs.yaml con example-config.yaml
- ✓ Unificado nombre botón a "Siguiente Jugador"
- ✓ Completados estados cycle-tap
- ✓ Añadido breakpoint Laptop
- ✓ Añadido unit_renderer.py
- ✓ Expandido troubleshooting
- ✓ Notas sobre __init__.py y orden de creación

Siguiente paso: Aprobar este workflow antes de comenzar implementación.
