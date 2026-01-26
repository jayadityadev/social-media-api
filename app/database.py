from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config


# Instead of connecting via db driver like
# conn = psycopg.connect(
#     dbname=getenv('DB_NAME'), user=getenv('DB_USER'), password=getenv('DB_PASS'), row_factory=dict_row
# )
# create a database URL like
# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-addr (or) hostname>/<dbname>'

engine = create_engine(url=config.db_url) # Engine = connection manager.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # This line creates a factory that can make Sessions.

Base = declarative_base() # parent class: Every ORM model will inherit from Base, so SQLAlchemy can track them.

# dependency generator (for proper cleanup)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()