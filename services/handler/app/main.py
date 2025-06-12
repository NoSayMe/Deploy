from fastapi import FastAPI
from app.tools import tools

app = FastAPI()
app.include_router(tools.router, prefix="/tools")