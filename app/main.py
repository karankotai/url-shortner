from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.models import ShortLink
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.cache import get_cached_url, set_cached_url

app = FastAPI(title="URL Shortner", version="1.0.0")

BASE_URL = "http://127.0.0.1:8000"

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        result.append(ALPHABET[num%62])
        num //= 62
    return "".join(reversed(result))

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    link = ShortLink(original_url=str(request.url), short_code="temp")
    db.add(link)
    db.flush()

    short_code = encode_base62(link.id)
    link.short_code = short_code
    db.commit()
    db.refresh(link)

    set_cached_url(short_code, link.original_url)

    return ShortenResponse(
        short_code=short_code,
        short_url=f"{BASE_URL}/{short_code}",
        original_url=link.original_url,
    )

@app.get("/{short_code}")
def redirect_to_url(short_code:str, db: Session=Depends(get_db)):
    # Check Redis cache first for fast lookups
    cached_url = get_cached_url(short_code)
    if cached_url:
        # Cache hit: increment clicks in the database
        db.query(ShortLink).filter(ShortLink.short_code==short_code).update({"clicks": ShortLink.clicks+1})
        db.commit()
        return RedirectResponse(url=cached_url, status_code=302)
    # Cache miss: query PostgreSQL for the original URL
    link = db.query(ShortLink).filter(ShortLink.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail = "Short link not found")
    # Backfill the cache so the next request is fast 
    set_cached_url(short_code, link.original_url)
    link.clicks += 1
    db.commit()
    return RedirectResponse(url=link.original_url, status_code=302)

@app.get("/stats/{short_code}", response_model=StatsResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    # Look up the link in the database
    link = db.query(ShortLink).filter(ShortLink.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail = "Short link not found")
    # Return the stats including click count
    return StatsResponse(
        short_code=link.short_code,
        original_url=link.original_url,
        clicks=link.clicks,
        created_at=link.created_at
    )
