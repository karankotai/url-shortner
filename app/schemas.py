from pydantic import BaseModel, HttpUrl
from datetime import datetime

class ShortenRequest(BaseModel):
    url: HttpUrl

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str

class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
