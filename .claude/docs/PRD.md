# SyV-Flet - Product Requirements Document (PRD)

**Versión:** 2.0
**Fecha:** 18 de Enero, 2026
**Plataforma:** PC (Linux/Windows) & Mobile (Android)
**Modelo de Distribución:**
- **MVP:** Single Device / Hot Seat (local)
- **Futuro:** Multijugador online vía API REST (servidor cloud)

---

## 1. Visión del Producto

Un juego de estrategia por turnos simultáneos (WEGO) 1v1 sobre un tablero hexagonal determinista llamado "Subordinación y Valor" (SyV). La resolución de conflictos es completamente determinista basada en la comparación de fuerzas.

### Evolución del Producto

| Fase | Modelo | Descripción |
|------|--------|-------------|
| **MVP** | Hot Seat Local | Dos jugadores en el mismo dispositivo, turnos alternados privados |
| **v2.0** | Multijugador Online | Servidor cloud recibe órdenes vía API, resuelve turno, devuelve estado |

**Estrategia Arquitectónica:** El motor lógico está diseñado como agnóstico al origen de datos. Las órdenes pueden provenir del UI local (MVP) o de un endpoint remoto (v2.0) sin refactoring del engine.

---

## 2. Stack Tecnológico & Justificaciones

### 2.1 Selecciones Tecnológicas Core

#### Python 3.13+
- **QUÉ:** Lenguaje de ejecución del motor y UI
- **POR QUÉ:** Tipado fuerte opcional (Pydantic), sintaxis clara para lógica de dominio, ecosistema maduro para juegos (Flet, Loguru)
- **DÓNDE:** `src/syv_flet/`

#### Flet (v0.24.0+)
- **QUÉ:** Framework UI cross-platform basado en Flutter
- **POR QUÉ:** Renderizado nativo acelerado (Canvas con Skia engine), soporte Desktop + Mobile sin bifurcación, distribución simplificada (.exe, .apk), curva de aprendizaje baja
- **DÓNDE:** `src/syv_flet/ui/`

#### Skia Engine (Canvas Rendering)
- **QUÉ:** Motor de renderizado subyacente en Flet
- **POR QUÉ:** Aceleración GPU, antialiasing nativo, soporte para primitivas geométricas (líneas, polígonos) necesarias para hexágonos
- **DÓNDE:** Integrado en Flet; usado via `flet.canvas`

#### Loguru (Logging)
- **QUÉ:** Motor de logging thread-safe con rotación automática
- **POR QUÉ:**
  - **Prevención de llenar disco:** Rotación automática crítica para versiones futuras dockerizadas
  - **Context Injection:** Capacidad de vincular `game_id`, `player_id` a logs (preparación para multiplayer)
  - **API minimalista:** Menos boilerplate que `logging` estándar
  - **Thread-safe:** Esencial para Flet/Asyncio
- **DÓNDE:** `src/syv_flet/utils/logger.py` (centralizado)

#### uv (Dependency Manager)
- **QUÉ:** Gestor de dependencias y virtualenv (reemplazo de pip/poetry)
- **POR QUÉ:** Velocidad, lockfile determinista, soporte nativo para Python 3.13, facilita reproducibilidad
- **DÓNDE:** `pyproject.toml`, `uv.lock`

#### Pydantic V2+
- **QUÉ:** Validación de datos y serialización de modelos
- **POR QUÉ:** Tipado fuerte en tiempo de ejecución, validación en límites del sistema, preparado para REST API (v2.0)
- **DÓNDE:** `src/syv_flet/engine/models/` (GameState, HexData, UnitData, OrderData)

### 2.2 Exclusiones Deliberadas

- **Bases de datos (MVP):** Estado volátil. No hay persistencia entre sesiones.
- **Frameworks web:** No aplica para hot-seat local.
- **ORM:** No hay entidades persistentes en MVP.

---

## 3. Mecánica de Juego

### 3.1 Coordenadas Hexagonales

#### Modelo: Cúbico + Axial
- **QUÉ:** Coordenadas `(q, r, s)` donde `q + r + s = 0` con proyección optimizada a `(q, r)`
- **POR QUÉ:**
  - **Cúbico:** Matemática elegante para distancia, adyacencia, líneas (ver skill `hex-grid-math`)
  - **Axial:** Reduce memoria a 2 coordenadas, no 3
  - **Invariante q+r+s=0:** Garantiza correctitud de cálculos sin verificación explícita

#### Orientación: Flat-Top
- **QUÉ:** Hexágonos con lado plano arriba (no punta)
- **POR QUÉ:** Coincide con sistema de iconografía Kenney (previsualizaciones 2D con orientación flat-top)

