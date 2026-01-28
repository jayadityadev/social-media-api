from fastapi import status, HTTPException, APIRouter
from sqlalchemy import func, or_
from .. import models, schemas, deps

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# # CRUD for managing posts

# CRUD - C (ORM done)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(
    post: schemas.PostCreate,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    new_post = models.Post(**post.model_dump(), user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# CRUD - R (ORM done)
@router.get("/", response_model=list[schemas.PostWithVotes])
def get_posts(
    db: deps.DBSession,
    current_user: deps.CurrentUser,
    limit: int = 10,
    offset: int = 0,
    search: str = ""
):
    posts = db.query(
        models.Post, func.count(models.Vote.post_id).label("vote_count")
    ).join(
        models.Vote,
        models.Post.id == models.Vote.post_id,
        isouter=True
    ).group_by(models.Post.id).filter(
        or_(
            models.Post.user_id == current_user.id,
            models.Post.published == True
        ), models.Post.title.contains(search)
    ).order_by(models.Post.id).limit(limit).offset(offset).all()
    return posts


@router.get("/{id}", response_model=schemas.PostWithVotes) # path parameter
def get_post(
    id: int,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    post = db.query(
        models.Post, func.count(models.Vote.post_id).label("vote_count")
    ).join(
        models.Vote,
        models.Post.id == models.Vote.post_id,
        isouter=True
    ).group_by(
        models.Post.id
    ).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {id} not found!"
        )
    if not (post[0].published or post[0].user_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action"
        )
    return post

# CRUD - U (ORM done)
@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(
    id: int, payload: schemas.PostCreate,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=404, detail=f"Post with id {id} not found!"
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action"
        )
    post.title = payload.title
    post.content = payload.content
    post.category = payload.category
    post.published = payload.published
    db.commit()
    return

# CRUD - D (ORM done)
@router.delete("/{id}", response_model=schemas.PostResponse)
def delete_post(
    id: int,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    if deleted_post is None:
        raise HTTPException(
            status_code=404, detail=f"Post with id {id} not found!"
        )
    if deleted_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action"
        )
    db.delete(deleted_post)
    db.commit()
    return deleted_post

