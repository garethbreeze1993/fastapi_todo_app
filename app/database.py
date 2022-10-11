from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# Structure just to keep until successful connect

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@" \
                          f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#  Dependency for FASTAPI create a db session

def get_db():
    db = SessionLocal()  # create a dbsession
    try:
        # Request and response delivered during yield statement allowing functions access to db session
        yield db
    finally:
        # After response close the db session
        db.close()
