# SyV-Flet - Product Requirements Document (PRD)

**Versión:** 1.1
**Fecha:** 18 de Enero, 2026
**Plataforma:** PC (Linux/Windows) & Mobile (Android)
**Modelo de Distribución:**
- **MVP:** Single Device / Hot Seat (local)
- **Futuro:** Multijugador online vía API REST (servidor cloud)

---

## 1. Visión del Producto

Un juego de estrategia por turnos simultáneos (WEGO) 1v1 sobre un tablero hexagonal determinista llamado "Subordinación y Valor" (o simplemente "SyV"). La resolución de conflictos es completamente determinista basada en la comparación de fuerzas.

### Evolución del Producto

| Fase | Modelo | Descripción |
|------|--------|-------------|
| **MVP** | Hot Seat Local | Dos jugadores en el mismo dispositivo, turnos alternados |
| **v2.0** | Multijugador Online | Servidor cloud recibe órdenes vía API, resuelve turno, devuelve estado |

La arquitectura de datos está diseñada para soportar ambos modelos sin refactoring. El motor lógico es agnóstico al origen de las órdenes (UI local o API remota).

---

## 2. Stack Tecnológico

* **Lenguaje:** Python 3.12+ (3.13+ recommended)
* **Framework UI:** Flet (v0.24.0+)
* **Motor de Renderizado:** `flet.canvas` (Skia Engine via Flutter)
* **Empaquetado:** `flet build` (APK, Linux AppImage/Executable)
* **Gestión de Estado:** Hash Maps interconectados (ver Sección 7)
* **Logging:** Loguru (configuración centralizada en `src/syv-flet/utils/logger.py`)
* **Dependencias Externas:** Loguru (logging); ninguna para lógica de negocio

---

## 2.1. Sistema de Logging

**Centralización:** Todos los logs se persisten en `logs/` (rotación automática).

**Niveles:**
- `debug.log` — Traza de ejecución (DEBUG+)
- `error.log` — Errores solamente (ERROR+)
- `YYYY-MM-DD.log` — Rotación diaria (INFO+)
- `STDERR` — Emitido simultáneamente en color (todos los niveles)

**Configuración:** Variable de entorno `DEBUG=True|False` (default: True en desarrollo).

---

## 3. Mecánica de Juego

### Sistema de Coordenadas
* **Modelo:** Coordenadas cúbicas `(q, r, s)` donde `q + r + s = 0`.
* **Proyección:** Axial `(q, r)` optimizada para memoria.
* **Orientación:** **Flat-Top** (lado plano arriba).
    ```
          ╱──╲
         │ q,r  │
          ╲──╱
    ```
* **Tablero:** Radio R=20 (fórmula: `3*R*(R+1) + 1` = 1,261 hexágonos).
* **Adyacencia:** 6 vecinos (Direcciones fijas relativas a ejes Flat-Top).
* **Distancia:** Manhattan hexagonal: `(|q1-q2| + |r1-r2| + |s1-s2|) / 2`.

### Entidades Base
* **Unidades:** Infantry, Officer, Captain
* **Estados:** ACTIVE, ROUTED, RETREAT, ELIMINATED
* **Pool de Órdenes:** `(Officers × 1) + (Captain × 3)`

### Resolución de Turno (Loop Principal)
1. Fase de Movimiento → Colisiones
2. Fase de Combate Determinista (comparación de fuerzas)
   - Ganador: Unidad con mayor fuerza
   - Empate: Ambas unidades se mantienen estáticas (sin cambio)
3. Post-procesado: Transiciones de estado (RETREAT, ROUTED), Limpieza de unidades aisladas (ELIMINATED)

### Regla de los 5 Hexágonos
* Elimina unidades aisladas de sus oficiales (distancia > 5 hexágonos)
* Cálculo de distancia: Manhattan hexagonal

---

## 4. Interfaz de Usuario (Flet)

### 4.1 Filosofía de Diseño: Minimalismo Radical

La UI encarna **minimalismo radical basado en intentionalidad**. No hay elementos decorativos. Cada píxel existe por un propósito táctico.

**Principios:**
* **Vacío Intencionado:** El espacio negativo es protagonista
* **Claridad de Propósito:** Solo 2 elementos de control visibles
* **Foco en lo Essential:** El mapa hexagonal es 95% de la pantalla
* **Feedback Implícito:** Interactividad mediante cambios sutiles (hover, transiciones)

### 4.2 Arquitectura Visual (Hot-Seat con Privacidad)

**Dos pantallas principales:**

