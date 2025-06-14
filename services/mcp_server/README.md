# MCP Server

`mcp_server` exposes a small FastAPI service that follows the [OpenAI MCP](https://platform.openai.com/docs/mcp) guidelines.  It is built locally as `mcp-test-server:latest` and runs on port **8000** (exposed on the host as `8090`). The tool definition served by `/tools/schema` is derived from the `openapi.json` file at container start.

The container exposes the base URL used in its OpenAPI schema via the
`BASE_URL` environment variable (default: `http://localhost:8090`).  This
allows the service to operate correctly regardless of the host's IP address.
It has no other required environment variables or persistent volumes, but it
depends on the `nginx` container for routing.

## Endpoints

- `GET /agent/ping` – simple health check returning `{"pong": true}`.
- `POST /agent/echo` – echoes the received message.
- `POST /tools/get_vehicle_price` – returns a price for the given vehicle brand and model. Known vehicles are looked up from a small in-memory table, otherwise a random value is returned.
- `GET /tools/schema` – returns the MCP tool definition derived from the OpenAPI spec.
- `GET /openapi.json` – minimal OpenAPI schema describing the tool.
- `GET /.well-known/ai-plugin.json` – plugin manifest used by OpenAI clients.

The server also serves a tiny placeholder logo at `/logo.png`.

