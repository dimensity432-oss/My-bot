
import os
import time
import secrets
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, RateLimitError

APP_NAME = "XENUS AI"
APP_VERSION = "0.2.0"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XENUS_API_KEY = os.getenv("XENUS_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="XENUS AI Developer API"
)

api_key_header = APIKeyHeader(
    name="Authorization",
    auto_error=False
)

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Message] = Field(min_length=1)
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)


def authenticate(api_key: Optional[str] = Depends(api_key_header)):
    if not XENUS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="XENUS authentication is not configured"
        )

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    token = api_key.removeprefix("Bearer ").strip()

    if not secrets.compare_digest(token, XENUS_API_KEY):
        raise HTTPException(
            status_code=403,
            detail="Invalid XENUS API key"
        )

    return True


@app.get("/")
def home():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "service": "XENUS",
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": int(time.time())
    }


@app.get("/v1/models", dependencies=[Depends(authenticate)])
def models():
    return {
        "object": "list",
        "data": [
            {
                "id": OPENAI_MODEL,
                "object": "model",
                "owned_by": "xenus"
            }
        ]
    }


@app.post(
    "/v1/chat/completions",
    dependencies=[Depends(authenticate)]
)
def chat_completions(request: ChatRequest):

    if client is None:
        raise HTTPException(
            status_code=503,
            detail="OpenAI provider is not configured"
        )

    allowed_roles = {"system", "user", "assistant"}

    for message in request.messages:
        if message.role not in allowed_roles:
            raise HTTPException(
                status_code=400,
                detail="Unsupported message role"
            )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": message.role,
                    "content": message.content
                }
                for message in request.messages
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return response.model_dump()

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="AI provider rate limit reached"
        )

    except APIError:
        raise HTTPException(
            status_code=502,
            detail="XENUS AI provider request failed"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="XENUS encountered an internal error"
        )
