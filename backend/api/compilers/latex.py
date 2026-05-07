from pathlib import Path
import subprocess
import tempfile
import os
import logging
from io import BytesIO

from api.core.base import BaseCompiler
from api.core.exceptions import CompilationError, ValidationError
from api.config import config


logger = logging.getLogger("api")


class LatexCompiler(BaseCompiler):
    def __init__(self, font_dir: Path = None):
        self.font_dir = font_dir or config.FONT_DIR

    def compile(self, source: str) -> BytesIO:
        self.validate_source(source)

        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "file.tex")

            try:
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(source)
            except OSError as e:
                raise CompilationError(f"Failed to write TeX source: {e}")

            try:
                result = subprocess.run(
                    ["xelatex", "-interaction=nonstopmode", "file.tex"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=config.XELATEX_TIMEOUT_SEC,
                )
            except subprocess.TimeoutExpired:
                logger.error(f"LaTeX compilation timed out after {config.XELATEX_TIMEOUT_SEC}s")
                raise CompilationError(f"LaTeX compilation timed out after {config.XELATEX_TIMEOUT_SEC}s")

            if result.returncode != 0:
                error_msg = (
                    result.stderr.decode() if result.stderr else result.stdout.decode()
                )
                logger.error(f"LaTeX compilation failed: {error_msg[:500]}")
                raise CompilationError("LaTeX compilation failed")

            output_path = os.path.join(tmpdir, "file.pdf")

            if not os.path.exists(output_path):
                raise CompilationError("PDF not generated")

            with open(output_path, "rb") as f:
                return BytesIO(f.read())

    @staticmethod
    def validate_source(source: str) -> None:
        if not source or not isinstance(source, str):
            raise ValidationError("Source must be a non-empty string")


class LatexBuilder:
    def __init__(self, font_dir: Path = None):
        self.font_dir = font_dir or config.FONT_DIR

    def build(self, text: str, options: dict) -> str:
        font = options.get("font", "")
        font_path = str(self.font_dir) + "/"

        top = f"{options.get('top', config.DEFAULT_MARGIN_CM)}cm"
        bottom = f"{options.get('bottom', config.DEFAULT_MARGIN_CM)}cm"
        left = f"{options.get('left', config.DEFAULT_MARGIN_CM)}cm"
        right = f"{options.get('right', config.DEFAULT_MARGIN_CM)}cm"

        font_size = int(options.get("fontSize", config.DEFAULT_FONT_SIZE))
        line_height = int(font_size * config.LATEX_LINE_HEIGHT_MULTIPLIER)

        return rf"""\documentclass{{article}}
\usepackage{{fontspec}}
\usepackage{{seqsplit}}
\usepackage[margin=1in]{{geometry}}

\setmainfont{{{font}}}[
    Path={font_path}
]

\geometry{{
  top={top},
  bottom={bottom},
  left={left},
  right={right}
}}

\pagestyle{{empty}}

\begin{{document}}
\noindent {{\fontsize{{{font_size}}}{{{line_height}}}\selectfont {text}}}\end{{document}}
"""
