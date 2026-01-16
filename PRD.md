# SyV-Flet - Product Requirements Document (PRD)

**Versión:** 1.0
**Fecha:** 16 de Enero, 2026
**Plataforma:** PC (Linux/Windows) & Mobile (Android)
**Modelo de Distribución:** Single Device / Hot Seat

---

## 1. Visión del Producto

Un juego de estrategia por turnos simultáneos (WEGO) 1v1 sobre un tablero hexagonal estocástico basado en los principios de Subordinación y Valor (SyV). El juego prioriza la táctica posicional y la gestión de la cadena de mando sobre la acción visual. La resolución de conflictos utiliza una mecánica única de input analógico (Brújula) para eliminar el azar puramente numérico.

---

## 2. Stack Tecnológico

* **Lenguaje:** Python 3.12+
* **Framework UI:** Flet (versión estable)
* **Motor de Renderizado:** `flet.canvas` (Skia Engine via Flutter)
* **Empaquetado:** `flet build` (APK, Linux AppImage/Executable)
* **Gestión de Estado:** Python nativo (clases observables)
* **Dependencias Externas:** Ninguna para lógica de negocio

---

## 2.5 Modelo de Interacción (Hot Seat / Single Device)

**Este es un juego de un único dispositivo compartido (hot seat).**

- **Ambos jugadores usan el mismo dispositivo**
- **Las órdenes del jugador anterior están COMPLETAMENTE OCULTAS cuando toma turno el siguiente**
- **Botón "Cambiar Jugador":**
  - Borra visualmente todas las órdenes del tablero
  - Reinicia la UI
  - Cambia el identificador de "jugador actual"
  - Permite que el siguiente jugador vea solo su pool de órdenes
- **Privacidad en PLANIFICACIÓN:** Las órdenes secretas se revelan solo en EJECUCIÓN
- **Implementación:** Solo un jugador tiene acceso visible al estado de órdenes a la vez

---

## 3. Mecánica de Juego

### Sistema de Coordenadas
* **Modelo:** Coordenadas cúbicas `(q, r, s)` donde `q + r + s = 0`, proyectadas a coordenadas axiales `(q, r)` para optimización de memoria (ver skill `hex-grid-math` para detalles matemáticos)
* **Tablero:** Radio R=20 (fórmula: `3*R*(R+1) + 1` = 1,261 hexágonos)
* **Adyacencia:** 6 vecinos inmediatos calculados mediante vectores de dirección constantes
* **Distancia:** Manhattan hexagonal: `dist(a, b) = (|a.q - b.q| + |a.q + a.r - b.q - b.r| + |a.r - b.r|) / 2`

### Entidades Base
* **Unidades:** Infantería, Oficial, Capitán
* **Estados:** Activo, Desbandada, Retirada
* **Pool de Órdenes:** `(Oficiales × 1) + (Capitán × 3)`

### Ciclo WEGO (Simultaneous Movement)

#### Fase 1: PLANIFICACIÓN (Secretas)
- **Duración:** Activa mientras hay órdenes disponibles (pool > 0)
- **Visibilidad:** Órdenes completamente ocultas para jugadores
- **Interacción:** Cada jugador coloca TODAS sus órdenes haciendo click en hexágonos
- **Contador:** Pool visible solo para jugador actual
- **Hot Seat:** Botón "Cambiar Jugador" oculta órdenes previas, reinicia UI
- **Finalización:** Ambos jugadores agotan pool (ó declara órdenes listas)

#### Fase 2: EJECUCIÓN (Visibles)
1. **Resolución Simultánea de Órdenes**
   - Todas las órdenes ejecutan en paralelo (WEGO)
   - Órdenes ahora VISIBLES en el tablero

2. **Subfase de Movimiento**
   - Ejecución de DEPLOY, MOVE
   - Detección de colisiones

3. **Subfase de Combate**
   - Combate Determinista: Comparación de fuerzas
   - Combate Estocástico: Brújula si hay empate

4. **Post-procesado**
   - Retiradas, Desbandadas
   - Limpieza: Regla de los 5 Hexágonos
   - Eliminación de unidades aisladas

#### Fase 3: RESET
- Limpieza de estado de ejecución
- Reinicio de pools de órdenes
- Vuelta a PLANIFICACIÓN

### Mecánica de Brújula
* **Trigger:** Combate con deltas de fuerza iguales
* **Input:** Ángulo jugador (0-359°) vs. ángulo objetivo
* **Resolución:** Menor diferencia angular gana

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
│  [Click-to-cycle orders on hexes]  │
│                                     │
│     [Scrolleable + Zoomeable]       │
└─────────────────────────────────────┘
    [Start Game] [Cambiar Jugador]
