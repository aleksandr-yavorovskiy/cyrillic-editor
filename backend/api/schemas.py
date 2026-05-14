from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str
    font: str = ""
    fontSize: int = Field(default=14, ge=8, le=72)
    top: float = Field(default=2, ge=0)
    bottom: float = Field(default=2, ge=0)
    left: float = Field(default=2, ge=0)
    right: float = Field(default=2, ge=0)
