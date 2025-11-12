from pydantic import Field
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather", log_level="ERROR")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

LONDON_LATITUDE = 51.5074
LONDON_LONGITUDE = -0.1278

async def fetch_weather_rain(lat: float, lon: float):    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"User-Agent": USER_AGENT}
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon, "hourly": "rain"},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool(
    name="get_weather",
    description="Find whether it is raining in London right now.",
)
async def get_weather_rain():
    weather_data = await fetch_weather_rain(LONDON_LATITUDE, LONDON_LONGITUDE)

    if not weather_data:
        return "Could not fetch weather data at this time."
    
    return {"forecast": "rain" if weather_data["hourly"]["rain"][0] > 0 else "clear"}

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()