from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from . import models
from .database import engine, Base, Session, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    category: str = "Generic"
    published: bool = True

@app.get("/")
def read_root():
    return {"working": True}


# CRUD - C (ORM done)
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# CRUD - R (ORM done)
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# CRUD - R (ORM done)
@app.get("/posts/{id}") # path parameter
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {id} not found!"
        )
    return post

# CRUD - U
@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, payload: Post, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=404, detail=f"Post with id {id} not found!"
        )
    post.title = payload.title
    post.content = payload.content
    post.category = payload.category
    post.published = payload.published
    db.commit()
    return

# CRUD - D
@app.delete("/posts/{id}")
def delete_posts(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    if deleted_post is None:
        raise HTTPException(
            status_code=404, detail=f"Post with id {id} not found!"
        )
    db.delete(deleted_post)
    db.commit()
    return deleted_post