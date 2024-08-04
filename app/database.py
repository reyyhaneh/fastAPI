from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


engine = create_engine(DATABASE_URL)

# Each instance of the SessionLocal class will be a database session. 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#  Database models or classes will inherit from this class.
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    