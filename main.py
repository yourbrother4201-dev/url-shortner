import secrets
import sqlite3
import string
import time
from contextlib import asynccontextmanager
from urllib.parse import urlparse


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl


DATABASE = "urls.db"
CODE_LENGTH = 7
CACHE_TTL = 300
ALPHABET = string.ascii_letters + string.digits


cache = {}
access_counts = {}

CACHE_TTL = 300
POPULAR_THRESHOLD = 3


def get_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                long_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="URL Shortener API",
    description="Create short URLs and redirect to original links.",
    lifespan=lifespan,
)


class URLRequest(BaseModel):
    long_url: HttpUrl


def generate_code():
    return "".join(
        secrets.choice(ALPHABET)
        for _ in range(CODE_LENGTH)
    )



def get_cached_url(short_code):
    entry = cache.get(short_code)

    if entry is None:
        return None

    long_url, expires_at = entry

    if time.monotonic() >= expires_at:
        cache.pop(short_code, None)
        return None

    return long_url



@app.post("/api/urls", status_code=201)
def create_short_url(data: URLRequest, request: Request):
    long_url = str(data.long_url)
    parsed = urlparse(long_url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(
            status_code=400,
            detail="Only valid HTTP and HTTPS URLs are allowed."
        )

    
    for _ in range(10):
        short_code = generate_code()

        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
                    (short_code, long_url),
                )
            break

        except sqlite3.IntegrityError:
            continue
    else:
        raise HTTPException(
            status_code=503,
            detail="Could not generate a unique code. Try again."
        )

    return {
        "short_code": short_code,
        "short_url": str(request.base_url) + short_code,
        "long_url": long_url,
    }


@app.get("/{short_code}")
def redirect_url(short_code: str):
    # 1. Check cache first.
    long_url = get_cached_url(short_code)


    if long_url is None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT long_url FROM urls WHERE short_code = ?",
                (short_code,),
            ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found."
            )

        long_url = row["long_url"]

        
        access_counts[short_code] = access_counts.get(short_code, 0) + 1

# Cache only popular links.
        if access_counts[short_code] >= POPULAR_THRESHOLD:
            cache[short_code] = (
                long_url,
                time.monotonic() + CACHE_TTL,
            )


    
    return RedirectResponse(
        url=long_url,
        status_code=302,
    )
