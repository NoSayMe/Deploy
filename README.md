# Deploy Infrastructure

This repository contains Docker-based services and a Jenkins pipeline used to run a small example application. Each service lives under the `services/` directory and is deployed according to its `deploy.json` file. The pipeline builds or pulls images, creates containers and ensures they share a Docker network for internal communication.

```
Deploy/
├── services/
│   ├── handler/        # FastAPI API service
│   ├── mcp_server/     # Dummy MCP server
│   ├── nginx/          # Reverse proxy
│   └── postgres/       # PostgreSQL database
├── Jenkinsfile         # CI/CD pipeline
└── README.md
```

## Jenkins Pipeline

The `Jenkinsfile` looks for services that changed in the latest commit and deploys only those containers. If a service image is marked with `"build": true` in its `deploy.json`, Jenkins builds it from the local Dockerfile. Otherwise the image is pulled from a registry when needed. A dedicated Docker network (`ci-network`) is created so the containers can reach each other by name.

## Services

The table below lists the available services. Follow the links for detailed information about each one.

| Service | Ports | Depends On | Documentation |
|---------|-------|------------|---------------|
| **handler** | `8082:8000` | `postgres` | [handler/README.md](services/handler/README.md) |
| **postgres** | `5432:5432` | - | [postgres/README.md](services/postgres/README.md) |
| **mcp_server** | `8090:8000` | - | [mcp_server/README.md](services/mcp_server/README.md) |
| **nginx** | `8081:80` | `handler`, `mcp_server` | [nginx/README.md](services/nginx/README.md) |

### Persistent Storage

Containers store data in `/var/ci_data` on the host. For example the PostgreSQL data directory resides in `/var/ci_data/postgres/data` and Nginx logs are written to `/var/ci_data/nginx/logs`. Volume mappings can be found in each service's `deploy.json` file.

