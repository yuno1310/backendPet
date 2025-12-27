from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

SERVER = "localhost"
DATABASE = "PetCareX_DB"
USERNAME = "sa"
PASSWORD = "123456789"  # StrongPass@123

DATABASE_URL = (
    "mssql+pyodbc://"
    f"{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    db = SessionLocal()
    print(DATABASE_URL)
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_session)]
