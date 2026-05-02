import pytest
from unittest.mock import Mock, patch
from io import BytesIO

from api.converters.files import (
    TextImporter, DocxImporter, PdfImporter, DocxExporter, ConverterRegistry
)
from api.core.exceptions import FileProcessingError


class TestTextImporter:
    def test_import_valid_utf8(self):
        content = b"Hello World"
        result = TextImporter().convert(BytesIO(content))
        assert result == "Hello World"

    def test_import_empty_file(self):
        result = TextImporter().convert(BytesIO(b""))
        assert result == ""

    def test_import_utf8_with_cyrillic(self):
        content = "Привет мир".encode('utf-8')
        result = TextImporter().convert(BytesIO(content))
        assert "Привет мир" in result

    def test_import_invalid_utf8(self):
        content = b'\xff\xfe'
        with pytest.raises(FileProcessingError, match="Failed to decode"):
            TextImporter().convert(BytesIO(content))




class TestDocxImporter:
    @patch('api.converters.files.Document')
    def test_import_valid_docx(self, mock_doc):
        mock_para1 = Mock()
        mock_para1.text = "Hello"
        mock_para2 = Mock()
        mock_para2.text = "World"
        mock_doc.return_value.paragraphs = [mock_para1, mock_para2]

        result = DocxImporter().convert(BytesIO(b"fake docx"))
        assert "Hello" in result
        assert "World" in result

    @patch('api.converters.files.Document')
    def test_import_docx_with_multiple_paragraphs(self, mock_doc):
        paragraphs = []
        for text in ["Para 1", "Para 2", "Para 3"]:
            mock_p = Mock()
            mock_p.text = text
            paragraphs.append(mock_p)
        mock_doc.return_value.paragraphs = paragraphs

        result = DocxImporter().convert(BytesIO(b"fake"))
        assert "Para 1" in result
        assert "Para 2" in result
        assert "Para 3" in result

    @patch('api.converters.files.Document')
    def test_import_docx_exception(self, mock_doc):
        mock_doc.side_effect = Exception("DOCX error")

        with pytest.raises(FileProcessingError, match="Failed to read DOCX"):
            DocxImporter().convert(BytesIO(b"fake"))


class TestPdfImporter:
    @patch('api.converters.files.PdfReader')
    def test_import_valid_pdf(self, mock_reader_cls):
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_reader_cls.return_value.pages = [mock_page1, mock_page2]

        result = PdfImporter().convert(BytesIO(b"fake pdf"))
        assert "Page 1 text" in result
        assert "Page 2 text" in result

    @patch('api.converters.files.PdfReader')
    def test_import_pdf_no_text(self, mock_reader_cls):
        mock_page = Mock()
        mock_page.extract_text.return_value = None
        mock_reader_cls.return_value.pages = [mock_page]

        with pytest.raises(FileProcessingError, match="no extractable text"):
            PdfImporter().convert(BytesIO(b"fake"))

    @patch('api.converters.files.PdfReader')
    def test_import_pdf_empty_pages(self, mock_reader_cls):
        mock_reader_cls.return_value.pages = []
        with pytest.raises(FileProcessingError, match="no extractable text"):
            PdfImporter().convert(BytesIO(b"fake"))

    @patch('api.converters.files.PdfReader')
    def test_import_pdf_exception(self, mock_reader_cls):
        mock_reader_cls.side_effect = Exception("PDF error")

        with pytest.raises(FileProcessingError, match="Failed to read PDF"):
            PdfImporter().convert(BytesIO(b"fake"))


class TestDocxExporter:
    @patch('api.converters.files.Document')
    def test_export_valid_text(self, mock_doc_cls):
        mock_doc = Mock()
        mock_doc_cls.return_value = mock_doc

        result = DocxExporter().export("Hello\nWorld")

        mock_doc.add_paragraph.assert_called()
        mock_doc.save.assert_called()
        assert isinstance(result, BytesIO)

    @patch('api.converters.files.Document')
    def test_export_empty_text(self, mock_doc_cls):
        mock_doc = Mock()
        mock_doc_cls.return_value = mock_doc

        result = DocxExporter().export("")
        assert isinstance(result, BytesIO)

    @patch('api.converters.files.Document')
    def test_export_multiline_text(self, mock_doc_cls):
        mock_doc = Mock()
        mock_doc_cls.return_value = mock_doc

        DocxExporter().export("Line 1\nLine 2\nLine 3")
        assert mock_doc.add_paragraph.call_count == 3

    @patch('api.converters.files.Document')
    def test_export_exception(self, mock_doc_cls):
        mock_doc_cls.side_effect = Exception("Export error")

        with pytest.raises(FileProcessingError, match="Failed to create DOCX"):
            DocxExporter().export("test")


class TestConverterRegistry:
    def test_register_and_get_importer(self):
        registry = ConverterRegistry()
        mock_importer = Mock()
        registry.register_importer(".test", mock_importer)
        result = registry.get_importer(".test")
        assert result is mock_importer

    def test_register_and_get_exporter(self):
        registry = ConverterRegistry()
        mock_exporter = Mock()
        registry.register_exporter(".test", mock_exporter)
        result = registry.get_exporter(".test")
        assert result is mock_exporter

    def test_get_nonexistent_importer(self):
        registry = ConverterRegistry()
        result = registry.get_importer(".xyz")
        assert result is None

    def test_get_nonexistent_exporter(self):
        registry = ConverterRegistry()
        result = registry.get_exporter(".xyz")
        assert result is None

    def test_detect_extension_txt(self):
        registry = ConverterRegistry()
        ext = registry.detect_extension("test.txt")
        assert ext == ".txt"

    def test_detect_extension_docx(self):
        registry = ConverterRegistry()
        ext = registry.detect_extension("document.docx")
        assert ext == ".docx"

    def test_detect_extension_pdf(self):
        registry = ConverterRegistry()
        ext = registry.detect_extension("file.pdf")
        assert ext == ".pdf"

    def test_detect_extension_unsupported(self):
        registry = ConverterRegistry()
        with pytest.raises(Exception, match="Unsupported file format"):
            registry.detect_extension("test.xyz")

    def test_singleton_pattern(self):
        registry1 = ConverterRegistry()
        registry2 = ConverterRegistry()
        assert registry1 is registry2

    def test_initialization(self):
        registry = ConverterRegistry()
        # Check that default importers/exporters are registered
        assert ".txt" in registry.importers
        assert ".docx" in registry.importers
        assert ".pdf" in registry.importers
        assert ".docx" in registry.exporters
