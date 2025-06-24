# MCP Server

`mcp_server` exposes a FastAPI service that follows the [OpenAI MCP](https://platform.openai.com/docs/mcp) guidelines.  Jenkins builds the image from this directory and tags it as `${DOCKER_REGISTRY}/mcp_server:latest`. The server runs on port **8000** (exposed on the host as `8090`). The tool definition served by `/tools/schema` is derived from the `openapi.json` file at container start.

The container exposes the base URL used in its OpenAPI schema via the
`BASE_URL` environment variable (default: `http://\${REMOTE_HOST}:8090` before
substitution). Additional environment variables `SERVER_NAME` and `VERSION` are
defined in `docker-compose.yml`. The service writes logs to
`/var/ci_data/mcp_server/logs` and depends on the `nginx` container for routing.

## Endpoints

- `GET /agent/ping` – simple health check returning `{"pong": true}`.
- `POST /agent/echo` – echoes the received message.
- `POST /tools/get_vehicle_price` – returns a price for the given vehicle brand and model. Known vehicles are looked up from a small in-memory table, otherwise a random value is returned.
- `POST /tools/get_weather` – returns fake weather information for a location.
- `POST /tools/calculate` – evaluates a simple arithmetic expression.
- `GET /tools/schema` – returns the MCP tool definition derived from the OpenAPI spec.
- `GET /openapi.json` – minimal OpenAPI schema describing the tool set.
- `GET /.well-known/ai-plugin.json` – plugin manifest used by OpenAI clients.
- `POST /mcp` – basic MCP protocol endpoint.
- `GET /health` – health endpoint used by Docker.

The server also serves a tiny placeholder logo at `/logo.png`.

