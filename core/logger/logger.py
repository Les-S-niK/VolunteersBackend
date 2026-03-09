from functools import wraps
from os import path
from typing import Any, Callable

from loguru import logger

logs_dir: str = path.join(path.dirname(__file__), "logs")


def setup_logger(logs_dir: str = logs_dir) -> None:
    logger.add(
        path.join(logs_dir, "last.log"),
        level="INFO",
        format="{level}:\t{message}\t{time:YYYY-MM-DD HH:mm:ss}",
        rotation="10 MB",
        compression="zip",
        retention="7 days",
    )


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
        try:
            result: Any = await func(self, *args, **kwargs)
        except Exception as e:
            statement: str = getattr(self, "stmt", "None")
            message: str = f"Function: {func.__qualname__}\nAn error occured: {e}\nStatement: {statement}"
            logger.error(message)
            raise e
        return result

    return wrapper
