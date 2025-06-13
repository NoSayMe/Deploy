from fastapi import FastAPI
from app.routes import tools
from app.db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event() -> None:
    await init_db()

app.include_router(tools.router, prefix="/tools")
