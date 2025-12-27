from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class VaccineBase(SQLModel):
    vaccine_name: str = Field(max_length=100)
    vaccine_type: Optional[str] = Field(default=None, max_length=50)
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None


class Vaccine(VaccineBase, table=True):
    __tablename__ = "Vaccine"

    vaccine_id: int = Field(primary_key=True, foreign_key="Product.product_id")


class VaccineCreate(VaccineBase):
    vaccine_id: int


class VaccineRead(VaccineBase):
    vaccine_id: int


class VaccineUpdate(SQLModel):
    vaccine_name: Optional[str] = Field(default=None, max_length=100)
    vaccine_type: Optional[str] = Field(default=None, max_length=50)
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
