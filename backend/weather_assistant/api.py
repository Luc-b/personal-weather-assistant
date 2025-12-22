from __future__ import annotations

from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from weather_assistant.config import get_settings
from weather_assistant.models import WeatherSummary, LLMRecommendation
from weather_assistant.services.openweather import OpenWeatherClient, build_weather_summary
from weather_assistant.services.groq import GroqClient


class HealthResponse(BaseModel):
    status: str

app = FastAPI(title="Personal Weather Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")

#for future improvements - not using it now
@app.get("/geocode")
def geocode(city: str = Query(..., min_length=1)):
    s = get_settings()
    ow = OpenWeatherClient(s.openweather_api_key)
    try:
        geo = ow.geocode(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        ow.close()
    return {
        "name": geo.name,
        "lat": geo.lat,
        "lon": geo.lon,
        "country": geo.country,
        "state": geo.state,
    }


@app.get("/forecast", response_model=WeatherSummary)
def forecast(
    city: str = Query(..., min_length=1),
    date: str = Query(..., description="YYYY-MM-DD"),
):
    try:
        requested = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    s = get_settings()
    
    ow = OpenWeatherClient(s.openweather_api_key)
    try:
        geo = ow.geocode(city)
        forecast_json = ow.forecast_5day_3h(geo.lat, geo.lon)
        slot, used_date, tz = ow.pick_best_slot_for_date(forecast_json, requested)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        ow.close()

    summary = build_weather_summary(
        city_name=geo.name,
        country=geo.country,
        used_date=used_date,
        slot=slot,
    )
    return summary


@app.get("/recommend", response_model=LLMRecommendation)
def recommend(
    city: str = Query(..., min_length=1),
    date: str = Query(..., description="YYYY-MM-DD"),
):
    try:
        requested = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    s = get_settings()
    ow = OpenWeatherClient(s.openweather_api_key)
    try:
        geo = ow.geocode(city)
        forecast_json = ow.forecast_5day_3h(geo.lat, geo.lon)
        slot, used_date, tz = ow.pick_best_slot_for_date(forecast_json, requested)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        ow.close()
    summary = build_weather_summary(
        city_name=geo.name,
        country=geo.country,
        used_date=used_date,
        slot=slot,
    )

    groq = GroqClient(api_key=s.groq_api_key, model=s.groq_model)
    try:
        raw = groq.get_recommendations(summary.model_dump(mode="json"))
    finally:
        groq.close()

    try:
        rec = LLMRecommendation.model_validate(raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid schema: {e}")

    return rec