#### Tablero: Radio R=20
- **QUÉ:** Hexágonos válidos donde `max(|q|, |r|, |s|) ≤ 20`
- **CANTIDAD:** 1,261 hexágonos totales (fórmula: `3*R*(R+1) + 1`)
- **POR QUÉ:** Equilibrio entre complejidad visual (cabe en pantalla) y profundidad estratégica

#### Distancia: Manhattan Hexagonal
- **QUÉ:** `distance(a, b) = (|q1-q2| + |r1-r2| + |s1-s2|) / 2`
- **POR QUÉ:**
  - Determinista (sin raíz cuadrada)
  - Coincide con número de pasos reales en grid (validación de alcance de órdenes)
  - Usado en Regla 5 Hexágonos (aislamiento de unidades)

### 3.2 Entidades Base

#### Unidades
- **Tipos:** Infantry, Officer, Captain
- **Estados:** ACTIVE, ROUTED, RETREAT, ELIMINATED
- **Propietario:** 0 o 1 (jugadores)
- **Posición:** Coordenadas `(q, r)` en el mapa

#### Pool de Órdenes
- **Composición:** `(Officers × 1) + (Captain × 3)` = N órdenes disponibles
- **Consumo:** Una orden por unidad activa durante PLANNING, excepto DEFENSE (sin costo)
- **Recuperación:** CANCEL devuelve orden al pool

### 3.3 Resolución de Turno (Fase EXECUTION)

1. **Movimiento:** Unidades ejecutan órdenes MOVE/DEPLOY/ATTACK, resolviendo colisiones
2. **Combate Determinista:**
   - Comparación directa de fuerzas (unidad en mismo hex)
   - Ganador: Mayor fuerza. Loser: Eliminada
   - **Empate:** Ambas unidades estáticas (sin cambio)
3. **Post-Procesado:**
   - Transiciones de estado (RETREAT → ROUTED → ELIMINATED)
   - **Regla 5 Hexágonos:** Unidades a distancia > 5 de cualquier officer → ELIMINATED

**POR QUÉ determinista:** Elimina RNG (dado), permite reproducibilidad, acelera resolución simultánea

---

## 4. Interfaz de Usuario (Flet)

### 4.1 Filosofía de Diseño: Minimalismo Radical

**Principio:** Vacío intencionado. Cada píxel existe por propósito táctico, no decoración.

#### Justificaciones
- **95% Mapa:** Enfoque total en grid. Mínima UI desconcentra
- **2 Elementos de Control:** Reduce fricción, claridad de intent
- **Feedback Implícito:** Cambios sutiles (opacidad, tonalidad) comunican estado sin texto
- **Intentionalidad Visual:** Espacios vacíos son activos, no deficiencias

### 4.2 Arquitectura de Pantallas

#### Screen 1: Phase Transition (Barrera de Privacidad)

**Propósito:** Bloquea visibilidad entre turnos. Anunciador de fase.

**Composición:**
- Fondo oscuro (overlay negro, opacidad 0.95)
- Botón reutilizable centrado
- Textos contextuales

**Textos según fase:**
- "Iniciar Partida" (game start)
- "Siguiente Jugador" (entre turnos PLANNING)
- "Nuevo Turno" (post-RESET)

**POR QUÉ:** En hot-seat, necesitamos barrera física (visual) entre jugadores. Esta pantalla es la única forma de progresar entre fases, garantizando que ningún jugador "peeking" en la pantalla anterior.

#### Screen 2: Game Screen (Juego Activo)

**Propósito:** Tablero hexagonal + controles interactivos.

**Composición (Z-Order):**
1. **Static Canvas:** Grid de hexágonos (dibujado UNA VEZ, cacheado)
2. **Dynamic Canvas:** Unidades, órdenes, efectos (re-dibujado en estado changed)
3. **Gesture Detector:** Input layer (tap/drag para órdenes)
4. **UI Overlay:** Botón "Siguiente Jugador" (solo PLANNING), contadores de fase

**Responsive Breakpoints:**

| Breakpoint | Layout | Hex Size | Buttons |
|-----------|--------|----------|---------|
| Desktop 1920x1080+ | Full Grid | 64px | Fixed bottom-right |
| Tablet 768-1024 | Scaled Grid | 48px | Center bottom |
| Mobile <768 | Zoom Default | 40px | Full width bottom |

### 4.3 Estados Visuales y Privacidad

#### Fase PLANNING (Privada por Jugador)

