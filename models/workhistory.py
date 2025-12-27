from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class WorkHistoryBase(SQLModel):
    start_date: date
    end_date: Optional[date] = None
    reason: Optional[str] = Field(default=None, max_length=255)


class WorkHistory(WorkHistoryBase, table=True):
    __tablename__ = "WorkHistory"

    branch_id: int = Field(foreign_key="Branch.branch_id", primary_key=True)
    employee_id: int = Field(foreign_key="Employee.employee_id", primary_key=True)
    start_date: date = Field(primary_key=True)


class WorkHistoryCreate(WorkHistoryBase):
    branch_id: int
    employee_id: int


class WorkHistoryRead(WorkHistoryBase):
    branch_id: int
    employee_id: int


class WorkHistoryUpdate(SQLModel):
    end_date: Optional[date] = None
    reason: Optional[str] = Field(default=None, max_length=255)
