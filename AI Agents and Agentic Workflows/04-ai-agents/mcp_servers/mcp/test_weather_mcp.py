"""Lightweight client for testing the Azerbaijani mock weather MCP server."""

import asyncio
import json
import sys
from typing import Any

from fastmcp import Client


MCP_SERVER_URL = "http://127.0.0.1:8020/weather-mcp"
WEATHER_TOOL_NAME = "get_weather_conditions"
DEFAULT_LOCATION = "Baku"


async def test_weather_tool(location: str) -> None:
    """Connect to the MCP server, discover its tools, and test a weather call."""
    async with Client(MCP_SERVER_URL) as client:
        print(f"Client connected: {client.is_connected()}")

        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"Available tools: {tool_names}")

        if WEATHER_TOOL_NAME not in tool_names:
            raise RuntimeError(
                f"Required tool '{WEATHER_TOOL_NAME}' was not exposed by the server."
            )

        result: Any = await client.call_tool(
            WEATHER_TOOL_NAME,
            {"location": location},
        )

        weather_data = getattr(result, "data", None)
        if weather_data is None:
            weather_data = getattr(result, "structured_content", None)

        print(
            f"Weather result for {location}:\n"
            f"{json.dumps(weather_data, indent=2, ensure_ascii=False)}"
        )

        if not isinstance(weather_data, dict):
            raise TypeError("The weather tool did not return structured dictionary data.")
        if weather_data.get("data_source") != "mock":
            raise AssertionError("The response was not identified as mock data.")
        if "current_conditions" not in weather_data:
            raise AssertionError("The response does not contain current_conditions.")

        print("Weather MCP test passed.")

    print(f"Client connected after context exit: {client.is_connected()}")


def main() -> None:
    """Run the test with an optional location supplied on the command line."""
    location = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOCATION

    try:
        asyncio.run(test_weather_tool(location))
    except Exception as exc:
        raise SystemExit(
            f"Weather MCP test failed. Ensure weather_mcp.py is running at "
            f"{MCP_SERVER_URL}. Error: {type(exc).__name__}: {exc}"
        ) from None


if __name__ == "__main__":
    main()
