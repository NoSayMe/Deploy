from fastapi import APIRouter
from pydantic import BaseModel
import random


def openapi_to_mcp(schema: dict) -> dict:
    """Convert an OpenAPI schema to a minimal MCP tool definition."""
    tools = []
    title = schema.get("info", {}).get("title", "")
    for path, methods in schema.get("paths", {}).items():
        for method, op in methods.items():
            name = op.get("operationId") or f"{method}_{path.strip('/').replace('/', '_')}"
            description = op.get("description") or op.get("summary", "")

            input_schema = {}
            if "requestBody" in op:
                content = op["requestBody"].get("content", {})
                input_schema = content.get("application/json", {}).get("schema", {})
            elif "parameters" in op:
                props = {}
                required = []
                for p in op["parameters"]:
                    schema_ = p.get("schema", {}).copy()
                    if p.get("description"):
                        schema_["description"] = p["description"]
                    props[p["name"]] = schema_
                    if p.get("required"):
                        required.append(p["name"])
                if props:
                    input_schema = {"type": "object", "properties": props}
                    if required:
                        input_schema["required"] = required

            tools.append(
                {
                    "name": name,
                    "description": description,
                    "inputSchema": input_schema,
                    "annotations": {"title": title},
                }
            )

    return {"tools": tools}

router = APIRouter()

class VehicleRequest(BaseModel):
    brand: str
    model: str

# Minimal OpenAPI schema describing the available tool.
OPENAPI_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "Vehicle Price API",
        "description": "API to estimate vehicle prices by brand and model.",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@yourdomain.com",
            "url": "http://yourdomain.com/support",
        },
    },
    "externalDocs": {
        "description": "Full documentation",
        "url": "http://yourdomain.com/docs",
    },
    "servers": [{"url": "http://31.97.45.128:8090"}],
    "paths": {
        "/tools/get_vehicle_price": {
            "post": {
                "operationId": "get_vehicle_price",
                "summary": "Get vehicle price estimate",
                "description": "Returns vehicle price for the provided brand and model",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "brand": {
                                        "type": "string",
                                        "description": "Vehicle brand (e.g. Skoda)",
                                    },
                                    "model": {
                                        "type": "string",
                                        "description": "Vehicle model (e.g. Octavia)",
                                    },
                                },
                                "required": ["brand", "model"],
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

TOOLS = openapi_to_mcp(OPENAPI_SCHEMA)["tools"]

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
    """Return the MCP tool definition generated from the OpenAPI schema."""
    return {"tools": TOOLS}

