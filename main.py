from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from dotenv import load_dotenv
import secrets
import os

load_dotenv()
security = HTTPBasic()

DOCS_USERNAME = os.getenv("DOCS_USERNAME")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

app = FastAPI(docs_url=None, redoc_url=None)
@app.get("/docs", include_in_schema=False)
def custom_swagger(username: str = Depends(verify_credentials)):
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure API Docs")

# Secure OpenAPI JSON
@app.get("/openapi.json", include_in_schema=False)
def get_open_api_endpoint(username: str = Depends(verify_credentials)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

items_db: list[Item] = []

# CREATE - POST
@app.post("/items/")
def create_item(item: Item, username: str = Depends(verify_credentials)):
    for existing_item in items_db:
        if existing_item.id == item.id:
            raise HTTPException(status_code=400, detail="Item ID already exist")
    items_db.append(item)
    return item

# READ ALL - GET
@app.get("/items/")
def get_all_items(username: str = Depends(verify_credentials)):
    return items_db

# READ ONE - GET
@app.get("/items/{item_id}")
def get_item(item_id: int, username: str = Depends(verify_credentials)):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# UPDATE - PUT
@app.put("/items/{item_id}")
def update_item(item_id: int, update_item: Item, username: str = Depends(verify_credentials)):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db[index] = update_item
            return update_item
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE - DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int, username: str = Depends(verify_credentials)):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(index)
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# READ ROOT - GET
@app.get("/")
def read_root(username: str = Depends(verify_credentials)):
    return {"message": "Hello FastAPI!"}