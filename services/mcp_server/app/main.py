from fastapi import FastAPI
from pydantic import BaseModel
from app.tools import router as tools_router

app = FastAPI(title="Dummy MCP Server")

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
