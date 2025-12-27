from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel


class BookingStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class BookingBase(SQLModel):
    booking_time: datetime
    customer_name: Optional[str] = Field(default=None, max_length=50)
    species: Optional[str] = Field(default=None, max_length=20)
    phone_number: str = Field(max_length=10)
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    note: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.now)


class Booking(BookingBase, table=True):
    __tablename__ = "Booking"

    booking_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    customer_id: Optional[int] = Field(default=None, foreign_key="Customer.customer_id")
    branch_id: int = Field(foreign_key="Branch.branch_id")
    receptionist_id: int = Field(foreign_key="Employee.employee_id")


class BookingCreate(BookingBase):
    customer_id: Optional[int] = None
    branch_id: int
    receptionist_id: int


class BookingRead(BookingBase):
    booking_id: int
    customer_id: Optional[int]
    branch_id: int
    receptionist_id: int


class BookingUpdate(SQLModel):
    booking_time: Optional[datetime] = None
    customer_name: Optional[str] = Field(default=None, max_length=50)
    species: Optional[str] = Field(default=None, max_length=20)
    phone_number: Optional[str] = Field(default=None, max_length=10)
    status: Optional[BookingStatus] = None
    note: Optional[str] = None
