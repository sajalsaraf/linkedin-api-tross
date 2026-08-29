from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
import httpx
from dotenv import load_dotenv

from linkedin import LinkedInClient
from models import ProfileResponse

load_dotenv()

client: LinkedInClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = LinkedInClient()
    yield


app = FastAPI(
    title="LinkedIn Profile API",
    description="Reverse-engineered LinkedIn Voyager API wrapper",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/profile", response_model=ProfileResponse)
def get_profile(url: str = Query(..., description="LinkedIn profile URL")):
    """
    Return structured profile data for a LinkedIn profile URL.

    Example: /profile?url=https://www.linkedin.com/in/sajal-saraf-222486224
    """
    if "linkedin.com/in/" not in url:
        raise HTTPException(status_code=400, detail="Invalid LinkedIn profile URL — must contain linkedin.com/in/")

    # Extract username from URL
    try:
        username = url.rstrip("/").split("/in/")[1].split("/")[0].split("?")[0]
    except IndexError:
        raise HTTPException(status_code=400, detail="Could not parse username from URL")

    try:
        profile = client.get_profile(username)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="LinkedIn session expired — update cookies in .env")
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="LinkedIn profile not found")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="LinkedIn rate limit hit — try again later")
        raise HTTPException(status_code=502, detail=f"LinkedIn API error: {e.response.status_code}")
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except httpx.TooManyRedirects:
        raise HTTPException(status_code=401, detail="LinkedIn session expired — update cookies in .env and restart server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {type(e).__name__}: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}
