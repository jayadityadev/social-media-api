from fastapi import status, HTTPException, APIRouter
from .. import models, schemas, deps
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/vote",
    tags=['Votes']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    db: deps.DBSession,
    current_user: deps.CurrentUser
):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    found_vote = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    ).first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user already has a vote on post_id {vote.post_id}")
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return new_vote
    else:
        if found_vote is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user does not have a vote on post_id {vote.post_id}")
        db.delete(found_vote)
        db.commit()
        return found_vote