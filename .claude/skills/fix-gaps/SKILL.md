# Fix Gaps Skill

**Nombre:** `fix-gaps`
**Comando:** `/fix-gaps`
**Propósito:** Solucionar recursivamente los gaps técnicos identificados en el ante-proyecto SyV-Flet

---

## Descripción

Este skill gestiona la resolución sistemática de **gaps técnicos y de documentación** identificados durante el análisis del proyecto. Mantiene estado persistente para continuar donde se dejó y genera feedback semántico de cada corrección.

**Características:**
- ✅ Checklist con estado persistente (YAML)
- ✅ Feedback semántico de cada corrección (Markdown)
- ✅ Ejecución recursiva (continúa automáticamente)
- ✅ Priorización por criticidad

---

## Uso

### Comando básico
```bash
/fix-gaps
```

Ejecuta el siguiente gap pendiente en la checklist y genera feedback.

### Con argumentos opcionales
```bash
/fix-gaps --item <id>        # Solucionar gap específico por ID
/fix-gaps --status           # Ver estado del checklist
/fix-gaps --reset            # Reiniciar checklist (requiere confirmación)
```

---

## Checklist de Gaps

**Ubicación:** `.claude/skills/fix-gaps/checklist.yaml`

### Estructura

```yaml
version: "1.0"
last_updated: "2026-01-18"
progress:
  total: 15
  completed: 0
  pending: 15

gaps:
  # Prioridad CRÍTICA (🔴)
  - id: GAP-001
    priority: critical
    category: dependencies
    title: "Agregar PyYAML a dependencias"
    status: pending
    blocker: true
    description: |
      pyproject.toml requiere pyyaml>=6.0.0 para cargar configs.yaml
    solution_spec: |
      - Ejecutar: uv add pyyaml>=6.0.0
      - Verificar: uv lock
      - Validar: import yaml en Python

  - id: GAP-002
    priority: critical
    category: skills
    title: "Crear skill: combat-resolution"
    status: pending
    blocker: true
    description: |
      No existe especificación de cómo calcular fuerza en combate.
      PRD menciona "mayor fuerza gana, empate = estático" pero no algoritmo.
    solution_spec: |
      - Definir cálculo de fuerza base por UnitType
      - Especificar modificadores de terreno
      - Definir reglas de flanking/support
      - Documentar resolución de empates
      - Crear ejemplos de combate
      - Integrar con testing-framework

  - id: GAP-003
    priority: critical
    category: skills
    title: "Crear skill: order-execution"
    status: pending
    blocker: true
    description: |
      No hay pipeline definido para ejecutar órdenes en EXECUTION phase.
      ¿Secuencial o paralelo? ¿Conflictos de movimiento?
    solution_spec: |
      - Definir orden de ejecución (FIFO, prioridad, simultáneo)
      - Resolver conflictos de destino (dos unidades → mismo hex)
      - Especificar animación/timing
      - Documentar cancelación de órdenes inválidas
      - Integrar con state-machine

  # Prioridad ALTA (🟡)
  - id: GAP-004
    priority: high
    category: skills
    title: "Crear skill: five-hex-rule"
    status: pending
    blocker: false
    description: |
      Regla 5 Hexágonos mencionada pero algoritmo no especificado.
      ¿Cómo detectar unidades aisladas? ¿BFS/DFS?
    solution_spec: |
      - Definir algoritmo de conectividad (BFS recomendado)
      - Especificar cuándo se ejecuta (RESET phase)
      - Documentar casos edge (tablero vacío, islas múltiples)
      - Crear ejemplos visuales

  - id: GAP-005
    priority: high
    category: skills
    title: "Crear skill: animation-framework"
    status: pending
    blocker: false
    description: |
      No hay especificación de timing, easing, secuencias de animación.
      UI necesita transiciones definidas.
    solution_spec: |
      - Definir duración de transiciones (PhaseTransition → GameScreen)
      - Especificar easing functions (linear, ease-in-out, etc.)
      - Documentar secuencias de combate (attack animation)
      - Definir FPS target y performance budget
      - Integrar con ux-ui-flet-rendering

  - id: GAP-006
    priority: high
    category: skills
    title: "Completar skill: logging"
    status: pending
    blocker: false
    description: |
      logging skill actual está al 30%. Falta implementación real.
      logging_config.py existe pero no está integrado.
    solution_spec: |
      - Definir niveles (DEBUG, INFO, WARNING, ERROR)
      - Especificar sinks (console, file, rotation)
      - Documentar contexto injection (user_id, turn_number)
      - Integrar logging_config.py con GameController
      - Crear ejemplos de uso

  # Prioridad MEDIA (🟢)
  - id: GAP-007
    priority: medium
    category: skills
    title: "Crear skill: error-handling"
    status: pending
    blocker: false
    description: |
      No existe estrategia de manejo de errores.
      ¿Qué pasa con estados inválidos, movimientos ilegales?
    solution_spec: |
      - Definir excepciones custom (InvalidOrderError, IllegalMoveError)
      - Especificar recovery strategies
      - Documentar validación en boundaries
      - Integrar con logging

  - id: GAP-008
    priority: medium
    category: architecture
    title: "Definir config initialization"
    status: pending
    blocker: false
    description: |
      Template example-config.yaml existe pero no hay spec de carga.
      ¿Cuándo se carga? ¿Validación? ¿Path exacto?
    solution_spec: |
      - Crear config_loader.py en src/syv_flet/engine/
      - Definir validación con Pydantic
      - Especificar error handling (missing config, invalid YAML)
      - Documentar orden de inicialización (env vars > configs.yaml > defaults)

  - id: GAP-009
    priority: medium
    category: ui
    title: "Especificar transition timing"
    status: pending
    blocker: false
    description: |
      PhaseTransitionScreen → GameScreen: ¿fade? ¿instant?
      EXECUTION animations: ¿simultáneas? ¿secuenciales?
    solution_spec: |
      - Definir fade duration (recomendado: 300ms)
      - Especificar overlay opacity transition
      - Documentar EXECUTION sequence timing
      - Integrar con animation-framework

  - id: GAP-010
    priority: medium
    category: ui
    title: "Completar input feedback"
    status: pending
    blocker: false
    description: |
      Tap → hex highlight definido, pero faltan haptic/audio/error states.
    solution_spec: |
      - Especificar haptic feedback (mobile, intensidad)
      - Definir audio cues opcionales
      - Documentar error states visuales (invalid move, red flash)
      - Integrar con ux-ui-flet-rendering

  - id: GAP-011
    priority: medium
    category: ui
    title: "Definir loading states"
    status: pending
    blocker: false
    description: |
      ¿Qué muestra durante carga de assets?
      ¿Progress bar? ¿Splash screen?
    solution_spec: |
      - Crear splash screen spec (logo, progress bar)
      - Definir lazy loading strategy
      - Especificar timeout handling
      - Integrar con assets-manager

  - id: GAP-012
    priority: medium
    category: ui
    title: "Completar order path visualization"
    status: pending
    blocker: false
    description: |
      Waypoints (max 3) mencionados pero visualización incompleta.
      ¿Flechas? ¿Colores por tipo de orden?
    solution_spec: |
      - Definir estilo de línea (dashed, solid, arrow heads)
      - Especificar colores por OrderType
      - Documentar waypoint rendering (circles, numbers)
      - Integrar con hex-grid-flet-rendering

  # Prioridad BAJA (⚪)
  - id: GAP-013
    priority: low
    category: consistency
    title: "Resolver nomenclatura inconsistente"
    status: pending
    blocker: false
    description: |
      ScreenState.PHASE_TRANSITION (enum) vs PhaseTransitionScreen (class)
      Mezcla de UPPERCASE y PascalCase.
    solution_spec: |
      - Documentar regla: Enums UPPERCASE, Classes PascalCase
      - Verificar consistencia en todos los skills
      - Actualizar code-standards skill

  - id: GAP-014
    priority: low
    category: consistency
    title: "Explicitar opacity values en hex-grid-flet-rendering"
    status: pending
    blocker: false
    description: |
      "HIDDEN" mencionado pero sin especificar 0.0 explícitamente.
    solution_spec: |
      - Agregar tabla de opacity values
      - Sincronizar con ux-ui-flet-rendering
      - Documentar en visual states

  - id: GAP-015
    priority: low
    category: validation
    title: "Validar completitud de skills existentes"
    status: pending
    blocker: false
    description: |
      Revisar que todos los skills tengan secciones completas.
    solution_spec: |
      - Audit checklist para cada skill
      - Verificar ejemplos, quick reference, allowed-tools
      - Asegurar consistencia de formato
```

