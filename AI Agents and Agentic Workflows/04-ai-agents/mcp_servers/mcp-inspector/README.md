# Testing the Weather MCP Server with MCP Inspector

The weather MCP server uses **Streamable HTTP** and provides realistic mock weather data for Azerbaijani destinations. It does not require an external weather API or an API key.

## Prerequisite: Node.js and npm

MCP Inspector is launched with `npx`, so Node.js and npm must be installed. npm and npx are included with the standard Node.js installation.

On Windows, download and install the **LTS** release from the [official Node.js download page](https://nodejs.org/en/download/). Alternatively, install it from PowerShell or Command Prompt with Windows Package Manager:

```powershell
winget install OpenJS.NodeJS.LTS
```

After installation, open a new terminal and verify that both commands are available:

```powershell
node --version
npm --version
```

My output:

```shell
(.venv) C:\Gasym\...\AI Agents and Agentic Workflows\04-ai-agents\mcp_servers>node --version
v24.19.0

(.venv) C:\Gasym\...\AI Agents and Agentic Workflows\04-ai-agents\mcp_servers>npm --version
11.17.0
```

## 1. Start MCP Inspector

From this directory, run:

```powershell
npx @modelcontextprotocol/inspector
```

Keep this terminal running and open the Inspector URL displayed in the output.

## 2. Start the weather MCP server

Open a second terminal in this directory and run:

```powershell
python ..\mcp\weather_mcp.py
```

The server should start at:

```text
http://127.0.0.1:8020/weather-mcp
```

## 3. Add the server in MCP Inspector

In **Add servers**, select `+ Add manually`, enter:

```text
Server ID: azerbaijan-weather
Transport: Streamable HTTP
URL: http://127.0.0.1:8020/weather-mcp
```

No headers, environment variables, or API keys are required. Click **Add**, then connect the server if it does not connect automatically.

## 4. Test the weather tool

1. Open **Tools**.
2. Select `get_weather_conditions`.
3. Enter the following arguments:

In the `location*` field, enter:

```text
Baku
```

or 

Click `Edit as JSON` and enter:
```json
{
  "location": "Baku"
}
```

4. Click **Execute Tool**.

The result should contain structured mock weather data marked with:

```json
{
  "location": "Baku",
  "country": "Azerbaijan",
  "data_source": "mock",
  "current_conditions": {
    "temperature": {
      "value": 27,
      "unit": "C"
    },
    "weather_text": "Sunny and breezy",
    "relative_humidity": 55,
    "precipitation": false,
    "wind_speed": {
      "value": 24,
      "unit": "km/h"
    },
    "observation_time": "2026-09-10T07:52:48+04:00"
  }
}
```

Other supported examples include `Bakı`, `Ganja`, `Gəncə`, `Barda`, `Quba`, `Qusar`, and `Lankaran`.

> The returned conditions are demonstration data and must not be treated as real-time weather information.
