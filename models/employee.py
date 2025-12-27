from datetime import date
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class EmployeeBase(SQLModel):
    name: str = Field(max_length=100)
    date_of_birth: date
    start_date: date
    gender: Optional[str] = Field(default=None, max_length=10)
    salary: Optional[Decimal] = Field(
        default=None, gt=0, max_digits=18, decimal_places=0
    )
    position: str = Field(max_length=50, description="Vet, Receptionist, Sale, Manager")


class Employee(EmployeeBase, table=True):
    __tablename__ = "Employee"

    employee_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    branch_id: Optional[int] = Field(default=None, foreign_key="Branch.branch_id")


class EmployeeCreate(EmployeeBase):
    branch_id: Optional[int] = None


class EmployeeRead(EmployeeBase):
    employee_id: int
    branch_id: Optional[int]


class EmployeeUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[date] = None
    start_date: Optional[date] = None
    gender: Optional[str] = Field(default=None, max_length=10)
    salary: Optional[Decimal] = None
    position: Optional[str] = Field(default=None, max_length=50)
    branch_id: Optional[int] = None
