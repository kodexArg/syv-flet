# Logging System

## Setup
```python
from src.logging_config import logger
```

## Usage
```python
logger.debug("mensaje de debug")
logger.info("info importante")
logger.warning("advertencia")
logger.error("error capturado")
logger.critical("fallo crítico")
```

## Rules
- **Errores excepcionales:** `try/except` con `logger.error()` y `traceback`
- **Flujo normal:** `logger.info()` en checkpoints clave (inicio turno, combate, etc)
- **Debug:** `logger.debug()` para transiciones de estado
- **Todos los errores van a STDERR + logs/**

## Output
- `logs/debug.log` — Todo en DEBUG
- `logs/error.log` — Errores solamente
- `logs/YYYY-MM-DD.log` — Rotación diaria (INFO+)
- `STDERR` — Todos los niveles en color
