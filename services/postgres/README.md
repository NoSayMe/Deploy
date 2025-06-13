# PostgreSQL Database

The repository uses the official `postgres:15` image to provide a database for the handler service. The container exposes port **5432** and stores its data under `/var/ci_data/postgres/data` on the host.

Environment variables defined in `deploy.json`:

- `POSTGRES_PASSWORD` – password for the default `postgres` user (set to `postgres`).
- `POSTGRES_DB` – database created on startup (set to `handler_db`).

This service depends on the `nginx` container so that other applications can reach the database through the shared network.

No additional configuration is required. The handler service automatically creates the required tables when it starts.

