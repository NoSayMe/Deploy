from fastapi import FastAPI
from pydantic import BaseModel
from app.tools import router as tools_router, OPENAPI_SCHEMA

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


app.include_router(tools_router, prefix="/tools")


# Expose the minimal OpenAPI schema so agents can discover the tool
@app.get("/openapi.json", include_in_schema=False)
async def openapi() -> dict:
    return OPENAPI_SCHEMA
