# MCP Server

`mcp_server` provides a minimal FastAPI application used for experimenting with OpenAI agent tools. It is built locally as `mcp-test-server:latest` and runs on port **8000** (exposed on the host as `8090`).

The container does not require any environment variables or persistent volumes, but it depends on the `nginx` container for routing.

## Endpoints

- `GET /agent/ping` – simple health check returning `{"pong": true}`.
- `POST /agent/echo` – echoes the received message.
- `POST /tools/get_vehicle_price` – returns a random price for the given vehicle brand and model.
- `GET /tools/schema` – returns the OpenAI tool definition for `get_vehicle_price`.
- `GET /openapi.json` – minimal OpenAPI schema describing the tool.
- `GET /.well-known/ai-plugin.json` – plugin manifest used by OpenAI clients.

The server also serves a tiny placeholder logo at `/logo.png`.

