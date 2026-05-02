from unittest.mock import Mock
from io import BytesIO

from api.services import CompilationService, CompileOptions


class TestCompileOptions:
    def test_default_values(self):
        options = CompileOptions()
        assert options.fontSize == 14
        assert options.top == 2


class TestCompilationService:
    def test_compile_success(self):
        service = CompilationService(
            compiler=Mock(), builder=Mock(), pipeline=Mock()
        )
        service._pipeline.process.return_value = "processed"
        service._builder.build.return_value = "latex"
        service._compiler.compile.return_value = BytesIO(b'pdf')

        options = CompileOptions()
        result = service.compile("test text", options)
        assert isinstance(result, BytesIO)
