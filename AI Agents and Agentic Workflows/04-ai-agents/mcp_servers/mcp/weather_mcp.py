from datetime import datetime
from typing import Any, Dict
from zoneinfo import ZoneInfo

from fastmcp import FastMCP


mcp = FastMCP("azerbaijan-weather-mcp")


# Realistic but deterministic demonstration data. No external API is called.
MOCK_WEATHER: Dict[str, Dict[str, Any]] = {
    "baku": {
        "location": "Baku",
        "temperature_c": 27,
        "weather_text": "Sunny and breezy",
        "relative_humidity": 55,
        "precipitation": False,
        "wind_speed_kmh": 24,
    },
    "bilgah": {
        "location": "Bilgah",
        "temperature_c": 26,
        "weather_text": "Sunny with a coastal breeze",
        "relative_humidity": 61,
        "precipitation": False,
        "wind_speed_kmh": 21,
    },
    "novkhani": {
        "location": "Novkhani",
        "temperature_c": 26,
        "weather_text": "Partly cloudy",
        "relative_humidity": 63,
        "precipitation": False,
        "wind_speed_kmh": 19,
    },
    "nabran": {
        "location": "Nabran",
        "temperature_c": 23,
        "weather_text": "Cloudy with light rain",
        "relative_humidity": 78,
        "precipitation": True,
        "wind_speed_kmh": 12,
    },
    "barda": {
        "location": "Barda",
        "temperature_c": 28,
        "weather_text": "Mostly sunny",
        "relative_humidity": 46,
        "precipitation": False,
        "wind_speed_kmh": 10,
    },
    "tovuz": {
        "location": "Tovuz",
        "temperature_c": 23,
        "weather_text": "Partly cloudy",
        "relative_humidity": 57,
        "precipitation": False,
        "wind_speed_kmh": 9,
    },
    "ganja": {
        "location": "Ganja",
        "temperature_c": 25,
        "weather_text": "Clear",
        "relative_humidity": 49,
        "precipitation": False,
        "wind_speed_kmh": 11,
    },
    "salyan": {
        "location": "Salyan",
        "temperature_c": 29,
        "weather_text": "Sunny",
        "relative_humidity": 51,
        "precipitation": False,
        "wind_speed_kmh": 15,
    },
    "quba": {
        "location": "Quba",
        "temperature_c": 20,
        "weather_text": "Cloudy",
        "relative_humidity": 70,
        "precipitation": False,
        "wind_speed_kmh": 8,
    },
    "qusar": {
        "location": "Qusar",
        "temperature_c": 18,
        "weather_text": "Light rain",
        "relative_humidity": 81,
        "precipitation": True,
        "wind_speed_kmh": 7,
    },
    "xachmaz": {
        "location": "Xachmaz",
        "temperature_c": 22,
        "weather_text": "Overcast",
        "relative_humidity": 74,
        "precipitation": False,
        "wind_speed_kmh": 10,
    },
    "sheki": {
        "location": "Sheki",
        "temperature_c": 21,
        "weather_text": "Scattered showers",
        "relative_humidity": 76,
        "precipitation": True,
        "wind_speed_kmh": 6,
    },
    "gabala": {
        "location": "Gabala",
        "temperature_c": 19,
        "weather_text": "Cloudy with sunny intervals",
        "relative_humidity": 72,
        "precipitation": False,
        "wind_speed_kmh": 7,
    },
    "lankaran": {
        "location": "Lankaran",
        "temperature_c": 24,
        "weather_text": "Rain showers",
        "relative_humidity": 84,
        "precipitation": True,
        "wind_speed_kmh": 13,
    },
    "shamakhi": {
        "location": "Shamakhi",
        "temperature_c": 20,
        "weather_text": "Mostly cloudy",
        "relative_humidity": 66,
        "precipitation": False,
        "wind_speed_kmh": 14,
    },
    "nakhchivan": {
        "location": "Nakhchivan",
        "temperature_c": 28,
        "weather_text": "Dry and sunny",
        "relative_humidity": 35,
        "precipitation": False,
        "wind_speed_kmh": 9,
    },
    "naftalan": {
        "location": "Naftalan",
        "temperature_c": 25,
        "weather_text": "Mostly sunny",
        "relative_humidity": 48,
        "precipitation": False,
        "wind_speed_kmh": 8,
    },
    "goygol": {
        "location": "Goygol",
        "temperature_c": 19,
        "weather_text": "Cool and partly cloudy",
        "relative_humidity": 68,
        "precipitation": False,
        "wind_speed_kmh": 6,
    },
}


LOCATION_ALIASES = {
    "bakı": "baku",
    "gence": "ganja",
    "gəncə": "ganja",
    "xaçmaz": "xachmaz",
    "khachmaz": "xachmaz",
    "şəki": "sheki",
    "shaki": "sheki",
    "qəbələ": "gabala",
    "qabala": "gabala",
    "lənkəran": "lankaran",
    "şamaxı": "shamakhi",
    "naxçıvan": "nakhchivan",
    "göygöl": "goygol",
}


def normalize_location(location: str) -> str:
    """Normalize English and Azerbaijani location spellings."""
    normalized = " ".join(location.strip().casefold().split())
    return LOCATION_ALIASES.get(normalized, normalized)


@mcp.tool(
    description=(
        "Get realistic mock weather conditions for a supported Azerbaijani "
        "city, town, or seaside destination. No external weather API is used."
    )
)
async def get_weather_conditions(location: str) -> Dict[str, Any]:
    """Return deterministic mock weather for an Azerbaijani location."""
    location_key = normalize_location(location)
    weather = MOCK_WEATHER.get(location_key)

    if weather is None:
        return {
            "error": f"No mock weather data is available for '{location}'.",
            "available_locations": sorted(
                item["location"] for item in MOCK_WEATHER.values()
            ),
        }

    observation_time = datetime.now(ZoneInfo("Asia/Baku")).isoformat(
        timespec="seconds"
    )
    return {
        "location": weather["location"],
        "country": "Azerbaijan",
        "data_source": "mock",
        "current_conditions": {
            "temperature": {
                "value": weather["temperature_c"],
                "unit": "C",
            },
            "weather_text": weather["weather_text"],
            "relative_humidity": weather["relative_humidity"],
            "precipitation": weather["precipitation"],
            "wind_speed": {
                "value": weather["wind_speed_kmh"],
                "unit": "km/h",
            },
            "observation_time": observation_time,
        },
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8020,
        path="/weather-mcp",
    )
