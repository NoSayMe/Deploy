# PostgreSQL Database

The repository uses the official `postgres:15` image to provide a database for the handler service. The container exposes port **5432** and stores its data under `/var/ci_data/postgres/data` on the host.

Environment variables defined in `docker-compose.yml`:

- `POSTGRES_PASSWORD` – password for the default `postgres` user (set to `postgres`).
- `POSTGRES_DB` – database created on startup (set to `handler_db`).

This service depends on the `nginx` container so that other applications can reach the database through the shared network.

No additional configuration is required. The handler service automatically creates the required tables when it starts.

### Permissions

The data directory mounted at `/var/ci_data/postgres/data` must be writable by
the `postgres` user inside the container (UID `999`). If the database fails to
start with a permission error, adjust the ownership on the host:

```bash
sudo chown -R 999:999 /var/ci_data/postgres
```

This allows PostgreSQL to access `pg_filenode.map` and other internal files.