**Jugador Activo:**
- ✓ Ve SOLO sus propias unidades
- ✓ Ve SOLO sus propias órdenes pendientes (opacidad 0.4, "ghost" mode)
- ✓ Ve terreno completo (grass, water)
- ✓ Puede interactuar (colocar órdenes)

**Jugador Opuesto:**
- ✗ Unidades NO renderizadas (no dibujadas en Canvas dinámico)
- ✗ Órdenes NO renderizadas
- ✗ Terreno visible (pero no indica posiciones enemigas)

**Mecanismo:** `GameState` contiene estado completo. Rendering filtra según `current_phase` + `active_player` antes de dibujar.

#### Fase EXECUTION (Compartida)

**Ambos Jugadores:**
- ✓ Ven TODAS las unidades (opacidad 1.0)
- ✓ Ven TODAS las órdenes (coloreadas por faction: Azul P1, Rojo P2)
- ✓ Visualización en tiempo real de resolución
- ✓ Sin botones (transición automática post-animación)

#### Fase RESET (Silenciosa)

- Limpieza automatizada (Regla 5 Hexágonos)
- No visible al usuario
- Auto-transiciona a PHASE_TRANSITION con botón "Nuevo Turno"

### 4.4 Interactividad y Cycle-Tap Mechanism

**Referencia:** Skill `cycle-tap-mechanism` define orden de taps y state transitions.

**Resumen Rápido:**
- **Tap origen (unit):** Selecciona como origen
- **Tap origen 2da vez:** Switch a DEFENSE
- **Tap origen 3ra vez:** CANCEL (devuelve orden)
- **Tap adjacent 1ra vez:** ATTACK
- **Tap adjacent 2da vez:** Inicia MOVEMENT path
- **Tap successive:** Extiende path (max 3 waypoints)
- **Tap origin to confirm:** Finaliza MOVEMENT

**Feedback Visual:**
- Origen: Double outline + faction color fill (0.2 opacity)
- Adjacent (hover): Single outline + yellow highlight (0.15 opacity)
- Orders: Iconos (sword=ATTACK, arrow=MOVE, shield=DEFENSE) + path visualization

### 4.5 Requisitos de Rendimiento

- **Desktop:** 60 FPS (Linux/Windows)
- **Mobile:** 30 FPS target (Android)
- **Caching:** Static grid dibujado una sola vez
- **Culling:** Solo hexes visibles en viewport renderizados

---

## 5. Assets y Recursos

### 5.1 Fuentes y Estructura

**Proveedor:** Kenney.nl (Creative Commons Zero — Dominio Público)

**Componentes:**

| Tipo | Cantidad | Ubicación | Resolución |
|------|----------|-----------|------------|
| Hexagon Tiles (terreno) | 74 PNG | `assets/hexagons/Previews/` | 64×64px |
| Board Game Icons | 292 (64px) + 218 (128px) | `assets/icons/PNG/` | 64px, 128px |
| Fonts | ~10 | `assets/fonts/kenney_kenney-fonts/` | TTF/OTF |

### 5.2 Mapeo de Assets a Gameplay

#### Terrain Hexagons
- **Default:** `grass.png` (transitable)
- **Obstacle:** `water.png` (impasable)
- **Variantes:** sand, stone, mountain (extensión futura)

#### Order Icons
| Orden | Icono | Ubicación |
|-------|-------|-----------|
| ATTACK | sword | `icons/PNG/Default (64px)/` |
| MOVE | arrow/path | `icons/PNG/Default (64px)/` |
| DEFEND | shield | `icons/PNG/Default (64px)/` |
| DEPLOY | flag | `icons/PNG/Default (64px)/` |

#### Typography
- UI text (buttons, turnos): Kenney Fonts suite
- Flexible pesos para scaling responsive

### 5.3 Estrategia de Carga

**MVP:** Batch preload todos los hexagon tiles (74) + iconos frecuentes al startup. Resto lazy-load on-demand.

**POR QUÉ:** Evita stutter en primer render, mantiene memoria acotada para mobile.

**Caching:** In-memory dictionary (path → Image object). Invalidar en cambios de tema.

### 5.4 Attribution

```
Kenney.nl (2024). "Hexagon Kit", "Board Game Icons", "Kenney Fonts"
Retrieved from https://kenney.nl/assets
License: Creative Commons Zero (CC0) — Public Domain
```

---

## 6. Criterios de Aceptación (MVP)

### Incluido

1. ✓ Tablero generado correctamente (radio 20, conectado, sin islas inalcanzables)
2. ✓ Input pixel→hexágono funcional en todas las resoluciones
3. ✓ **Interfaz Privada de Órdenes:**
   - Phase Transition Screen bloqueando visibilidad entre turnos
   - Cada jugador ve SOLO sus unidades durante PLANNING
   - Botón "Siguiente Jugador" gate-keeps transición
