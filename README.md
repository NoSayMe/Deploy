# Deploy Repository Overview

This repository contains the deployment configuration for a small FastAPI example and its supporting database. Jenkins reads the `deploy.json` files in the `services` directory to build and run each container.

```
Deploy/
├── services/
│   ├── handler/        # FastAPI service
│   │   ├── Dockerfile
│   │   ├── deploy.json
│   │   └── app/
│   └── postgres/       # Postgres database
│       └── deploy.json
├── Jenkinsfile         # CI/CD pipeline
└── README.md
```

## Jenkins Pipeline

The pipeline defined in `Jenkinsfile` creates a shared Docker network (`ci-network`) and deploys only the services that changed in the last commit. Images can be built locally or pulled from a registry according to each `deploy.json` file.

## Deployed Containers

| Container | Ports | Purpose |
|-----------|-------|---------|
| **handler** | `8082:8000` | FastAPI application exposing the API described below. |
| **postgres** | `5432:5432` | PostgreSQL 15 database used by the handler service. |
| **mcp_server** | `8090:8000` | Dummy MCP server for experimenting with OpenAI agents. |

### Handler API

The handler container runs a FastAPI app on port `8000` (mapped to `8082` on the host). Available endpoints under the `/tools` prefix:

- `POST /tools/echo` – return a friendly greeting.
- `GET /tools/echo2` – simple HTML response.
- `POST /tools/messages` – store a message in the Postgres database.
- `GET /tools/messages/{id}` – retrieve a stored message by ID.

The Postgres container provides the database `handler_db` and is configured with the `POSTGRES_PASSWORD` environment variable set to `postgres`.

Both containers run on the same Docker network created by Jenkins so the handler service can reach the database at the hostname `postgres`.

### Database Initialisation

The FastAPI application automatically creates the required tables when it
starts. If the database is not ready yet, the startup routine retries a few
times before giving up. Simply running the `handler` service prepares the
database for storing messages.

### MCP Server API

The `mcp_server` container exposes a minimal FastAPI application on port `8000`
(mapped to `8090` on the host). It now includes a small example tool and an
endpoint exposing its schema so you can experiment with OpenAI's tool calling
feature:

- `GET /agent/ping` – simple health check returning `{ "pong": true }`.
- `POST /agent/echo` – returns the message sent in the request body.
- `POST /tools/get_vehicle_price` – returns a mock price for the provided
  vehicle brand and model.
- `GET /tools/schema` – returns the OpenAI tool schema describing
  `get_vehicle_price`.
- `GET /openapi.json` – returns an OpenAPI description of the
  `get_vehicle_price` tool.

These endpoints are intentionally lightweight so you can easily connect to them
from the ChatGPT playground or your own scripts while learning how MCP works.
