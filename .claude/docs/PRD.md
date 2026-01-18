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
* **Modelo:** Coordenadas cúbicas `(q, r, s)` donde `q + r + s = 0`, proyectadas a coordenadas axiales `(q, r)` para optimización de memoria (ver [ARCHITECTURE.md](./ARCHITECTURE.md) para detalles técnicos)
* **Tablero:** Radio R=20 (fórmula: `3*R*(R+1) + 1` = 1,261 hexágonos)
* **Adyacencia:** 6 vecinos inmediatos calculados mediante vectores de dirección constantes
* **Distancia:** Manhattan hexagonal: `dist(a, b) = (|a.q - b.q| + |a.q + a.r - b.q - b.r| + |a.r - b.r|) / 2`

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

### 4.2 Arquitectura Visual

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
  [Start Game] [Next Turn]  (2 buttons)
```

**Capas Flet:**
1. **Canvas Static:** Grid hexagonal (dibujado una vez)
2. **Canvas Dynamic:** Unidades y efectos de combate
3. **GestureDetector:** Input de coordenadas + órdenes
4. **UI Overlay:** Botones (Start, Next Turn)

### 4.3 Elementos Visuales

#### Terreno (Hexagons)
- **Default:** `grass.png` (Kenney Hexagon Kit - Previews)
- **Impasable:** `water.png`
- **Futuro:** Variantes (sand, mountain, snow)
- **Resolución:** 64x64 px (escalable)
- **Ubicación:** `assets/hexagons/Previews/`

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

#### Botón "Start Game"
- **Estilo:** Redondo, gomoso (border-radius 50%, shadow suave)
- **Color:** Accent color TBD
- **Posición:** Centro de pantalla (pantalla de inicio)
- **Acción:** Navega a GameScreen

#### Botón "Next Turn"
- **Estilo:** Idéntico a Start Game, pero secundario
- **Posición:** Esquina inferior (fixed)
- **Visibilidad:** Solo post-orden (invisible por defecto)
- **Acción:** Ejecuta turn logic y cambia de jugador

#### Interactividad de Nodos
- **Click en Hex:** Selecciona unidad / muestra opciones
- **Hover en Arista:** Resalta posible orden
- **Drag/Click Confirmación:** Ejecuta orden (pre-visualización)
- **Visual Feedback:** Cambio de opacidad + tono

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
3. ✓ Interfaz secuencial de órdenes (J1 → J2)
4. ✓ Resolución automática de movimiento y combates
5. ✓ Empates resultan en ambas unidades estáticas (sin cambio)
6. ✓ Limpieza post-turno (Regla 5 Hexágonos)

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
    map: Dict[Tuple[int, int], HexData]
    units: Dict[str, UnitData]
    orders: Dict[str, OrderData]

    current_phase: GamePhase
    active_player: int
    turn_number: int

    selected_hex: Optional[Tuple[int, int]]
    order_path: List[Tuple[int, int]]

    next_unit_id: int
    next_order_id: int
    order_history: deque
```

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

**PLANNING → EXECUTION → RESET → PLANNING...**

| Fase | Acción | Órdenes |
|------|--------|---------|
| **PLANNING** | Jugadores emiten órdenes | `executed: False` |
| **EXECUTION** | Resolución de movimientos y combates | `executed: True` |
| **RESET** | Limpieza, cambio de jugador | Regla 5 Hexágonos |

---

## 8. Nota Técnica

La lógica de negocio es agnóstica a la capa Flet.

### Comunicación Engine ↔ UI

| Dirección | Datos |
|-----------|-------|
| UI → Engine | Acceso directo a GameState |
| Engine → UI | Eventos de cambio de estado |
