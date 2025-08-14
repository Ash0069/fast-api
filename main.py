from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ItemResponse(BaseModel):
    name: str
    price: float
    total_price: float | None = None

@app.post("/items/", response_model=ItemResponse)
def create_item(item: Item):
    total_price = item.price + item.tax if item.tax else None
    return ItemResponse(
        name=item.name,
        price=item.price,
        total_price=total_price
    )

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/search/")
def search_items(keyword: str, limit: int = 10):
    return {"keyword": keyword, "limit": limit}