# Deploy Infrastructure

This repository contains Docker-based services and a Jenkins pipeline used to run a small example application. Each service lives under the `services/` directory and is configured through the shared `docker-compose.yml`. The pipeline builds container images, pushes them to a registry and deploys the stack on a remote host.

```
Deploy/
├── services/
│   ├── handler/        # FastAPI API service
│   ├── mcp_server/     # Enhanced MCP server
│   ├── nginx/          # Reverse proxy
│   └── postgres/       # PostgreSQL database
├── Jenkinsfile         # CI/CD pipeline
├── docker-compose.yml  # Service definitions
├── deploy-script.sh    # Remote setup script
└── README.md
```

## Jenkins Pipeline

The pipeline performs the following steps:

1. **Pull Repo** – checkout the latest code.
2. **Build Images** – build Docker images for each service and tag them as `${DOCKER_REGISTRY}/SERVICE:latest` and with the Jenkins build number.
3. **Push to DockerHub** – authenticate with Docker Hub and push the newly built images.
4. **Deploy to Remote Server** – copy `docker-compose.yml` and `deploy-script.sh` to the target host and run the script over SSH. The script installs Docker if required, substitutes the registry and host values, pulls the images and starts the containers on a shared `ci-network`.

After deployment the pipeline prunes local images.

## Services

The table below lists the available services. Follow the links for detailed information about each one.

| Service | Ports | Depends On | Documentation |
|---------|-------|------------|---------------|
| **handler** | `8082:8000` | `nginx`, `postgres` | [handler/README.md](services/handler/README.md) |
| **postgres** | `5432:5432` | `nginx` | [postgres/README.md](services/postgres/README.md) |
| **mcp_server** | `8090:8000` | `nginx` | [mcp_server/README.md](services/mcp_server/README.md) |
| **nginx** | `80:80` | - | [nginx/README.md](services/nginx/README.md) |

The Jenkins UI running on the host at port `8080` can be reached via `http://localhost/jenkins/` through the Nginx proxy.

### Persistent Storage

Containers store data in `/var/ci_data` on the host. For example the PostgreSQL data directory resides in `/var/ci_data/postgres/data` and Nginx logs are written to `/var/ci_data/nginx/logs`. All volume mappings are specified in `docker-compose.yml`.

