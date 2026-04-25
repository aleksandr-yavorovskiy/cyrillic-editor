import re
import logging

from api.core.base import BaseProcessor
from api.core.exceptions import ValidationError


logger = logging.getLogger("api")


class LatexEscaper(BaseProcessor):
    REPLACEMENTS = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }

    def process(self, text: str) -> str:
        self.validate_text(text)
        result = text
        for char, replacement in self.REPLACEMENTS.items():
            result = result.replace(char, replacement)
        return result.replace("\n", r"\\n")

    @staticmethod
    def validate_text(text: str) -> None:
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")


class SoftBreaksProcessor(BaseProcessor):
    def __init__(self, threshold: int = 15):
        self.threshold = threshold

    def process(self, text: str) -> str:
        self.validate_text(text)
        words = text.split()
        processed = [
            f"\\seqsplit{{{word}}}" if len(word) > self.threshold else word
            for word in words
        ]
        return " ".join(processed)


class WhitespaceNormalizer(BaseProcessor):
    PATTERN = re.compile(r"\s+")

    def process(self, text: str) -> str:
        self.validate_text(text)
        return self.PATTERN.sub(" ", text).strip()


class ProcessingPipeline:
    def __init__(self, processors: list[BaseProcessor] = None):
        self._processors = processors or []

    def add(self, processor: BaseProcessor) -> "ProcessingPipeline":
        self._processors.append(processor)
        return self

    def process(self, text: str) -> str:
        result = text
        for processor in self._processors:
            result = processor.process(result)
        return result


def create_default_pipeline() -> ProcessingPipeline:
    return ProcessingPipeline(
        [
            WhitespaceNormalizer(),
            LatexEscaper(),
            SoftBreaksProcessor(),
        ]
    )
