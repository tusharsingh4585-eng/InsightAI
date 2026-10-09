from pydantic import BaseModel
from typing import Any

class InsightResponse(BaseModel):
    dataset_id: int
    summary: dict[str, Any]
    insights: list[str]
    trend: list[dict[str, Any]]
