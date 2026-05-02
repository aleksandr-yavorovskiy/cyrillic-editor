import pytest
from unittest.mock import Mock
from api.processors.text import LatexEscaper, SoftBreaksProcessor, ProcessingPipeline
from api.core.exceptions import ValidationError


class TestLatexEscaper:
    def setup_method(self):
        self.escaper = LatexEscaper()

    def test_escape_ampersand(self):
        result = self.escaper.process("Hello & World")
        assert r"\&" in result

    def test_escape_percent(self):
        result = self.escaper.process("50% done")
        assert r"\%" in result

    def test_escape_dolar(self):
        result = self.escaper.process("$100")
        assert r"\$" in result

    def test_escape_hash(self):
        result = self.escaper.process("#heading")
        assert r"\#" in result

    def test_escape_underscore(self):
        result = self.escaper.process("file_name")
        assert r"\_" in result

    def test_escape_curly_braces(self):
        result = self.escaper.process("{text}")
        assert r"\{" in result
        assert r"\}" in result

    def test_escape_newlines(self):
        result = self.escaper.process("line1\nline2")
        assert r"\\" in result

    def test_multiple_special_chars(self):
        result = self.escaper.process("a&b%c$d#e_f{g}h")
        assert r"\&" in result
        assert r"\%" in result
        assert r"\$" in result

    def test_validate_text_non_string(self):
        with pytest.raises(ValidationError, match="must be a string"):
            LatexEscaper.validate_text(123)

    def test_validate_text_none(self):
        with pytest.raises(ValidationError, match="must be a string"):
            LatexEscaper.validate_text(None)


class TestSoftBreaksProcessor:
    def setup_method(self):
        self.processor = SoftBreaksProcessor(threshold=15)

    def test_short_words_unchanged(self):
        result = self.processor.process("hello world")
        assert result == "hello world"

    def test_long_word_gets_split(self):
        processor = SoftBreaksProcessor(threshold=5)
        result = processor.process("hellooooo")
        assert r"\seqsplit{" in result
        assert result == r"\seqsplit{hellooooo}"

    def test_mixed_words(self):
        processor = SoftBreaksProcessor(threshold=5)
        result = processor.process("hi hellooooo world")
        assert r"\seqsplit{" in result
        assert "hi" in result
        assert "world" in result

    def test_custom_threshold(self):
        processor = SoftBreaksProcessor(threshold=3)
        result = processor.process("hello")
        assert r"\seqsplit{" in result

    def test_validate_text_non_string(self):
        processor = SoftBreaksProcessor()
        with pytest.raises(ValidationError):
            processor.process(123)

    def test_process_multiple_long_words(self):
        processor = SoftBreaksProcessor(threshold=5)
        result = processor.process("hellooooo worlddddd")
        assert result.count(r"\seqsplit{") == 2


class TestProcessingPipeline:
    def test_empty_pipeline(self):
        pipeline = ProcessingPipeline()
        result = pipeline.process("test")
        assert result == "test"

    def test_single_processor(self):
        mock_processor = Mock()
        mock_processor.process.return_value = "processed"
        pipeline = ProcessingPipeline([mock_processor])
        result = pipeline.process("test")
        assert result == "processed"
        mock_processor.process.assert_called_once_with("test")

    def test_multiple_processors(self):
        mock1 = Mock()
        mock1.process.return_value = "step1"
        mock2 = Mock()
        mock2.process.return_value = "step2"

        pipeline = ProcessingPipeline([mock1, mock2])
        result = pipeline.process("test")

        assert result == "step2"
        mock1.process.assert_called_once_with("test")
        mock2.process.assert_called_once_with("step1")

    def test_add_processor(self):
        pipeline = ProcessingPipeline()
        mock_processor = Mock()
        pipeline.add(mock_processor)
        assert len(pipeline._processors) == 1

    def test_add_processor_returns_self_for_chaining(self):
        pipeline = ProcessingPipeline()
        mock_processor = Mock()
        result = pipeline.add(mock_processor)
        assert result is pipeline


class TestCreateDefaultPipeline:
    def test_creates_pipeline_with_default_processors(self):
        from api.processors.text import create_default_pipeline
        pipeline = create_default_pipeline()
        assert isinstance(pipeline, ProcessingPipeline)
        assert len(pipeline._processors) == 2
