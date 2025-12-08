from fastapi import FastAPI, HTTPException
from .schemas import PostCreate

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

@app.post("/posts")
def create_post(post: PostCreate):
    new_post = {
        "title": post.title,
        "content": post.content,
        "author": post.author
    }
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post