from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from .schemas import PostCreate, UserRead, UserCreate, UserUpdate
from .db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from .images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from .users import auth_backend, fastapi_users, current_active_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

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
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session)
):

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        upload_result = imagekit.upload_file(
            file = open(temp_file_path, "rb"),
            file_name = file.filename,
            options = UploadFileRequestOptions(
                use_unique_file_name = True,
                tags = ['backend-upload']
            )
        )

        if upload_result.response_metadata.http_status_code == 200:
            
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video") else "photo",
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

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

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            return HTTPException(status_code=404, detail="Post not found")

        await session.delete(post)
        await session.commit()

        return { "success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))