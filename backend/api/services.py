import dataclasses
from io import BytesIO

from api.core.base import BaseService
from api.core.exceptions import UnsupportedFormatError
from api.core.options import CompileOptions
from api.compilers.latex import LatexCompiler, LatexBuilder
from api.converters.files import ConverterRegistry
from api.processors.text import create_default_pipeline


class CompilationService(BaseService):
    def __init__(self, compiler=None, builder=None, pipeline=None):
        super().__init__()
        self._compiler = compiler or LatexCompiler()
        self._builder = builder or LatexBuilder()
        self._pipeline = pipeline or create_default_pipeline()

    def compile(self, text: str, options: CompileOptions) -> BytesIO:
        self.logger.info(f"Compiling text ({len(text)} chars)")

        processed = self._pipeline.process(text)
        source = self._builder.build(processed, dataclasses.asdict(options))

        result = self._compiler.compile(source)
        self.logger.info("Compilation successful")
        return result


class ImportService(BaseService):
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


class ExportService(BaseService):
    def __init__(self, registry: ConverterRegistry = None):
        super().__init__()
        self._registry = registry or ConverterRegistry()

    def export(self, text: str, format: str = ".docx", options=None) -> BytesIO:
        self.logger.info(f"Exporting to {format}")

        exporter = self._registry.get_exporter(format)

        if not exporter:
            raise UnsupportedFormatError(f"Unsupported export format: {format}")

        result = exporter.export(text, options=options)
        self.logger.info("Export successful")
        return result

    def get_available_formats(self) -> list:
        return list(self._registry.exporters.keys())
