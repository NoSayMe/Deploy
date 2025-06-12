from fastapi import FastAPI
from app.routes import tools

app = FastAPI()
app.include_router(tools.router, prefix="/tools")