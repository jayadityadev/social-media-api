from fastapi import FastAPI
from .database import engine, Base
from .routers import post, user, auth, vote

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def read_root():
    return {"working": True}