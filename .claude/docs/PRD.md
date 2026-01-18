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

## 7. Arquitectura de Datos: Hash Maps

**IMPORTANTE (MVP):** Todo el GameState es volátil. El estado completo se pierde al cerrar la aplicación. No hay funcionalidad de guardar/cargar partidas en esta versión.

La clave de esta implementación es la **separación de responsabilidades**. No guardamos "todo dentro de todo", sino que usamos IDs para vincular las diferentes tablas. Este diseño permite que el motor lógico funcione tanto localmente (MVP) como en servidor cloud (v2.0 multijugador).

### 7.1 Mapa Hexagonal (Topología Fija)

Coordenadas axiales `(q, r)` como claves. Base espacial del juego con 1,261 hexágonos (radio 20). La topología del tablero no cambia durante la partida.

**Estructura:** `mapa = {(q, r): hex_data}`

| Campo | Tipo | Valores | Descripción |
|-------|------|---------|-------------|
| `terreno` | int | 0=GRASS, 1=WATER | Tipo de terreno. GRASS es transitable, WATER es obstáculo |
| `unit_id` | int/None | ID numérico o None | Referencia a la unidad presente. None si el hexágono está vacío |
| `last_order_id` | int/None | ID numérico o None | Última orden ejecutada aquí. Útil para feedback visual en UI |

**Notas:**
- La clave `(q, r)` es una tupla de coordenadas axiales
- Un hexágono vacío tiene `unit_id: None`
- El campo `last_order_id` permite mostrar indicadores visuales de acciones recientes

### 7.2 Registro de Unidades

Repositorio centralizado donde cada unidad tiene un ID único. Facilita la **Regla de los 5 Hexágonos** y el cálculo de fuerzas. El estado de las unidades cambia durante el juego (movimiento, combate, eliminación).

**Estructura:** `unidades = {unit_id: unit_data}`

| Campo | Tipo | Valores | Descripción |
|-------|------|---------|-------------|
| `bando` | int | 0 o 1 | Jugador 1 (0) o Jugador 2 (1) |
| `tipo` | str | INFANTRY, OFFICER, CAPTAIN | Tipo de unidad según jerarquía militar |
| `pos` | tuple | (q, r) | Coordenadas axiales actuales de la unidad |
| `estado` | str | ACTIVE, ROUTED, RETREAT, ELIMINATED | Estado actual de la unidad |

**Estados de Unidad:**

| Estado | Descripción |
|--------|-------------|
| ACTIVE | Unidad operativa, puede recibir y ejecutar órdenes |
| ROUTED | Unidad en desbandada, movimiento limitado hacia retaguardia |
| RETREAT | Unidad en retirada ordenada, puede reagruparse |
| ELIMINATED | Unidad eliminada del juego, no se procesa |

**Notas:**
- El `unit_id` es un entero único incremental asignado al crear la unidad
- El campo `pos` debe mantenerse sincronizado con `mapa[(q,r)].unit_id`
- La transición de estados sigue reglas de combate y la Regla de los 5 Hexágonos

### 7.3 Registro de Órdenes (con Limpieza FIFO)

ID incremental con sistema de historial. Las órdenes se guardan cronológicamente en memoria y se limpian automáticamente mediante sistema FIFO para prevenir memory leaks.

**Estructura:** `ordenes = {order_id: order_data}`

| Campo | Tipo | Valores | Descripción |
|-------|------|---------|-------------|
| `unit_id` | int | ID numérico | Referencia a la unidad que ejecuta la orden |
| `tipo` | str | ATTACK, MOVE, DEPLOY, DEFEND, CANCEL | Tipo de orden a ejecutar |
| `coords` | tuple | (from_q, from_r, to_q, to_r) o (q, r) | Coordenadas origen/destino según tipo de orden |
| `turno` | int | Número positivo | Número de turno en que se emitió la orden |
| `executed` | bool | True/False | False mientras está pendiente, True tras resolución |

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

### 7.5 GameState: Contenedor Central

El GameState es la clase que encapsula los tres Hash Maps y gestiona el estado global del juego.

**Componentes del GameState:**

