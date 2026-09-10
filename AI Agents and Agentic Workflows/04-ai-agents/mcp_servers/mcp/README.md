# Testing the Azerbaijani Weather MCP Server

This directory contains:

- `weather_mcp.py` — a Streamable HTTP MCP server with realistic, deterministic mock weather data.
- `test_weather_mcp.py` — a lightweight FastMCP client that discovers and tests the weather tool.

No external weather API or API key is required.

## 1. Start the MCP server

Open a terminal in this directory and activate the project's virtual environment. Then run:

```powershell
python weather_mcp.py
```

The server should start at:

```text
http://127.0.0.1:8020/weather-mcp
```

Keep this terminal running while testing. The `AuthlibDeprecationWarning` printed during startup comes from a FastMCP dependency and does not prevent the server from working.

## 2. Run the lightweight test client

Open a second terminal in the same directory, activate the same virtual environment, and run:

```powershell
python test_weather_mcp.py
```

Without an argument, the client checks the default location, **Baku**. It connects to the server, lists the available tools, calls `get_weather_conditions`, validates the structured mock response, and prints:

```text
Weather MCP test passed.
```

`Client connected after context exit: False` is expected: it confirms that the client closed its connection cleanly after the test.

## 3. Test another city or destination

Pass a location after the script name:

```powershell
python test_weather_mcp.py Ganja
python test_weather_mcp.py Barda
python test_weather_mcp.py Quba
python test_weather_mcp.py Qusar
python test_weather_mcp.py Lankaran
```

Supported default spellings are:

```text
Baku, Bilgah, Novkhani, Nabran, Barda, Tovuz, Ganja, Salyan,
Quba, Qusar, Xachmaz, Sheki, Gabala, Lankaran, Shamakhi,
Nakhchivan, Naftalan, Goygol
```

Several Azerbaijani and alternative spellings are also recognized, including:

```powershell
python test_weather_mcp.py "Bakı"
python test_weather_mcp.py "Gəncə"
python test_weather_mcp.py "Xaçmaz"
python test_weather_mcp.py "Şəki"
python test_weather_mcp.py "Qəbələ"
python test_weather_mcp.py "Lənkəran"
python test_weather_mcp.py "Şamaxı"
python test_weather_mcp.py "Naxçıvan"
python test_weather_mcp.py "Göygöl"
```

Use quotation marks whenever a location name contains spaces.

## 4. Stop the server

Return to the first terminal and press `Ctrl+C`.

The returned conditions are demonstration data marked with `"data_source": "mock"`; they must not be treated as live weather observations.
