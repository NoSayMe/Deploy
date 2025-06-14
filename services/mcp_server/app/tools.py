from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import random
import os
import httpx
import ast
import operator as op


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


class WeatherRequest(BaseModel):
    location: str
    units: str = "metric"


class WeatherResponse(BaseModel):
    location: str
    temperature: float
    units: str


class CalcRequest(BaseModel):
    expression: str


class CalcResponse(BaseModel):
    result: float


def get_price(brand: str, model: str) -> int | None:
    return VEHICLE_PRICES.get(brand.lower(), {}).get(model.lower())


@router.post("/get_vehicle_price", response_model=VehicleResponse)
async def get_vehicle_price(data: VehicleRequest) -> dict:
    price = get_price(data.brand, data.model)
    if price is None:
        price = random.randint(15000, 45000)
    return {"brand": data.brand, "model": data.model, "price_eur": price}


@router.post("/get_weather", response_model=WeatherResponse)
async def get_weather(data: WeatherRequest) -> dict:
    """Return fake weather info. In real deployments this would query an API."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": 0, "longitude": 0, "current_weather": True},
                timeout=5,
            )
            temp = resp.json().get("current_weather", {}).get("temperature", 20)
    except Exception:
        temp = random.uniform(-10, 30)
    return {"location": data.location, "temperature": temp, "units": data.units}


ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        return ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return ALLOWED_OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


@router.post("/calculate", response_model=CalcResponse)
async def calculate(data: CalcRequest) -> dict:
    try:
        expr = ast.parse(data.expression, mode="eval").body
        result = _eval(expr)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid expression")
    return {"result": result}


async def execute_tool(name: str, arguments: dict) -> dict:
    if name == "get_vehicle_price":
        return await get_vehicle_price(VehicleRequest(**arguments))
    if name == "get_weather":
        return await get_weather(WeatherRequest(**arguments))
    if name == "calculate":
        return await calculate(CalcRequest(**arguments))
    raise ValueError(f"Unknown tool {name}")


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
