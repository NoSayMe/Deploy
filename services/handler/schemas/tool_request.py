from pydantic import BaseModel

class ToolRequest(BaseModel):
    message: str
