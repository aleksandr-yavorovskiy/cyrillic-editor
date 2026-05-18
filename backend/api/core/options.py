from dataclasses import dataclass


@dataclass
class CompileOptions:
    font: str = ""
    fontSize: int = 14
    top: float = 2.0
    bottom: float = 2.0
    left: float = 2.0
    right: float = 2.0
