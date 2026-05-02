import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from api.compilers.latex import LatexBuilder, LatexCompiler
from api.core.exceptions import CompilationError, ValidationError
from api.config import config


class TestLatexBuilder:
    def setup_method(self):
        self.builder = LatexBuilder()

    def test_build_basic_text(self):
        text = "Hello World"
        options = {'font': 'TestFont', 'fontSize': 14}
        result = self.builder.build(text, options)

        assert '\\documentclass{article}' in result
        assert '\\usepackage{fontspec}' in result
        assert '\\usepackage{seqsplit}' in result
        assert '\\usepackage[margin=1in]{geometry}' in result
        assert text in result

    def test_build_with_font_path(self):
        options = {'font': 'TestFont', 'fontSize': 14}
        result = self.builder.build("text", options)
        assert 'Path=' in result

    def test_build_with_margins(self):
        options = {
            'font': 'TestFont',
            'fontSize': 14,
            'top': 3, 'bottom': 3, 'left': 3, 'right': 3
        }
        result = self.builder.build("text", options)
        assert 'top=3cm' in result
        assert 'bottom=3cm' in result
        assert 'left=3cm' in result
        assert 'right=3cm' in result

    def test_build_with_default_margins(self):
        options = {'font': 'TestFont', 'fontSize': 14}
        result = self.builder.build("text", options)
        assert f"top={config.DEFAULT_MARGIN_CM}cm" in result
        assert f"bottom={config.DEFAULT_MARGIN_CM}cm" in result

    def test_build_font_size(self):
        options = {'font': 'TestFont', 'fontSize': 16}
        result = self.builder.build("text", options)
        assert '16' in result

    def test_build_line_height(self):
        options = {'font': 'TestFont', 'fontSize': 12}
        result = self.builder.build("text", options)
        line_height = int(12 * config.LATEX_LINE_HEIGHT_MULTIPLIER)
        assert str(line_height) in result

    def test_build_escapes_special_chars_in_text(self):
        text = "text with $pecial"
        options = {'font': 'TestFont', 'fontSize': 14}
        result = self.builder.build(text, options)
        assert text in result

    def test_build_empty_text(self):
        options = {'font': 'TestFont', 'fontSize': 14}
        result = self.builder.build("", options)
        assert '\\end{document}' in result


class TestLatexCompiler:
    def setup_method(self):
        self.compiler = LatexCompiler()

    def test_validate_source_valid(self):
        LatexCompiler.validate_source("valid source")

    def test_validate_source_empty(self):
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            LatexCompiler.validate_source("")

    def test_validate_source_non_string(self):
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            LatexCompiler.validate_source(123)

    def test_validate_source_none(self):
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            LatexCompiler.validate_source(None)

    @patch('api.compilers.latex.subprocess.run')
    def test_compile_success(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = b""
        mock_result.stdout = b"success"
        mock_run.return_value = mock_result

        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.read.return_value = b'pdf content'

        with patch('builtins.open', return_value=mock_file), \
             patch('os.path.exists', return_value=True), \
             patch('tempfile.TemporaryDirectory') as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = Mock(return_value='/tmp/test')
            mock_tmpdir.return_value.__exit__ = Mock(return_value=False)

            result = self.compiler.compile("test latex source")
            assert isinstance(result, BytesIO)

    @patch('api.compilers.latex.subprocess.run')
    def test_compile_failure(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = b"LaTeX error"
        mock_result.stdout = b""
        mock_run.return_value = mock_result

        with patch('builtins.open', MagicMock()), \
             patch('os.path.exists', return_value=False), \
             patch('tempfile.TemporaryDirectory') as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = Mock(return_value='/tmp/test')
            mock_tmpdir.return_value.__exit__ = Mock(return_value=False)

            with pytest.raises(CompilationError, match="LaTeX compilation failed"):
                self.compiler.compile("test")

    @patch('api.compilers.latex.subprocess.run')
    def test_compile_pdf_not_generated(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with patch('builtins.open', MagicMock()), \
             patch('os.path.exists', return_value=False), \
             patch('tempfile.TemporaryDirectory') as mock_tmpdir:
            mock_tmpdir.return_value.__enter__ = Mock(return_value='/tmp/test')
            mock_tmpdir.return_value.__exit__ = Mock(return_value=False)

            with pytest.raises(CompilationError, match="PDF not generated"):
                self.compiler.compile("test")

    @patch('api.compilers.latex.subprocess.run')
    def test_compile_write_error(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = OSError("Write failed")

            with pytest.raises(CompilationError, match="Failed to write TeX source"):
                self.compiler.compile("test")
