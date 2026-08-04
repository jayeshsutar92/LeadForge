from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SearchHistoryBase(BaseModel):
    query: str
    filters: dict[str, Any]
    result_count: int


class SearchHistoryCreate(SearchHistoryBase):
    pass


class SearchHistoryResponse(SearchHistoryBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
