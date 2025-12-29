from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import urllib.parse

# 1. Cấu hình thông tin server dựa trên hình ảnh của bạn
SERVER = "DESKTOP-7I7S36B"  # Lấy tên server từ hình ảnh
DATABASE = "PETCARE_DB"  # Tên database đã tạo

# 2. Tạo chuỗi kết nối cho Windows Authentication (Trusted Connection)
# Lưu ý: Cần driver ODBC. Thường là 'ODBC Driver 17 for SQL Server'
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# Mã hóa chuỗi kết nối để dùng với SQLAlchemy
params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# 3. Tạo Engine
engine = create_engine(
    DATABASE_URL,
    echo=True, # Để xem log SQL in ra terminal
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_session)]