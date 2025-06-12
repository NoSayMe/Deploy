from fastapi import FastAPI
from . import tools

app = FastAPI()
app.include_router(tools.router, prefix="/tools")