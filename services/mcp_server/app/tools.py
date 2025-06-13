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

# Minimal OpenAPI schema describing the available tool.
OPENAPI_SCHEMA = {
    "openapi": "3.0.1",
    "info": {"title": "Vehicle Price API", "version": "1.0.0"},
    "paths": {
        "/tools/get_vehicle_price": {
            "post": {
                "operationId": "get_vehicle_price",
                "description": "Returns vehicle price given brand and model",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "brand": {"type": "string"},
                                    "model": {"type": "string"}
                                },
                                "required": ["brand", "model"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "brand": {"type": "string"},
                                        "model": {"type": "string"},
                                        "price_eur": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
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

