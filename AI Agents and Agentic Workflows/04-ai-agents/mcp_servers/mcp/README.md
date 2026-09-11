# Testing the Azerbaijani Weather MCP Server

This directory contains:

- `weather_mcp.py` — a Streamable HTTP MCP server with realistic, deterministic mock weather data.
- `test_weather_mcp.py` — a lightweight FastMCP client that discovers the weather tool exposed by `weather_mcp.py`, calls it once, prints the result, and exits.
- `agent_with_mcp.py` — a full LangChain `create_agent` travel assistant that uses local Ollama models, a vector-search tool for Azerbaijani travel information, and the weather tool exposed by `weather_mcp.py`. It runs an interactive chat until the user enters `exit` or `quit`.

The lightweight test client makes one direct MCP weather call to verify the connection and response. The full agent instead keeps accepting questions in a chat loop and lets the LLM decide when and how to use the MCP weather tool and local travel-search tool for each request.

To test the MCP server and its exposed weather tool through the MCP Inspector UI, use the guide in [`../mcp-inspector`](../mcp-inspector/README.md).

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

### Transport and result details

The client uses:

```python
client = Client(MCP_SERVER_URL)
```

FastMCP automatically detects the URL and creates the Streamable HTTP transport, so an explicit `StreamableHttpTransport` import is not required. Both approaches are valid.

The call still returns the standard `CallToolResult` wrapper. The client extracts its structured dictionary from `.data` to make validation and display simpler:

```python
result = await client.call_tool(...)
weather_data = result.data
```

Some server configurations return `307 Temporary Redirect` when a request URL omits a required trailing slash. This server handles `/weather-mcp` directly, so its normal request logs contain successful `200 OK` and `202 Accepted` responses instead.

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

## Example agent run

Run the server and agent in separate terminals:

```powershell
python weather_mcp.py
```

```powershell
python agent_with_mcp.py
```

Example output:

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|#################################################| 15/15 [00:02<00:00, 5.16it/s]
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Azerbaijan MCP Travel Assistant (type 'exit' to quit)
You: Suggest beach Azerbaijani towns with rainy weather
Assistant: Based on the available travel information and mock weather data,
here are the beach destinations in Azerbaijan.

Currently, Nabran is the beach destination matching your request for rainy
weather:

- Nabran: This is a coastal city close to Xachmaz and is considered
  Azerbaijan's biggest tourist destination for international travelers. It
  features beaches and resorts along the Caspian Sea.
- Mock Weather: Cloudy with light rain (23°C).

Other notable beach areas in Azerbaijan include:

- Bilgah: Located on the northern side of the Absheron Peninsula, it is known
  for its nicer beaches and the Amburan Beach Club.
- Mock Weather: Sunny with a coastal breeze (26°C).
- Novkhani: Home to the AF Beach Club, which offers multiple swimming pools,
  water sports, and entertainment.
- Shikhov: Features the Crescent Beach Hotel, which offers beachfront access
  and indoor/outdoor pools.

You: quit
```
