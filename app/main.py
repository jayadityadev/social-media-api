from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from random import randint

app = FastAPI()

class Post(BaseModel):
    id : int | None = None
    title: str
    content: str
    category: str | None = None
    published: bool = True

local_db: list[Post] = [
    Post(id=randint(1, 100), title="sample hardcoded title 1", content="sample hardcoded content 1"),
    Post(id=randint(1, 100), title="sample hardcoded title 2", content="sample hardcoded content 2")
]

def find_post_by_id(id: int):
    for post in local_db:
        if id == post.id:
            return local_db.index(post)
    raise HTTPException(status_code=404, detail=f"Post with id {id} not found!")

@app.get("/")
def read_root():
    return {"working": True}

# CRUD - C
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post.id = randint(1, 100)
    local_db.append(post)
    return {"detail": "Post created successfully!"}

# CRUD - R
@app.get("/posts")
def get_posts():
    return {"data": local_db}

# CRUD - R
@app.get("/posts/{id}") # path parameter
def get_post(id: int):
    # # response.status_code = status.HTTP_404_NOT_FOUND; send a response: Response param in the function
    post_index = find_post_by_id(id)
    return local_db[post_index]

# CRUD - U
@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, post: Post):
    post_index = find_post_by_id(id)
    post.id = id
    local_db[post_index] = post

# CRUD - D
@app.delete("/posts/{id}")
def delete_posts(id: int):
    post_index = find_post_by_id(id)
    deleted_post = local_db.pop(post_index)
    return {"detail": "Post deleted successfully!", "data": deleted_post}
