from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import json
import random
import os


router = APIRouter()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8090")

OPENAPI_PATH = Path(__file__).with_name("openapi.json")
PLUGIN_PATH = Path(__file__).with_name("ai-plugin.json")


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_openapi() -> dict:
    schema = load_json(OPENAPI_PATH)
    for srv in schema.get("servers", []):
        srv["url"] = BASE_URL
    return schema


OPENAPI_SCHEMA = load_openapi()


def load_plugin() -> dict:
    plugin = load_json(PLUGIN_PATH)
    plugin["api"]["url"] = f"{BASE_URL}/openapi.json"
    plugin["logo_url"] = f"{BASE_URL}/logo.png"
    return plugin


AI_PLUGIN_SCHEMA = load_plugin()


VEHICLE_PRICES = {
    "skoda": {"octavia": 23000, "fabia": 18000},
    "toyota": {"corolla": 25000, "camry": 27000},
}


class VehicleRequest(BaseModel):
    brand: str
    model: str


class VehicleResponse(BaseModel):
    brand: str
    model: str
    price_eur: int


def get_price(brand: str, model: str) -> int | None:
    return VEHICLE_PRICES.get(brand.lower(), {}).get(model.lower())


@router.post("/get_vehicle_price", response_model=VehicleResponse)
async def get_vehicle_price(data: VehicleRequest) -> dict:
    price = get_price(data.brand, data.model)
    if price is None:
        price = random.randint(15000, 45000)
    return {"brand": data.brand, "model": data.model, "price_eur": price}


def openapi_to_mcp(schema: dict) -> dict:
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

            tools.append({
                "name": name,
                "description": description,
                "inputSchema": input_schema,
                "annotations": {"title": title},
            })

    return {"tools": tools}


@router.get("/schema")
async def get_schema() -> dict:
    return openapi_to_mcp(OPENAPI_SCHEMA)
