import logging
from typing import TypeVar, Callable
from functools import wraps

logger = logging.getLogger("api")


class APIError(Exception):
    status_code = 500

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class ValidationError(APIError):
    status_code = 400


class NotFoundError(APIError):
    status_code = 404


class UnsupportedFormatError(APIError):
    status_code = 400


class CompilationError(APIError):
    status_code = 500


class FileProcessingError(APIError):
    status_code = 500


T = TypeVar("T")


def handle_errors(func: Callable[..., T]) -> Callable[..., T | dict]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.message}")
            return {"error": e.message}
        except UnsupportedFormatError as e:
            logger.warning(f"Unsupported format: {e.message}")
            return {"error": e.message}
        except NotFoundError as e:
            logger.warning(f"Not found: {e.message}")
            return {"error": e.message}
        except FileProcessingError as e:
            logger.error(f"File processing error: {e.message}")
            return {"error": e.message}
        except CompilationError as e:
            logger.error(f"Compilation error: {e.message}")
            return {"error": e.message}
        except APIError as e:
            logger.error(f"API error: {e.message}")
            return {"error": e.message}
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return {"error": "Internal server error"}

    return wrapper