```

**Capas Flet:**
1. **Canvas Static:** Grid hexagonal (dibujado una vez)
2. **Canvas Dynamic:** Unidades y órdenes pendientes (visibles solo en EJECUCIÓN)
3. **GestureDetector:** Input de tap-cycling de órdenes
4. **UI Overlay:** Botones (Start Game, Cambiar Jugador)

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

#### Botón "Cambiar Jugador"
- **Estilo:** Minimalista, discreto (pequeño, 60px altura, esquina inferior derecha)
- **Posición:** Bottom-right corner (fixed, pequeño offset)
- **Visibilidad:** Siempre presente durante PLANIFICACIÓN
- **Acción:** Oculta las órdenes del jugador actual → Cambia de jugador → Reinicia contador de órdenes
- **Comportamiento:** En EJECUCIÓN, permite avanzar al siguiente turno después de resolución

#### Sistema de Tap Cycling (Selección de Órdenes)

**Flujo General:**
1. Jugador hace click en hexágono origen (donde hay unidad propia)
2. Sistema activa ese hexágono y sus 6 hexágonos adyacentes
3. Clicks sucesivos en hexágonos ciclan órdenes en secuencia precisa
4. Click en origen nuevamente para modificar o cancelar

**Ciclo del Hexágono de Origen:**
- **Click 1:** Activa como ORIGEN (visual: highlight + muestra adyacentes activos)
- **Click 2:** Cambia a DEFENSA (visual: icono DEFENSA visible)
- **Click 3:** Cancela completamente (orden devuelta al pool)

**Ciclo de Hexágonos Adyacentes (activados durante origen seleccionado):**
- **Click 1:** DEPLOY (movimiento seguro sin combate)
- **Click 2:** MOVE (movimiento con riesgo de combate)
- **Click 3:** ATTACK (ataque directo)
- **Click 4:** SUPPORT (refuerza defensa o ataque del hex adyacente)
- **Recomenzar:** Siguiente click vuelve a DEPLOY

**Cancelación de Orden Adyacente:**
- Click en hex origen nuevamente:
  - **1er click:** Pasa a DEFENSA y elimina todas las órdenes de hexágonos adyacentes
  - **2do click:** Cancela completamente (devuelve origen al pool)

**Visual Feedback:**
- Hex origen: Outline doble, color facción
- Hex adyacentes activos: Outline sencillo, semi-transparentes
- Orden aplicada: Icono de orden superpuesto, texto de tipo
- Hover feedback: Cambio de opacidad en adyacentes disponibles

### 4.5 Input y Coordenadas

* **Detección Pixel→Hex:** Conversión de click a coordenadas `(q, r)` via matriz 2x2
* **Órdenes:** Sistema de tap cycling en hexágonos (ver sección 4.4 para detalles del ciclo)
* **Brújula:** Widget visual con animaciones de rotación (trigger: empate de fuerzas)

### 4.6 Responsiveness

| Breakpoint | Layout | Hex Size | Botón Cambiar Jugador |
|-----------|--------|----------|---------|
| Desktop 1920x1080+ | Full Grid | 64px | Bottom Right (pequeño, 60px) |
| Tablet 768-1024 | Scaled Grid | 48px | Bottom Right (pequeño, 50px) |
| Mobile <768 | Zoom Default | 40px | Bottom Right (adaptado, 45px) |

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

1. Tablero generado correctamente (radio 20, sin islas inalcanzables)
2. Click→Coordenadas funcional en todas las resoluciones
3. Sistema de tap cycling preciso (origen → adyacentes → ciclos)
4. Hot seat con ocultamiento de órdenes (Cambiar Jugador)
5. Órdenes secretas en PLANIFICACIÓN, visibles en EJECUCIÓN
6. Resolución automática simultánea de movimiento y combates (WEGO)
7. Brújula como tiebreaker visual
8. Limpieza post-turno (Regla 5 Hexágonos)
9. Pool de órdenes visible solo para jugador actual

---

## 7. Estructuras de Datos Clave

### Órdenes (Enum)
```
DEPLOY, MOVE, ATTACK, SUPPORT, DEFENSE
```

**Representación Interna:**
```
orden = {
  tipo: "DEPLOY|MOVE|ATTACK|SUPPORT|DEFENSE",
  origen: (q, r),
  destino: (q, r),
  visible: False (secreto en PLANIFICACIÓN) | True (en EJECUCIÓN),
  fase: "PLANIFICACION|EJECUCION"
}
```

### Mapa (Hash Map)
```
mapa[(q, r)] = {
  terreno: "BLANCO|NEGRO",
  ocupante: ID_UNIDAD | None,
  orden_pendiente: Orden | None,
  visible_en_canvas: False (si fase == PLANIFICACION) | True (si fase == EJECUCION)
}
```

### Pool de Órdenes por Jugador
```
pool[jugador_id] = {
  disponibles: N,  # Cantidad restante de órdenes
  órdenes_activas: [Orden, ...],  # Órdenes ya colocadas (secretas si PLANIFICACION)
  jugador_actual: Boolean  # Solo true para el jugador con turno
}
```

---

## 8. Nota Técnica

La lógica de negocio debe mantenerse completamente agnóstica a la capa Flet. Las decisiones de renderizado no impactan las reglas del juego. La comunicación entre motor lógico e interfaz ocurre únicamente a través de estructuras de datos observables.

---

## 9. Guías de Implementación (Skills)

El proyecto SyV-Flet cuenta con un conjunto de guías especializadas (skills) que documentan aspectos específicos del desarrollo. Estas guías se complementan entre sí y deben consultarse según el área de trabajo.

### 9.1 Calidad y Estándares

**`code-standards`** — Define la forma del código: principios SOLID, coherencia arquitectónica, y prácticas obligatorias. Consultar SIEMPRE antes de escribir código nuevo.

### 9.2 Mecánicas de Juego

**`cycle-tap-mechanism`** — Explica con pseudocódigo todas las acciones del usuario durante la fase de PLANIFICACIÓN. Documenta:
- Tipos de órdenes (DEPLOY, MOVE, ATTACK, SUPPORT, DEFENSE)
- Secuencias de tap cycling (origen → adyacentes)
- Construcción de rutas multi-hexágono (MOVEMENT paths)
- Pool de órdenes y consumo

**Ejemplo de flujo (pseudocódigo):**
```
AL HACER CLICK en hexágono origen:
  SI origen tiene unidad propia:
    Activar origen (outline doble, color facción)
    Mostrar 6 hexágonos adyacentes disponibles

