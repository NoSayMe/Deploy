from fastapi import FastAPI
import tools

app = FastAPI()
app.include_router(tools.router, prefix="/tools")