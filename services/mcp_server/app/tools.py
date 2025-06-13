from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class VehicleRequest(BaseModel):
    brand: str
    model: str

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_vehicle_price",
        "description": "Returns the market price of a vehicle based on brand and model",
        "parameters": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Vehicle brand (e.g. Skoda)"},
                "model": {"type": "string", "description": "Vehicle model (e.g. Octavia)"}
            },
            "required": ["brand", "model"]
        }
    }
}

@router.post("/get_vehicle_price")
async def get_vehicle_price(data: VehicleRequest) -> dict:
    price = random.randint(15000, 45000)
    return {
        "brand": data.brand,
        "model": data.model,
        "price_eur": price,
    }

@router.get("/schema")
async def get_schema() -> dict:
    """Return the OpenAI tool definition."""
    return {"tools": [TOOL_SCHEMA]}