AL HACER CLICK en hexágono adyacente:
  SI es primer click: Orden = DEPLOY
  SI es segundo click: Orden = MOVE
  SI es tercer click: Orden = ATTACK
  SI es cuarto click: Orden = SUPPORT
  Ciclo vuelve a DEPLOY
```

### 9.3 Matemática de Grilla Hexagonal

**`hex-grid-math`** — Referencia rápida de operaciones con coordenadas hexagonales (pseudocódigo genérico):
- Distancia entre hexágonos
- Vecinos adyacentes (6 direcciones)
- Conversión píxel ↔ coordenadas
- Líneas de visión y anillos

**Ejemplo de cálculo de distancia:**
```
distancia(hex_a, hex_b):
  q1, r1 = hex_a
  q2, r2 = hex_b
  s1 = -q1 - r1
  s2 = -q2 - r2
  RETORNAR (|q1-q2| + |r1-r2| + |s1-s2|) / 2
```

### 9.4 Renderizado con Flet

**`hex-grid-flet-rendering`** — Implementación técnica del canvas de Flet para la grilla hexagonal:
- Dibujo de hexágonos en canvas
- Detección de clicks → coordenadas
- Scroll y zoom del tablero
- Renderizado de overlays (órdenes, iconos)

**`ux-ui-flet-rendering`** — Interfaz completa de usuario con Flet:
- Layouts y estructura de pantallas
- Botones (Start Game, Cambiar Jugador)
- Sistema de feedback visual
- Responsive design y breakpoints
- Integra `hex-grid-flet-rendering` como componente central

**Relación:** `ux-ui-flet-rendering` es la interfaz completa que incluye `hex-grid-flet-rendering` para la grilla.

### 9.5 Testing y Entorno

**`testing-framework`** — Filosofía BDD (Behavior-Driven Development) para testing. Define:
- Tests como casos de uso (no detalles de implementación)
- Organización de fixtures por estados de juego
- Cobertura objetivo: 80%+ en engine logic

**`dev-environment`** — Configuración del entorno de desarrollo (Python 3.12+, uv, dependencias).

### 9.6 Arquitectura de Estados

**`state-machine`** — Máquina de estados del juego (a documentar). Definirá:
- Transiciones entre fases (PLANIFICACIÓN → EJECUCIÓN → RESET)
- Eventos y guards de estado
- Gestión de turnos y resolución de órdenes
