from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = DATABASE_URL.replace(
    "mysql://",
    "mysql+pymysql://"
)
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {}
    }
)
SessionLocal = sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