4. ✓ Resolución simultánea compartida (EXECUTION: ambos ven todas órdenes ejecutarse)
5. ✓ Empates resultan en ambas unidades estáticas
6. ✓ Limpieza post-turno (Regla 5 Hexágonos) + Phase Transition "Nuevo Turno"
7. ✓ Ciclo tap completo (origen selection → adjacent tapping → path building → confirmation)

### NO Incluido

8. ✗ Guardar/cargar partidas (estado volátil)
9. ✗ Multijugador online
10. ✗ Persistencia de configuración
11. ✗ Histórico de partidas o estadísticas
12. ✗ Undo/replay

---

## 7. Arquitectura de Datos

**Principio:** Todo en `GameState`. Agnóstico a origen de datos (local UI o API remota).

### 7.1 GameState (Modelo Raíz)

**Componentes:**

- **map:** Diccionario de `HexData` indexado por `(q, r)`
- **units:** Diccionario de `UnitData` indexado por `unit_id`
- **orders:** Diccionario de `OrderData` indexado por `order_id` (FIFO deque con límite)
- **current_phase:** Enum `GamePhase` (PLANNING, EXECUTION, RESET)
- **screen_state:** Enum `ScreenState` (PHASE_TRANSITION, GAMEPLAY)
- **active_player:** Int (0 o 1)
- **turn_number:** Int (incrementa cada RESET)
- **selected_hex:** Optional coordenadas (UI state, ephemeral)
- **order_path:** Lista de coordenadas (path building, ephemeral)
- **phase_transition_text:** String ("Iniciar Partida", "Siguiente Jugador", "Nuevo Turno")

**POR QUÉ Single Root:** Simplifica sincronización entre engine y UI. En v2.0, este estado se serializa y viaja via API.

### 7.2 HexData (Mapa)

**Responsabilidad:** Describe estado de UNA celda hexagonal.

**Campos:**
- **terrain:** Enum `TerrainType` (GRASS, WATER)
- **occupant_id:** Optional str (unit_id si hay unidad, None si vacío)
- **last_order_id:** Optional str (trailing de última orden ejecutada aquí)
- **attributes:** Dict (extensión futura: burning, elevation, etc.)

**Invariantes:**
- Un hexágono = máximo UNA unidad (no stacking)
- Solo terrain GRASS es transitable
- WATER es siempre intransitable

### 7.3 UnitData (Registro de Unidades)

**Responsabilidad:** Define UNA unidad en el tablero.

**Campos:**
- **owner:** Int (0 o 1)
- **unit_type:** Enum `UnitType` (INFANTRY, OFFICER, CAPTAIN)
- **position:** Tuple[int, int] (coordenadas `(q, r)` actuales)
- **status:** Enum `UnitStatus` (ACTIVE, ROUTED, RETREAT, ELIMINATED)

**Estados y Transiciones:**
- ACTIVE → ROUTED (tras combate perdedor)
- ROUTED → RETREAT (siguiente turno)
- RETREAT → ELIMINATED (siguiente turno si aún aislada)
- Cualquiera → ELIMINATED (Regla 5 Hexágonos)

**POR QUÉ diccionario:** Lookup O(1) por unit_id, necesario para resolver órdenes en EXECUTION.

### 7.4 OrderData (Registro de Órdenes)

**Responsabilidad:** Reifica UNA orden antes de ejecución.

**Campos:**
- **unit_id:** Str (unidad que ejecuta)
- **order_type:** Enum `OrderType` (ATTACK, MOVE, DEPLOY, DEFEND, CANCEL)
- **coords:** Tuple o Path (origen/destino o secuencia de waypoints)
- **turn:** Int (turno de emisión, para auditoría)
- **executed:** Bool (False pendiente, True post-resolución)

**Tipos de Orden:**

| Tipo | Coords | Efecto | Costo |
|------|--------|--------|-------|
| ATTACK | (from_q, from_r, to_q, to_r) | Ataca hex adyacente | 1 orden |
| MOVE | [waypoint1, waypoint2, ...] | Path multi-hex (max 3) | 1 orden |
| DEPLOY | (q, r) | Deploy inicial (setup only) | 1 orden |
| DEFEND | (q, r) | +bonificación defensiva en hex | 0 ordenes |
| CANCEL | (q, r) | Invalida orden previa | Devuelve 1 |

### 7.5 Sistema FIFO de Órdenes

