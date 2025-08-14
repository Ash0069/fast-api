from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

items_db: list[Item] = []

#CREATE - POST
@app.post("/items/")
def create_item(item: Item):
    for existing_item in items_db:
        if existing_item.id == item.id:
            raise HTTPException(status_code=400, detail="Item ID already exist")
    items_db.append(item)
    return item

#READ ALL - GET
@app.get("/items/")
def get_all_items():
    return items_db

#READ ONE - GET
@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

#UPDATE - PUT
@app.put("/items/{item_id}")
def update_item(item_id: int, update_item: Item):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db[index] = update_item
            return update_item
    raise HTTPException(status_code=404, detail="Item not found")

#DELETE - DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(index)
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

#READ ROOT - GET
@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}