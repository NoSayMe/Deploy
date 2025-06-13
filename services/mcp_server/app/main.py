from fastapi import FastAPI
from fastapi.responses import Response
import base64
from pydantic import BaseModel
from app.tools import router as tools_router, OPENAPI_SCHEMA, AI_PLUGIN_SCHEMA

# Disable FastAPI's default OpenAPI endpoint so we can serve a custom schema
# describing only the available tool.
app = FastAPI(title="Dummy MCP Server", openapi_url=None)

class EchoRequest(BaseModel):
    message: str


@app.get("/")
async def root() -> dict:
    return {"status": "mcp server running"}

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
