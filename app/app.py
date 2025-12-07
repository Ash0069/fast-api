from fastapi import FastAPI, HTTPException

app = FastAPI()

text_posts = {
    1: {
        "title": "Hello World",
        "content": "This is a test post",
        "author": "John Doe"
    }
}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/posts")
def read_posts():
    return text_posts

@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found") 
    return text_posts.get(id)