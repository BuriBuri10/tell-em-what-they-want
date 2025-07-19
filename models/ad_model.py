from pydantic import BaseModel
from typing import Optional


class AdCreative(BaseModel):
    """
    Represents an AI-generated ad creative.
    """
    headline: str
    description: str
    call_to_action: Optional[str]
    persona_segment: Optional[str] = None
