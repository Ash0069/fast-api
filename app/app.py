from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from .schemas import PostCreate
from .db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# text_posts = {
#     1: {
#         "title": "Hello World",
#         "content": "This is a test post",
#         "author": "John Doe"
#     }
# }

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/posts")
# def read_posts():
#     return text_posts

# @app.get("/posts/{id}")
# def get_post(id: int):
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found") 
#     return text_posts.get(id)

# @app.post("/posts")
# def create_post(post: PostCreate):
#     new_post = {
#         "title": post.title,
#         "content": post.content,
#         "author": post.author
#     }
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    post = Post(
        caption=caption,
        url="dummy url",
        file_type="photo",
        file_name="dummy name"
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    results = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in results.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": post.id,
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )
    
    return {"posts": posts_data}