from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class BranchServiceBase(SQLModel):
    is_available: bool = Field(default=True)
    effective_date: Optional[date] = None


class BranchService(BranchServiceBase, table=True):
    __tablename__ = "Branch_Service"

    branch_id: int = Field(foreign_key="Branch.branch_id", primary_key=True)
    service_id: int = Field(foreign_key="Service.service_id", primary_key=True)


class BranchServiceCreate(BranchServiceBase):
    branch_id: int
    service_id: int


class BranchServiceRead(BranchServiceBase):
    branch_id: int
    service_id: int


class BranchServiceUpdate(SQLModel):
    is_available: Optional[bool] = None
    effective_date: Optional[date] = None