**1. Phase Transition Screen** (Barrera de privacidad + Anunciador de fases)
```
┌─────────────────────────────────────┐
│                                     │
│     Dark overlay (0.95 opacity)     │
│                                     │
│        [Centered Button]            │
│   "Iniciar Partida" /               │
│   "Siguiente Jugador" /             │
│   "Nuevo Turno"                     │
│                                     │
└─────────────────────────────────────┘
```
Aparece en:
- Inicio del juego ("Iniciar Partida")
- Entre turnos de orden ("Siguiente Jugador")
- Después de RESET ("Nuevo Turno")

**2. Game Screen** (Juego activo)
```
┌─────────────────────────────────────┐
│     GRILLA HEXAGONAL (95%)          │
│  [Grass default, Water = impasable]  │
│                                     │
│   [Board Icons overlaid on hexs]    │
│                                     │
│     [Interactive nodes on edges]    │
│                                     │
│     [Scrolleable + Zoomeable]       │
└─────────────────────────────────────┘
  [Siguiente Jugador]  (1 button)
```
**En fase PLANNING (privada):**
- Solo unidades + órdenes del jugador activo visible
- Unidades del adversario ocultas
- Dark overlay opcional (oscurece adversarios)

**En fase EXECUTION (compartida):**
- Todas las órdenes de ambos jugadores visibles
- Resolución simultánea mostrada en tiempo real
- Sin botones (auto-ejecución)

**Capas Flet:**
1. **Canvas Static:** Grid hexagonal (dibujado una vez)
2. **Canvas Dynamic:** Unidades y efectos de combate (filtrado por phase+player)
3. **GestureDetector:** Input de coordenadas + órdenes (solo si active_player match)
4. **UI Overlay:** Botón único reutilizable (Phase Transition o Siguiente Jugador)

### 4.3 Elementos Visuales

#### Terreno (Hexagons)
- **Orientación:** **Flat-Top** (Fixed).
- **Default:** `grass.png` (Kenney Hexagon Kit - Previews).
- **Impasable:** `water.png`.
- **Resolución:** 64x64 px (Source), renderizado dinámico.
- **Ubicación:** `assets/hexagons/Previews/`.

#### Iconografía (Board Icons)
- **Biblioteca:** Kenney Board Game Icons (PNG)
- **Uso:** Overlay sobre hexágonos para unidades y puntos de interés
- **Escalado:** Dinámico según zoom
- **Ubicación:** `assets/icons/PNG/`

#### Tipografía
- **Fuente:** Kenney Fonts (versatilidad de estilos)
- **Uso:** Textos de UI (botones, turnos, info)
- **Ubicación:** `assets/fonts/kenney_kenney-fonts/`

### 4.4 Controles de Usuario

#### Botón Único Reutilizable (Phase Transition)
**Ubicación:** `PhaseTransitionScreen` (pantalla oscura, centro)
- **Estilo:** Redondo/almohada (border-radius 50%, shadow suave, cushioned)
- **Color:** Accent color (consistent across all states)
- **Estados de Texto:**
  - "Iniciar Partida" (game start)
  - "Siguiente Jugador" (between PLANNING turns)
  - "Nuevo Turno" (after RESET cleanup)
- **Acción:** Transiciona entre fases (PLANNING P1 → PLANNING P2 → EXECUTION → RESET)
- **Comportamiento:** El botón es la ÚNICA forma de progresar entre fases. Crea barrera de privacidad.

#### Botón "Siguiente Jugador" en GameScreen
**Ubicación:** Durante fase PLANNING
- **Estilo:** Idéntico al botón de Phase Transition
- **Posición:** Esquina inferior o centro (fixed)
- **Visibilidad:** Solo visible durante PLANNING (oculto en EXECUTION)
- **Acción:** Termina turno del jugador activo → muestra Phase Transition Screen

#### Interactividad de Nodos (Durante PLANNING)
- **Click en Hex:** Selecciona unidad propia / muestra opciones
- **Hover en Arista:** Resalta posible orden
- **Drag/Click Confirmación:** Ejecuta orden (pre-visualización)
- **Visual Feedback:** Cambio de opacidad + tono
- **Restricción:** Solo interactivo si `active_player == actual_player` (orden de turnos)

#### Privacidad Visual (PLANNING only)
- **Unidades adversarias:** No renderizadas en Canvas (ocultas completamente)
- **Órdenes adversarias:** No renderizadas en Canvas
- **Terreno:** Completamente visible (mapa base sin filtro)
- **Implicación:** GameState contiene todo; rendering está filtrado por phase+player

### 4.5 Input y Coordenadas

* **Detección Pixel→Hex:** Conversión de click a coordenadas `(q, r)` via matriz 2x2
* **Órdenes:** Selección de unidad → Hotspots en aristas (drag/click)

### 4.6 Responsiveness

| Breakpoint | Layout | Hex Size | Buttons |
|-----------|--------|----------|---------|
| Desktop 1920x1080+ | Full Grid | 64px | Bottom Right |
| Tablet 768-1024 | Scaled Grid | 48px | Center Bottom |
| Mobile <768 | Zoom Default | 40px | Full Width |

