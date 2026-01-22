from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Instead of connecting via db driver like
# conn = psycopg.connect(
#     dbname=getenv('DB_NAME'), user=getenv('DB_USER'), password=getenv('DB_PASS'), row_factory=dict_row
# )
# create a database URL like
# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-addr (or) hostname>/<dbname>'

SQLALCHEMY_DATABASE_URL = getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL) # Engine = connection manager.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # This line creates a factory that can make Sessions.

Base = declarative_base() # parent class: Every ORM model will inherit from Base, so SQLAlchemy can track them.

# dependency generator (for proper cleanup)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()