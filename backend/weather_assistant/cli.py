import typer
from datetime import datetime

from weather_assistant.config import get_settings
from weather_assistant.models import WeatherSummary, LLMRecommendation
from weather_assistant.services.openweather import OpenWeatherClient, build_weather_summary
from weather_assistant.services.groq import GroqClient

app = typer.Typer(help="Personal Weather Assistant (CLI)")

@app.command("run")
def run_cmd():
    print("Hello from CLI OK")

@app.command("geocode")
def geocode_cmd(city: str = typer.Option(..., "--city", "-c")):
    s = get_settings()
    ow = OpenWeatherClient(s.openweather_api_key)

    geo = ow.geocode(city)
    print(f"City: {geo.name} ({geo.country})")
    print(f"Lat/Lon: {geo.lat}, {geo.lon}")
#zašto je geocode endpoint
@app.command("forecast")
def forecast_cmd(
    city: str = typer.Option(..., "--city", "-c"),
    date: str = typer.Option(..., "--date", "-d", help="YYYY-MM-DD"),
):
    requested = datetime.strptime(date, "%Y-%m-%d").date()

    s = get_settings()
    ow = OpenWeatherClient(s.openweather_api_key)

    geo = ow.geocode(city)
    forecast = ow.forecast_5day_3h(geo.lat, geo.lon)
    try:
        slot, used_date, tz = ow.pick_best_slot_for_date(forecast, requested)
    except ValueError as e:
        print(f" {e}")
        print(" OpenWeatherMap provides forecasts only up to ~5 days ahead.")
        raise typer.Exit(code=1)

    summary = build_weather_summary(
        city_name=geo.name,
        country=geo.country,
        used_date=used_date,
        slot=slot,
    )

    print("\n=== Weather Summary (JSON) ===")
    print(summary.model_dump_json(indent=2))

@app.command("recommend")
def recommend_cmd(
    city: str = typer.Option(..., "--city", "-c"),
    date: str = typer.Option(..., "--date", "-d"),
):
    requested = datetime.strptime(date, "%Y-%m-%d").date()

    s = get_settings()
    ow = OpenWeatherClient(s.openweather_api_key)

    geo = ow.geocode(city)
    forecast = ow.forecast_5day_3h(geo.lat, geo.lon)
    try:
        slot, used_date, tz = ow.pick_best_slot_for_date(forecast, requested)
    except ValueError as e:
        print(f" {e}")
        print(" OpenWeatherMap provides forecasts only up to ~5 days ahead.")
        raise typer.Exit(code=1)

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

    rec = LLMRecommendation.model_validate(raw)

    print("\n=== Recommendations (JSON) ===")
    print(rec.model_dump_json(indent=2))

if __name__ == "__main__":
    app()
