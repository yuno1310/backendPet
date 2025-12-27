from datetime import date
from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel


class MembershipTier(str, Enum):
    BASIC = "Basic"
    LOYAL = "Loyal"
    VIP = "VIP"


class CustomerBase(SQLModel):
    name: str = Field(max_length=100)
    phone_number: str = Field(max_length=10, unique=True)
    email: Optional[str] = Field(default=None, max_length=100)
    citizen_id: str = Field(max_length=12, unique=True)
    gender: Optional[str] = Field(default=None, max_length=10)
    date_of_birth: Optional[date] = None
    loyalty_points: int = Field(default=0, ge=0)
    membership_tier: MembershipTier = Field(default=MembershipTier.BASIC)


class Customer(CustomerBase, table=True):
    __tablename__ = "Customer"

    customer_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    customer_id: int


class CustomerUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=10)
    email: Optional[str] = Field(default=None, max_length=100)
    citizen_id: Optional[str] = Field(default=None, max_length=12)
    gender: Optional[str] = Field(default=None, max_length=10)
    date_of_birth: Optional[date] = None
    loyalty_points: Optional[int] = Field(default=None, ge=0)
    membership_tier: Optional[MembershipTier] = None
