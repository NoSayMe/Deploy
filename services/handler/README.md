# Handler Service

The handler container runs a small FastAPI application that exposes a few demonstration endpoints and stores messages in PostgreSQL.

## Configuration

The service is built from the included Dockerfile and published by Jenkins as `${DOCKER_REGISTRY}/handler:latest`. It listens on port **8000** (published on the host as `8082`).

Environment variables from `docker-compose.yml`:

- `GLOBAL_MESSAGE` – example message returned by the `/tools/echo` endpoint.
- `DATABASE_URL` – SQLAlchemy URL used to connect to PostgreSQL. By default `postgresql+asyncpg://postgres:postgres@postgres:5432/handler_db`.

This service depends on both the `nginx` and `postgres` containers, which must be reachable at the hostnames `nginx` and `postgres` on the Docker network.

## Endpoints

- All routes are prefixed with `/tools`:

- `POST /tools/echo` – returns `GLOBAL_MESSAGE` followed by the provided message.
- `GET /tools/echo2` – simple HTML response.
- `POST /tools/messages` – store a message in the database and return its ID.
- `GET /tools/messages/{id}` – retrieve a stored message by ID.

The application creates its database tables automatically on startup, retrying for a short period if the database is not yet ready.

