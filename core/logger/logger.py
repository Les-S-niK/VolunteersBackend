import datetime as dt
import logging
import sys
from functools import wraps
from os import path
from typing import Any, Callable

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        log_level: str = logger.level(record.levelname).name
        logger.opt(depth=6, exception=record.exc_info).log(
            log_level, record.getMessage()
        )


logs_dir: str = path.join(path.dirname(__file__), "logs")
logger.remove()
logger.add(
    path.join(logs_dir, f"{dt.datetime.now()}.log"),
    level="INFO",
    format="<bold>{level}</bold>:\t{message}\t{time:YYYY-MM-DD HH:mm:ss}",
    rotation="1 MB",
    compression="zip",
)
logger.add(
    sys.stdout,
    format="<green><bold>{level}</bold></green>:\t<cyan>{message}</cyan><green>{time:YYYY-MM-DD HH:mm:ss}</green>",
    level="INFO",
    colorize=True,
)
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


def database_query_logger(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.info(f"Query: {func.__name__}.\n\tArgs: {args}\n\tKwargs: {kwargs}\n")
        result: Any = func(*args, **kwargs)
        return result

    return wrapper


def execute_query_logger(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Any:
        logger.info(f"Statement: {self.stmt}\n")
        result: Any = await func(self, *args, **kwargs)
        return result

    return wrapper
