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

## 3. Mecánica de Juego

### Sistema de Coordenadas
* **Modelo:** Coordenadas cúbicas `(q, r, s)` donde `q + r + s = 0`, proyectadas a coordenadas axiales `(q, r)` para optimización de memoria (ver [Documentación Técnica: Grillas Hexagonales](./.claude/docs/about-hexagonal-coordinates.md))
* **Tablero:** Radio R=20 (fórmula: `3*R*(R+1) + 1` = 1,261 hexágonos)
* **Adyacencia:** 6 vecinos inmediatos calculados mediante vectores de dirección constantes
* **Distancia:** Manhattan hexagonal: `dist(a, b) = (|a.q - b.q| + |a.q + a.r - b.q - b.r| + |a.r - b.r|) / 2`

### Entidades Base
* **Unidades:** Infantería, Oficial, Capitán
* **Estados:** Activo, Desbandada, Retirada
* **Pool de Órdenes:** `(Oficiales × 1) + (Capitán × 3)`

### Resolución de Turno (Loop Principal)
1. Fase de Movimiento → Colisiones
2. Fase de Combate Determinista (comparación de fuerzas)
3. Fase de Combate Estocástico (Brújula si empate)
4. Post-procesado: Retiradas, Desbandadas, Limpieza de unidades aisladas

### Mecánica de Brújula
* **Trigger:** Combate con deltas de fuerza iguales
* **Input:** Ángulo jugador (0-359°) vs. ángulo objetivo
* **Resolución:** Menor diferencia angular gana

### Regla de los 5 Hexágonos
* Elimina unidades aisladas de sus oficiales (distancia > 5 hexágonos)
* Cálculo de distancia: Manhattan hexagonal

---

## 4. Interfaz de Usuario (Flet)

### Arquitectura Visual
* **Stack principal** con capas: Fondo → Grid → Terreno/Unidades → Overlays
* **Canvas dinámico** para hex activos y sprites de unidades
* **GestureDetector** para input de coordenadas

### Input y Controles
* **Detección Pixel→Hex:** Conversión de click a coordenadas `(q, r)`
* **Órdenes:** Selección de unidad → Hotspots en aristas (drag/click)
* **Brújula:** Widget visual con animaciones de rotación

### Requisitos de Rendimiento
* 60 FPS en Desktop y Mobile
* Renderizado escalable del grid hexagonal

---

## 5. Criterios de Aceptación (MVP)

1. ✓ Tablero generado correctamente (radio 20, sin islas inalcanzables)
2. ✓ Click→Coordenadas funcional en todas las resoluciones
3. ✓ Interfaz secuencial de órdenes (J1 → J2)
4. ✓ Resolución automática de movimiento y combates
5. ✓ Brújula como tiebreaker visual
6. ✓ Limpieza post-turno (Regla 5 Hexágonos)

---

## 6. Estructuras de Datos Clave

### Órdenes (Enum)
```
ATACAR, ATACAR_TODO, APOYAR, MOVER, DESPLEGAR, DEFENDER, DEFENDER_TODO
```

### Mapa (Hash Map)
```
mapa[(q, r)] = {
  terreno: "BLANCO|NEGRO",
  ocupante: ID_UNIDAD | None,
  orden_pendiente: Orden | None
}
```

---

## 7. Nota Técnica

La lógica de negocio debe mantenerse completamente agnóstica a la capa Flet. Las decisiones de renderizado no impactan las reglas del juego. La comunicación entre motor lógico e interfaz ocurre únicamente a través de estructuras de datos observables.
