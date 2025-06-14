# Nginx Reverse Proxy

This container runs a lightweight Nginx instance that forwards requests to the other services.
It is built as `custom-nginx:latest` and exposes port **80** on the host.

## Routing

- Requests to `/api/` are proxied to the **handler** service with the `/api` prefix removed.
- Requests to `/mcp/` are proxied to the **mcp_server** service.
- Requests to `/jenkins/` are proxied to the host Jenkins instance on port `8080`.
- Unknown paths return a custom `404.html` page.

Access and error logs are written to `/var/ci_data/nginx/logs` on the host as defined in `deploy.json`.
This container has no dependencies, but other services rely on it for routing.

