"""
Ejemplo minimalista de uso del sistema de logging.
Eliminar este archivo en producción.
"""

from src.logging_config import logger


def example():
    """Demuestra todos los niveles de logging."""
    logger.debug("Esto es debug - transición de estado")
    logger.info("Esto es info - evento importante")
    logger.warning("Esto es warning - situación anómala")
    logger.error("Esto es error - algo salió mal")
    logger.critical("Esto es crítico - fallo severo")

    # Capturar excepción
    try:
        x = 1 / 0
    except Exception as e:
        logger.error(f"División por cero capturada: {e}")


if __name__ == "__main__":
    example()
    print("\n✓ Logs disponibles en: logs/")
