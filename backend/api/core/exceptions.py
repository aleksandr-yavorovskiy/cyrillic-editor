import logging

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