---

## Feedback de Soluciones

**Ubicación:** `.claude/skills/fix-gaps/feedback.md`

### Formato de Feedback

Cada solución genera un bloque de feedback semántico:

```markdown
## [GAP-XXX] Título del Gap

**Fecha:** YYYY-MM-DD HH:MM
**Prioridad:** Critical/High/Medium/Low
**Categoría:** dependencies/skills/architecture/ui/consistency/validation

> **Corrección Aplicada:**
>
> [Descripción semántica de la solución implementada. Explicar QUÉ se hizo,
> POR QUÉ era necesario, y CÓMO impacta el proyecto. Sin code snippets,
> solo narrativa técnica clara.]

**Archivos Modificados:**
- `/path/to/file1`
- `/path/to/file2`

**Validación:**
- ✅ Test 1 pasado
- ✅ Test 2 pasado

**Próximo Gap:** GAP-XXX

---
```

---

## Workflow de Ejecución

### Paso 1: Leer Estado
```python
# Pseudo-código
checklist = load_yaml('.claude/skills/fix-gaps/checklist.yaml')
next_gap = find_next_pending(checklist, priority_order=['critical', 'high', 'medium', 'low'])
```

### Paso 2: Ejecutar Solución
Según `solution_spec` del gap:
- Crear archivos
- Modificar skills
- Ejecutar comandos
- Validar cambios

