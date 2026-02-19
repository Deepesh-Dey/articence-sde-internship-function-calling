
from pydantic import BaseModel
from typing import Any, List, Optional


class Metadata(BaseModel):
    total_results: int
    returned_results: int
    data_freshness: str
    data_type: Optional[str] = None
    source: Optional[str] = None
    context_message: Optional[str] = None
    voice_summary: Optional[str] = None  # Short phrase for TTS when voice=true


class DataResponse(BaseModel):
    data: List[Any]
    metadata: Metadata

