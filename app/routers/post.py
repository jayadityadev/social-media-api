from fastapi import status, Depends, HTTPException, APIRouter
from .. import models, schemas
from ..database import Session, get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# # CRUD for managing posts

# CRUD - C (ORM done)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# CRUD - R (ORM done)
@router.get("/", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@router.get("/{id}", response_model=schemas.Post) # path parameter
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {id} not found!"
        )
    return post

# CRUD - U (ORM done)
@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, payload: schemas.PostCreate, db: Session = Depends(get_db)):
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

# CRUD - D (ORM done)
@router.delete("/{id}", response_model=schemas.Post)
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    if deleted_post is None:
        raise HTTPException(
            status_code=404, detail=f"Post with id {id} not found!"
        )
    db.delete(deleted_post)
    db.commit()
    return deleted_post

