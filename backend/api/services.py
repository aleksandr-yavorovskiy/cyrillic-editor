from io import BytesIO
import logging
from dataclasses import dataclass

from api.core.base import BaseService
from api.core.exceptions import UnsupportedFormatError
from api.compilers.latex import LatexCompiler, LatexBuilder
from api.converters.files import ConverterRegistry
from api.processors.text import create_default_pipeline


logger = logging.getLogger("api")


@dataclass
class CompileOptions:
    font: str = ""
    fontSize: int = 14
    top: int = 2
    bottom: int = 2
    left: int = 2
    right: int = 2


@dataclass
class ImportOptions:
    filename: str = ""


@dataclass
class ExportOptions:
    format: str = ".docx"


class CompilationService(BaseService):
    _instance = None

    def __new__(cls, compiler=None, builder=None, pipeline=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._compiler = compiler or LatexCompiler()
            cls._instance._builder = builder or LatexBuilder()
            cls._instance._pipeline = pipeline or create_default_pipeline()
        return cls._instance

    def __init__(self, compiler=None, builder=None, pipeline=None):
        super().__init__()
        self._compiler = compiler or LatexCompiler()
        self._builder = builder or LatexBuilder()
        self._pipeline = pipeline or create_default_pipeline()

    def compile(self, text: str, options: CompileOptions) -> BytesIO:
        self.logger.info(f"Compiling text ({len(text)} chars)")

        processed = self._pipeline.process(text)
        source = self._builder.build(processed, vars(options))

        result = self._compiler.compile(source)
        self.logger.info("Compilation successful")
        return result

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class ImportService(BaseService):
    _instance = None

    def __new__(cls, registry: ConverterRegistry = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = registry or ConverterRegistry()
        return cls._instance

    def __init__(self, registry: ConverterRegistry = None):
        super().__init__()
        self._registry = registry or ConverterRegistry()

    def import_file(self, file_data: BytesIO, filename: str) -> str:
        self.logger.info(f"Importing file: {filename}")

        ext = self._registry.detect_extension(filename)
        importer = self._registry.get_importer(ext)

        if not importer:
            raise UnsupportedFormatError(f"Unsupported format: {ext}")

        result = importer.convert(file_data)
        self.logger.info(f"Import successful ({len(result)} chars)")
        return result

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class ExportService(BaseService):
    _instance = None

    def __new__(cls, registry: ConverterRegistry = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = registry or ConverterRegistry()
        return cls._instance

    def __init__(self, registry: ConverterRegistry = None):
        super().__init__()
        self._registry = registry or ConverterRegistry()

    def export(self, text: str, format: str = ".docx") -> BytesIO:
        self.logger.info(f"Exporting to {format}")

        exporter = self._registry.get_exporter(format)

        if not exporter:
            raise UnsupportedFormatError(f"Unsupported export format: {format}")

        result = exporter.export(text)
        self.logger.info("Export successful")
        return result

    def get_available_formats(self) -> list:
        return list(self._registry.exporters.keys())

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