### 4.7 Requisitos de Rendimiento

* **60 FPS** en Desktop (Linux/Windows)
* **30 FPS** target en Mobile (Android)
* **Renderizado escalable** del grid hexagonal (canvas dinámico)
* **Single frame rendering** del grid estático (cached canvas)

---

## 5. Assets y Recursos

### 5.1 Estructura de Assets

```
assets/
├── hexagons/
│   ├── Previews/          ← Kenney Hexagon Kit (PNG tiles)
│   │   ├── grass.png      ← DEFAULT terrain
│   │   ├── water.png      ← IMPASSABLE (obstacle)
│   │   ├── sand.png, mountain.png, etc.
│   ├── Textures/          ← Variations for detail
│   └── README.md
├── icons/
│   ├── PNG/               ← Kenney Board Game Icons
│   │   └── [Units, buildings, effects]
│   ├── Tilesheet/         ← Optimized spritesheets
│   └── README.md
└── fonts/
    └── kenney_kenney-fonts/  ← Typography options
```

### 5.2 Hex Grid Setup (Default)

| Setting | Value | Source |
|---------|-------|--------|
| Tile Size | 64×64 px | Kenney Hexagon Kit |
| Terrain Default | grass.png | `assets/hexagons/Previews/` |
| Terrain Impassable | water.png | `assets/hexagons/Previews/` |
| Icon Library | Board Game Icons | `assets/icons/PNG/` |
| Scaling | Dynamic (40-64px) | Based on viewport |

### 5.3 Attribution

