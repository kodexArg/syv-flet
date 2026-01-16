"""
Configuración centralizada de logging con loguru.
Inicializa logs por módulo, persiste en logs/ y siempre emite a stderr.
"""
import os
import sys
from pathlib import Path
from loguru import logger

# Remover handler default
logger.remove()

# Crear directorio logs si no existe
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# DEBUG: leer variable de entorno
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LEVEL = "DEBUG" if DEBUG else "INFO"

# Handler: STDERR (siempre, todos los niveles)
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LEVEL,
    colorize=True,
)

# Handler: Archivo por módulo (DEBUG y ERROR)
logger.add(
    LOGS_DIR / "debug.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="500 MB",
    retention="7 days",
)

logger.add(
    LOGS_DIR / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="500 MB",
    retention="14 days",
)

# Handler: Archivo rotativo por nivel (INFO y superior)
logger.add(
    LOGS_DIR / "{time:YYYY-MM-DD}.log",
    format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="00:00",
    retention="30 days",
)

__all__ = ["logger", "LOGS_DIR"]