- **Estructura:** `deque(maxlen=500)` (max 500 órdenes en historial)
- **Ciclo de Vida:**
  1. Creada en PLANNING con `executed: False`
  2. Procesada en EXECUTION
  3. Marcada `executed: True`
  4. Auto-eliminada cuando deque alcanza límite (FIFO overflow)

**POR QUÉ FIFO:** Previene memory leaks en sesiones largas. 500 órdenes ≈ 100 turnos (5 órdenes/turno promedio).

### 7.6 Flow de Fases (Orthogonal a Visibilidad)

#### Transiciones de Fase

```
START
  ↓
PLANNING (P1)
  ↓ [btn "Siguiente Jugador"]
PLANNING (P2)
  ↓ [btn "Siguiente Jugador"]
EXECUTION (ambos)
  ↓ [auto, post-animación]
RESET (silenciosa)
  ↓ [auto]
PHASE_TRANSITION (btn "Nuevo Turno")
  ↓
PLANNING (P1) [turn_number++]
```

#### Reglas de Visibilidad (Orthogonal)

| Phase | Screen State | Active Player | Visibility |
|-------|--------------|---------------|------------|
| PLANNING | PHASE_TRANSITION | N/A | NONE (overlay oscuro) |
| PLANNING | GAMEPLAY | P1 | P1 units/orders visible (0.4), P2 hidden |
| PLANNING | GAMEPLAY | P2 | P2 units/orders visible (0.4), P1 hidden |
| EXECUTION | GAMEPLAY | N/A | ALL units/orders visible (1.0) |
| RESET | HIDDEN | N/A | Internal cleanup, no render |

**POR QUÉ separación:** Phase controla lógica (qué órdenes se procesan). Visibility controla rendering (qué se dibuja). Orthogonal = flexible.

---

## 8. Estrategia de Logging

**Centralización:** `src/syv_flet/utils/logger.py`

### Niveles y Sinks

| Nivel | Archivo | Caso de Uso |
|-------|---------|------------|
| DEBUG | `debug.log` | Traza de ejecución (state changes, input) |
| INFO | `{YYYY-MM-DD}.log` | Game flow (turn start, phase change, elimination) |
| ERROR | `error.log` | Excepciones manejadas |
| CRITICAL | `error.log` | Corrupción de estado irreversible |
| (Todos) | STDERR | Salida inmediata en color (desarrollo) |

### Rotación

- **Daily:** Archivos `YYYY-MM-DD.log` crean nuevo cada día
- **Size-based:** Si excede 10MB, rotar automáticamente
- **Retention:** Máximo 30 días de historial (configurable)

**POR QUÉ:** Previene llenar disco en docker (v2.0). Facilita auditoría multiplayer (logs contextualizados).

### Uso

- **No `print()`:** Se reemplaza con logger
- **Context:** En multiplayer, inyectar `game_id`, `player_id` al logger context
- **Performance:** Logger es non-blocking (async writes cuando posible)

---

## 9. Notas Técnicas

### 9.1 Separación: Engine vs. UI

| Capa | Responsabilidad | Ubicación |
|------|-----------------|-----------|
| **Engine** | Lógica de negocio (pura, determinista, sin Flet) | `src/syv_flet/engine/` |
| **UI** | Renderizado, input, state binding | `src/syv_flet/ui/` |
| **Models** | Pydantic schemas (agnóstico a capa) | `src/syv_flet/engine/models/` |

**POR QUÉ:** Engine testeable sin UI. Facilita paso a API (v2.0).

### 9.2 Comunicación Engine ↔ UI

- **UI → Engine:** Acceso directo a `GameState` (validación via Pydantic)
- **Engine → UI:** Event-driven o polling (TBD en implementation)
- **Serialización:** `GameState` → JSON (ready para API v2.0)

### 9.3 Testability

- Engine lógica: 80%+ coverage via pytest (BDD style)
- UI layer: Smoke tests (cobertura de critical paths)
- Fixtures: Board states (empty, populated, mid-execution)

### 9.4 Decisiones Irreversibles

- **Hot-Seat only (MVP):** No auth, no multiplayer infrastructure
- **Volatile State:** MVP no persiste. v2.0 añade DB + API
- **Flat-Top Locked:** Cambiar a Pointy-Top requiere refactor math + rendering

---

## 10. Roadmap (Futuro)

### v2.0: Multiplayer Online

- REST API (orders endpoint)
- Cloud resolver (stateless)
- Session persistence
- Matchmaking lobby

### v2.1: Features

- Save/Load games
- Replay system
- Statistics tracking
- Ranked ladder

---

**END OF DOCUMENT**
