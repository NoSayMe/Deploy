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
    "servers": [{"url": "http://31.97.45.128:8090"}],
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

AI_PLUGIN_SCHEMA = {
    "schema_version": "v1",
    "name_for_human": "Vehicle Price Tool",
    "name_for_model": "get_vehicle_price",
    "description_for_human": "Get price estimate for a vehicle given brand and model",
    "description_for_model": "Use this tool to retrieve vehicle pricing by brand and model",
    "auth": {"type": "none"},
    "api": {"type": "openapi", "url": "http://31.97.45.128:8090/openapi.json"},
    "logo_url": "http://31.97.45.128:8090/logo.png",
    "contact_email": "support@yourdomain.com",
    "legal_info_url": "http://yourdomain.com/legal"
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

