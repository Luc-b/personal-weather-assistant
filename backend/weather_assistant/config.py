from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openweather_api_key: str
    groq_api_key: str
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

def get_settings() -> Settings:
    ow = os.getenv("OPENWEATHER_API_KEY", "").strip()
    groq = os.getenv("GROQ_API_KEY", "").strip()

    if not ow:
        raise RuntimeError("Missing OPENWEATHER_API_KEY. Add it to .env.")
    if not groq:
        raise RuntimeError("Missing GROQ_API_KEY. Add it to .env.")

    return Settings(openweather_api_key=ow, groq_api_key=groq)
