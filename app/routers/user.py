from fastapi import status, Depends, HTTPException, APIRouter
from .. import models, schemas, utils
from ..database import Session, get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# # CRUD for managing users

# CRUD - C
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    new_user.password = utils.get_password_hash(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# CRUD - R
@router.get("/", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get("/{id}", response_model=schemas.User) # path parameter
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {id} not found!"
        )
    return user

# CRUD - U
@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_user(id: int, payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {id} not found!"
        )
    user.email = payload.email
    user.password = utils.get_password_hash(payload.password)
    db.commit()
    return

# CRUD - D
@router.delete("/{id}", response_model=schemas.User)
def delete_user(id: int, db: Session = Depends(get_db)):
    deleted_user = db.query(models.User).filter(models.User.id == id).first()
    if deleted_user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {id} not found!"
        )
    db.delete(deleted_user)
    db.commit()
    return deleted_user