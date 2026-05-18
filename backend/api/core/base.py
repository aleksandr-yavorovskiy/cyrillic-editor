from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import logging

from .exceptions import ValidationError


@dataclass
class BaseConfig:
    pass


class BaseService(ABC):
    def __init__(self, config: BaseConfig = None):
        self.config = config or BaseConfig()
        self._logger = logging.getLogger(f"api.{self.__class__.__name__}")

    @property
    def logger(self):
        return self._logger


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        pass

    @staticmethod
    def validate_text(text: str) -> None:
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        if len(text) > 10_000_000:
            raise ValidationError("Text too large (max 10MB)")


class BaseImporter(ABC):
    @abstractmethod
    def convert(self, source: Any) -> Any:
        pass


class BaseExporter(ABC):
    @abstractmethod
    def export(self, text: str, options=None) -> Any:
        pass


class BaseCompiler(ABC):
    @abstractmethod
    def compile(self, source: str) -> Any:
        pass

    @staticmethod
    def validate_source(source: str) -> None:
        if not source or not isinstance(source, str):
            raise ValidationError("Source must be a non-empty string")
