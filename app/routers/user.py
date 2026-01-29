from fastapi import status, Depends, HTTPException, APIRouter
from .. import models, schemas, utils, deps

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# # CRUD for managing users

# CRUD - C
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: deps.DBSession
):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = models.User(**user.model_dump())
    new_user.password = utils.get_password_hash(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# CRUD - R
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    users = db.query(models.User).all()
    return users

@router.get("/{id}", response_model=schemas.UserResponse) # path parameter
def get_user(
    id: int,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {id} not found!"
        )
    return user

# CRUD - U
@router.put("/{id}")
def update_user(
    id: int, payload: schemas.UserCreate, db: deps.DBSession,
    current_user: deps.CurrentUser
):
    if current_user.id != id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    user.email = payload.email
    user.password = utils.get_password_hash(payload.password)
    db.commit()
    db.refresh(user)
    return user

# CRUD - D
@router.delete("/{id}", response_model=schemas.UserResponse)
def delete_user(
    id: int, db: deps.DBSession, current_user: deps.CurrentUser
):
    if current_user.id != id:
        raise HTTPException(status_code=403, detail="Not authorized")
    deleted_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    db.delete(deleted_user)
    db.commit()
    return deleted_user