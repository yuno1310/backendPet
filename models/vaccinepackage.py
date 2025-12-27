from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class VaccinePackageBase(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    duration: Optional[int] = None  # Months
    total_shots: Optional[int] = None
    price: Optional[Decimal] = Field(default=None, max_digits=18, decimal_places=0)
    discount: Optional[float] = None


class VaccinePackage(VaccinePackageBase, table=True):
    __tablename__ = "VaccinePackage"

    package_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class VaccinePackageCreate(VaccinePackageBase):
    pass


class VaccinePackageRead(VaccinePackageBase):
    package_id: int


class VaccinePackageUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    duration: Optional[int] = None
    total_shots: Optional[int] = None
    price: Optional[Decimal] = None
    discount: Optional[float] = None
