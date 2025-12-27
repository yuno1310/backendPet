from datetime import time
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class BranchBase(SQLModel):
    name: str = Field(max_length=100)
    address: str = Field(max_length=255)
    phone: str = Field(max_length=15, unique=True)
    open_time: time
    close_time: time


class Branch(BranchBase, table=True):
    __tablename__ = "Branch"

    branch_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class BranchCreate(BranchBase):
    pass


class BranchRead(BranchBase):
    branch_id: int


class BranchUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=15)
    open_time: Optional[time] = None
    close_time: Optional[time] = None
