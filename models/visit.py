from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class VisitBase(SQLModel):
    time_in: datetime = Field(default_factory=datetime.now)
    is_paid: bool = Field(default=False)


class Visit(VisitBase, table=True):
    __tablename__ = "Visit"

    visit_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    booking_id: Optional[int] = Field(default=None, foreign_key="Booking.booking_id")
    branch_id: int = Field(foreign_key="Branch.branch_id")
    customer_id: int = Field(foreign_key="Customer.customer_id")
    receptionist_id: int = Field(foreign_key="Employee.employee_id")


class VisitCreate(VisitBase):
    booking_id: Optional[int] = None
    branch_id: int
    customer_id: int
    receptionist_id: int


class VisitRead(VisitBase):
    visit_id: int
    booking_id: Optional[int]
    branch_id: int
    customer_id: int
    receptionist_id: int


class VisitUpdate(SQLModel):
    time_in: Optional[datetime] = None
    is_paid: Optional[bool] = None
