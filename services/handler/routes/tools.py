from fastapi import APIRouter
from app.schemas.tool_request import ToolRequest
from app.tools.echo import echo_message

router = APIRouter()

@router.post("/echo")
async def run_echo(req: ToolRequest):
    return {"result": echo_message(req.message)}
