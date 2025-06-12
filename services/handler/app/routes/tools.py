from fastapi import APIRouter
from app.schemas.tool_request import ToolRequest
from fastapi.responses import HTMLResponse
from app.tools.echo import echo_message

router = APIRouter()

@router.post("/echo")
async def run_echo(req: ToolRequest):
    return {"result": echo_message(req.message)}

@router.get("/echo2", response_class=HTMLResponse)
async def echo():
    return """
    <html>
        <head>
            <title>Echo Test</title>
        </head>
        <body>
            <h1>👋 Hello from Jenkins FastAPI!</h1>
            <p>This is a test response in HTML.</p>
        </body>
    </html>
    """
