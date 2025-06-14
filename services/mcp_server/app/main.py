from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import base64
from pydantic import BaseModel
from app.tools import (
    router as tools_router,
    OPENAPI_SCHEMA,
    AI_PLUGIN_SCHEMA,
    execute_tool,
    openapi_to_mcp,
)

# Disable FastAPI's default OpenAPI endpoint so we can serve a custom schema
# describing only the available tool.
app = FastAPI(title="Enhanced MCP Server", openapi_url=None)

class EchoRequest(BaseModel):
    message: str


@app.get("/")
async def root() -> dict:
    return {"status": "mcp server running"}


@app.get("/health")
async def health() -> dict:
    """Simple health endpoint used by Docker."""
    return {"status": "ok"}

@app.get("/agent/ping")
async def ping() -> dict:
    return {"pong": True}

@app.post("/agent/echo")
async def echo(req: EchoRequest) -> dict:
    return {"echo": req.message}


LOGO_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/w8AAwMB/1UenwAAAABJRU5ErkJggg=="
)


@app.get("/logo.png", include_in_schema=False)
async def logo() -> Response:
    """Serve a tiny placeholder PNG without storing a binary file."""
    data = base64.b64decode(LOGO_PNG_BASE64)
    return Response(content=data, media_type="image/png")


app.include_router(tools_router, prefix="/tools")


# Expose the minimal OpenAPI schema so agents can discover the tool
@app.get("/openapi.json", include_in_schema=False)
async def openapi() -> dict:
    return OPENAPI_SCHEMA


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def ai_plugin() -> dict:
    """Return the AI plugin description."""
    return AI_PLUGIN_SCHEMA


@app.post("/mcp")
async def mcp_endpoint(payload: dict) -> dict:
    """Handle basic MCP protocol requests."""
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if method == "tools/list":
        result = openapi_to_mcp(OPENAPI_SCHEMA)
        return {"id": req_id, "result": result}

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            result = await execute_tool(name, arguments)
            return {"id": req_id, "result": result}
        except Exception as exc:
            return {"id": req_id, "error": str(exc)}

    raise HTTPException(status_code=400, detail="Unsupported MCP method")