**Este proyecto utiliza assets gratuitos de [Kenney.nl](https://kenney.nl/assets):**

- **Hexagon Kit** — Modular hexagonal terrain tiles (3D models + 2D previews)
- **Board Game Icons** — Comprehensive icon library for game development
- **Kenney Fonts** — Open-source typography

**Licencia:** Creative Commons Zero (CC0) — Dominio público

**Citar como:**
```
Kenney.nl (2024). "Hexagon Kit", "Board Game Icons", "Kenney Fonts"
Retrieved from https://kenney.nl/assets
```

---

## 6. Criterios de Aceptación (MVP)

### Funcionalidad Incluida

1. ✓ Tablero generado correctamente (radio 20, sin islas inalcanzables)
2. ✓ Click→Coordenadas funcional en todas las resoluciones
3. ✓ **Interfaz secuencial privada de órdenes** (J1 ordena sin ver J2 → J2 ordena sin ver J1)
   - Phase Transition Screen oscurece el mapa entre turnos
   - Cada jugador ve SOLO sus propias unidades y órdenes durante PLANNING
   - Botón único "Siguiente Jugador" gate-keeps transición entre jugadores
4. ✓ Resolución simultánea compartida (EXECUTION: ambos ven todas las órdenes ejecutarse)
5. ✓ Empates resultan en ambas unidades estáticas (sin cambio)
6. ✓ Limpieza post-turno (Regla 5 Hexágonos) con Phase Transition "Nuevo Turno"

### Funcionalidad NO Incluida

7. ✗ Guardar/cargar partidas (estado volátil, se pierde al cerrar)
8. ✗ Multijugador online (solo hot-seat local)
9. ✗ Persistencia de configuración entre sesiones
10. ✗ Histórico de partidas o estadísticas

---

## 7. Arquitectura de Datos

**IMPORTANTE (MVP):** Todo el GameState es volátil. El estado completo se pierde al cerrar la aplicación. No hay funcionalidad de guardar/cargar partidas en esta versión.

### 7.1 GameState (Pydantic)

```python
class GameState(BaseModel):
    # Core game state
    map: Dict[Tuple[int, int], HexData]
    units: Dict[str, UnitData]
    orders: Dict[str, OrderData]

    # Phase management
    current_phase: GamePhase          # PLANNING, EXECUTION, RESET
    screen_state: ScreenState         # PHASE_TRANSITION, GAMEPLAY
    active_player: int                # 0 or 1 (whose turn is it?)
    turn_number: int

    # UI state (ephemeral)
    selected_hex: Optional[Tuple[int, int]]
    order_path: List[Tuple[int, int]]
    phase_transition_text: str        # "Iniciar Partida", "Siguiente Jugador", "Nuevo Turno"

    # Counters
    next_unit_id: int
    next_order_id: int
    order_history: deque              # Max 500 orders (FIFO)
```

**ScreenState Enum:**
- `PHASE_TRANSITION`: Muestra pantalla oscura con botón (barrera de privacidad)
- `GAMEPLAY`: Muestra Game Screen con grid (orden colocada o ejecución)

### 7.2 Mapa Hexagonal

Coordenadas axiales `(q, r)` como claves. 1,261 hexágonos (radio 20).

**Estructura:** `map = {(q, r): HexData}`

```python
class HexData(BaseModel):
    terrain: TerrainType
    occupant_id: Optional[str]
    last_order_id: Optional[str]
    attributes: Dict[str, Any]
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `terrain` | TerrainType | GRASS (transitable) o WATER (obstáculo) |
| `occupant_id` | str/None | ID de unidad presente o None |
| `last_order_id` | str/None | Última orden ejecutada aquí |
| `attributes` | dict | Extensiones futuras (burning, elevation, etc.) |

### 7.3 Registro de Unidades

**Estructura:** `units = {unit_id: UnitData}`

```python
class UnitData(BaseModel):
    owner: int
    unit_type: UnitType
    position: Tuple[int, int]
    status: UnitStatus
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `owner` | int | 0 o 1 |
| `unit_type` | UnitType | INFANTRY, OFFICER, CAPTAIN |
| `position` | tuple | (q, r) coordenadas actuales |
| `status` | UnitStatus | ACTIVE, ROUTED, RETREAT, ELIMINATED |

**Estados:**

| Estado | Descripción |
|--------|-------------|
| ACTIVE | Operativa |
| ROUTED | En desbandada |
| RETREAT | En retirada ordenada |
| ELIMINATED | Eliminada |

### 7.4 Registro de Órdenes (FIFO)

**Estructura:** `orders = {order_id: OrderData}`

```python
class OrderData(BaseModel):
    unit_id: str
    order_type: OrderType
    coords: Tuple[int, int] | Tuple[int, int, int, int]
    turn: int
    executed: bool
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `unit_id` | str | Unidad que ejecuta |
| `order_type` | OrderType | ATTACK, MOVE, DEPLOY, DEFEND, CANCEL |
| `coords` | tuple | Coordenadas origen/destino |
| `turn` | int | Turno de emisión |
| `executed` | bool | False pendiente, True tras resolución |

### 7.4 Tipos de Órdenes

| Orden | Coords | Descripción |
|-------|--------|-------------|
| ATTACK | (from_q, from_r, to_q, to_r) | Atacar hexágono adyacente ocupado por enemigo |
| MOVE | (from_q, from_r, to_q, to_r) | Mover a hexágono adyacente vacío y transitable |
| DEPLOY | (q, r) | Desplegar unidad en posición inicial (solo fase de setup) |
| DEFEND | (q, r) | Mantener posición con bonificación defensiva |
| CANCEL | (q, r) | Cancelar orden previa de la unidad (solo durante PLANNING) |

**Ciclo de Vida de una Orden:**
1. Se crea durante fase PLANNING con `executed: False`
2. Se procesa durante fase EXECUTION
3. Se marca `executed: True` tras resolución
4. Se elimina automáticamente cuando el historial FIFO alcanza su límite (default: 500 órdenes)

### 7.5 Sistema FIFO

`order_history` usa `deque(maxlen=500)`. Cuando se alcanza el límite, la orden más antigua se elimina automáticamente.

### 7.6 Fases del Juego

**PLANNING (P1 - PRIVATE) → PLANNING (P2 - PRIVATE) → EXECUTION (SHARED) → RESET (SILENT) → repeat**

| Fase | Acción | Visibilidad | Órdenes |
|------|--------|-------------|---------|
| **PLANNING (P1)** | J1 emite órdenes | PRIVATE: Solo J1 ve sus unidades+órdenes | `executed: False` |
| | | J2 unidades/órdenes OCULTAS | |
| | | Gate: "Siguiente Jugador" button | |
| **PLANNING (P2)** | J2 emite órdenes | PRIVATE: Solo J2 ve sus unidades+órdenes | `executed: False` |
| | | J1 unidades/órdenes OCULTAS | |
| | | Gate: "Siguiente Jugador" button | |
| **EXECUTION** | Resolución simultánea | SHARED: Ambos ven TODAS órdenes | `executed: True` |
| | Movimientos + Combates | Visualización en tiempo real | |
| | Auto-ejecución | Sin botones, transición automática | |
| **RESET** | Limpieza silenciosa | HIDDEN: Regla 5 Hexágonos | (interno) |
| | | Gate: "Nuevo Turno" button aparece | |

**Nota Importante:** GameState contiene el estado completo del juego (todas las unidades, órdenes de ambos jugadores). La privacidad es **visual solamente** — el rendering de Canvas filtra qué se muestra basado en `current_phase` y `active_player`.

---

## 8. Nota Técnica

La lógica de negocio es agnóstica a la capa Flet.

### Comunicación Engine ↔ UI

| Dirección | Datos |
|-----------|-------|
| UI → Engine | Acceso directo a GameState |
| Engine → UI | Eventos de cambio de estado |
