from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel


class BookingDetailStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class BookingDetailsBase(SQLModel):
    note: Optional[str] = None
    status: BookingDetailStatus = Field(default=BookingDetailStatus.PENDING)


class BookingDetails(BookingDetailsBase, table=True):
    __tablename__ = "BookingDetails"

    booking_id: int = Field(foreign_key="Booking.booking_id", primary_key=True)
    service_id: int = Field(foreign_key="Service.service_id", primary_key=True)
    pet_id: int = Field(foreign_key="Pet.pet_id", primary_key=True)


class BookingDetailsCreate(BookingDetailsBase):
    booking_id: int
    service_id: int
    pet_id: int


class BookingDetailsRead(BookingDetailsBase):
    booking_id: int
    service_id: int
    pet_id: int


class BookingDetailsUpdate(SQLModel):
    note: Optional[str] = None
    status: Optional[BookingDetailStatus] = None
