from loguru import logger


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sink=lambda message: print(message, end=""),
        level="INFO",
        colorize=False,
        backtrace=False,
        diagnose=False,
    )