### Paso 3: Generar Feedback
Escribir bloque de feedback en `feedback.md` con:
- Narrativa de la corrección
- Archivos tocados
- Validación realizada

### Paso 4: Actualizar Estado
```yaml
# checklist.yaml
gaps:
  - id: GAP-XXX
    status: completed  # pending → completed
    completed_at: "2026-01-18T14:30:00Z"

progress:
  completed: 1  # incrementar
  pending: 14   # decrementar
```

### Paso 5: Recursión
Si hay más gaps pendientes:
```
→ Preguntar: "¿Continuar con GAP-XXX? (Y/n)"
→ Si Y: goto Paso 2
→ Si n: Terminar
```

---

## Criterios de Completitud

Un gap se considera **completado** cuando:
1. ✅ Solución implementada según `solution_spec`
2. ✅ Archivos validados (syntax, imports)
3. ✅ Feedback semántico generado
4. ✅ Checklist actualizado
5. ✅ Tests pasando (si aplica)

---

## Ejemplos de Uso

### Ejemplo 1: Ejecutar próximo gap
```bash
$ /fix-gaps

🔍 Cargando checklist...
📋 Progreso: 0/15 completados

🔴 CRÍTICO: GAP-001 - Agregar PyYAML a dependencias
📝 Ejecutando solución...

✅ Solución completada
📄 Feedback generado en feedback.md

¿Continuar con GAP-002? (Y/n)
```

### Ejemplo 2: Ver estado
```bash
$ /fix-gaps --status

📊 Estado del Checklist (15 gaps)

🔴 CRÍTICOS (3):
  - GAP-001: Agregar PyYAML [PENDING]
  - GAP-002: Crear combat-resolution skill [PENDING]
  - GAP-003: Crear order-execution skill [PENDING]

🟡 ALTOS (3):
  - GAP-004: Crear five-hex-rule skill [PENDING]
  ...

Progreso: 0/15 (0%)
```

### Ejemplo 3: Solucionar gap específico
```bash
$ /fix-gaps --item GAP-005

🔍 Cargando GAP-005: Crear skill: animation-framework
🟡 ALTA PRIORIDAD
📝 Ejecutando solución...
...
```

---

## Integración con Otros Skills

Este skill coordina con:
- **code-standards** — Validar formato de código generado
- **testing-framework** — Validar que tests pasen
- **git-workflow** — Commits convencionales por gap
- **configuration-management** — Validar configs.yaml

---

## Archivos Gestionados

```
.claude/skills/fix-gaps/
├── SKILL.md ..................... Este archivo (definición del skill)
├── checklist.yaml ............... Estado del checklist (persistente)
└── feedback.md .................. Registro de correcciones (append-only)
```

---

## Notas de Implementación

### Estado Persistente
El archivo `checklist.yaml` es la **fuente de verdad**. No resetear sin confirmación explícita.

### Feedback Semántico
**SÍ:**
> La dependencia PyYAML fue agregada a pyproject.toml (versión >=6.0.0) porque el sistema de configuración centralizado requiere parsear configs.yaml durante la inicialización del motor de juego. Sin esta librería, el GameController no puede cargar parámetros críticos como board.radius, causando fallo en tiempo de ejecución. La solución incluye verificación de lockfile (uv.lock) para asegurar reproducibilidad.

**NO:**
```python
# Ejecuté: uv add pyyaml>=6.0.0
# Ahora funciona
```

### Priorización
Respetar orden de prioridad:
1. 🔴 CRITICAL (blockers primero)
2. 🟡 HIGH
3. 🟢 MEDIUM
4. ⚪ LOW

---

## Mantenimiento

### Agregar Nuevo Gap
```yaml
gaps:
  - id: GAP-016  # siguiente ID secuencial
    priority: medium
    category: nueva_categoria
    title: "Descripción corta"
    status: pending
    blocker: false
    description: |
      Explicación detallada del problema
    solution_spec: |
      - Paso 1
      - Paso 2
```

### Modificar Gap Existente
Solo permitido si `status: pending`. No editar gaps completados.

---

## Referencias

- Análisis original: `/home/kodex/.claude/plans/snazzy-sprouting-dolphin.md`
- Skills relacionados: `.claude/skills/*/SKILL.md`
- Documentación: `.claude/docs/`

---

**Versión:** 1.0
**Última Actualización:** 2026-01-18
**Mantenedor:** Claude Code (auto-gestionado)
