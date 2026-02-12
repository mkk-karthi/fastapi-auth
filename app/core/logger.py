import logging
import sys

from loguru import logger

from app.core.config import settings


def configure_logger() -> None:
    # Remove default loggers to prevent duplicate logs
    logger.remove()

    # Set up logging format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Add Loguru sink (console + file)
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        "logs/server.log",
        rotation=settings.LOGGER_ROTATION,
        format=log_format,
        level="INFO",
        enqueue=True,
    )
    # logger.add(
    #     "generation.log",
    #     rotation=settings.LOGGER_ROTATION,
    #     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    #     level="INFO",
    #     enqueue=True,
    #     backtrace=False,
    #     diagnose=False,
    # )

    # Attach loguru to FastAPI
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            loguru_logger_opt = logger.opt(depth=6, exception=record.exc_info)
            loguru_logger_opt.log(record.levelno, record.getMessage())

    logging.basicConfig(handlers=[LoguruHandler()], level=0)
