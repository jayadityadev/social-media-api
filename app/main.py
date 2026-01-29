from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .database import engine, Base
from .routers import post, user, auth, vote

# Base.metadata.create_all(bind=engine)

origins = [
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def read_root():
    return {"working": True}