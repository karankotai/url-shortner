from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.models import ShortLink
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.cache import get_cached_url, set_cached_url

app = FastAPI(title="URL Shortner", version="1.0.0")

BASE_URL = "http://localhost:8000"

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        result.append(ALPHABET[num%62])
        num //= 62
    return "".join(reversed[result])

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)