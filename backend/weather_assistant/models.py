import datetime as dt
from pydantic import BaseModel, Field, ConfigDict

class WeatherSummary(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "Zagreb",
                "country": "HR",
                "date": "2025-12-20",
                "description": "clear sky",
                "temperature_c": 6.0,
                "feels_like_c": 5.0,
                "humidity_percent": 70,
                "wind_speed_mps": 2.5,
                "precipitation_probability": 0.15,
            }
        }
    )

    city: str
    country: str
    date: dt.date = Field(description="ISO date used for forecast (YYYY-MM-DD)")
    description: str

    temperature_c: float
    feels_like_c: float | None = None
    humidity_percent: int | None = Field(default=None, ge=0, le=100)
    wind_speed_mps: float | None = None
    precipitation_probability: float | None = Field(default=None, ge=0.0, le=1.0)


class Outfit(BaseModel):
    top: list[str] = Field(default_factory=list)
    bottom: list[str] = Field(default_factory=list)
    shoes: list[str] = Field(default_factory=list)
    outerwear: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)


class Activities(BaseModel):
    outdoor: list[str] = Field(default_factory=list)
    indoor: list[str] = Field(default_factory=list)


class LLMRecommendation(BaseModel):
    summary: str
    outfit: Outfit
    activities: Activities
    warnings: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