| Componente | Tipo | Descripción |
|------------|------|-------------|
| `mapa` | dict | Hash Map de hexágonos: `{(q, r): hex_data}` |
| `unidades` | dict | Hash Map de unidades: `{unit_id: unit_data}` |
| `ordenes` | dict | Hash Map de órdenes: `{order_id: order_data}` |
| `next_unit_id` | int | Contador incremental para IDs de unidades |
| `next_order_id` | int | Contador incremental para IDs de órdenes |
| `order_history_ids` | deque | Cola FIFO para limpieza automática de órdenes antiguas |
| `current_phase` | str | Fase actual: PLANNING, EXECUTION, o RESET |
| `active_player` | int | Jugador activo: 0 o 1 |
| `turn_number` | int | Número de turno actual |

**Sistema FIFO para Órdenes:**

El historial de órdenes usa `collections.deque` con `maxlen=500` (configurable). Cuando se alcanza el límite:
1. La orden más antigua se elimina automáticamente del deque
2. Se borra la entrada correspondiente en el Hash Map `ordenes`
3. La nueva orden se añade al final del deque

Esto garantiza que el juego nunca consumirá memoria ilimitada en partidas largas.

### 7.6 Fases del Juego (Conceptual)

El juego opera en tres fases secuenciales que se repiten cada turno:

**PLANNING → EXECUTION → RESET → PLANNING...**

| Fase | Acción Principal | Estado de Órdenes |
|------|------------------|-------------------|
| **PLANNING** | Jugadores emiten órdenes | Se crean con `executed: False` |
| **EXECUTION** | Motor resuelve movimientos y combates | Se marcan `executed: True` |
| **RESET** | Limpieza post-turno, cambio de jugador | Se aplica Regla 5 Hexágonos |

**Diferencias por Modelo de Distribución:**

| Modelo | Flujo de Datos |
|--------|----------------|
| **MVP (local)** | UI → GameState directo. Ambos jugadores en mismo dispositivo |
| **v2.0 (cloud)** | Cliente envía órdenes vía API → Servidor ejecuta EXECUTION → Devuelve estado actualizado |

### 7.7 Ventajas de esta Arquitectura

| Ventaja | Descripción |
|---------|-------------|
| **Acceso O(1)** | Búsqueda por ID o coordenada es instantánea (60 FPS garantizados) |
| **Trazabilidad** | `executed: true` permite Modo Replay o Log de batalla |
| **Seguridad de Memoria** | `deque(maxlen)` previene memory leaks en partidas largas |
| **API-Ready** | Motor agnóstico al origen de órdenes (UI local o API remota) |
| **Simplicidad WEGO** | Resolución itera solo `ordenes` del turno actual |

---

## 8. Nota Técnica

La lógica de negocio debe mantenerse completamente **agnóstica a la capa Flet**. Las decisiones de renderizado no impactan las reglas del juego.

### Comunicación Engine ↔ UI

| Modelo | Dirección | Datos |
|--------|-----------|-------|
| **MVP (local)** | UI → Engine | Acceso directo a GameState |
| **MVP (local)** | Engine → UI | Lectura directa de Hash Maps |
| **v2.0 (cloud)** | Cliente → Servidor | Lista de órdenes del turno |
| **v2.0 (cloud)** | Servidor → Cliente | Estado actualizado del mapa + eventos |

### Contrato de Datos (API-Ready)

**Request (Cliente → Servidor):**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `player_id` | int | Identificador del jugador (0 o 1) |
| `orders` | list | Lista de órdenes, cada una con: unit_id, tipo, coords |

**Response (Servidor → Cliente):**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `turn` | int | Número de turno tras resolución |
| `mapa` | dict | Estado completo del mapa hexagonal |
| `unidades` | dict | Estado completo de todas las unidades |
| `events` | list | Lista de eventos ocurridos (movimientos, combates, eliminaciones) |

### Principio de Diseño

Esta estructura permite que el mismo motor lógico funcione sin modificaciones tanto en el MVP local como en el servidor cloud futuro. El motor recibe órdenes, las procesa, y devuelve estado — independiente de si el origen es una UI local o una API remota.
