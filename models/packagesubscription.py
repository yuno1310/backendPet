from datetime import date
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class PackageSubscriptionBase(SQLModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    remaining_shots: Optional[int] = None
    cancelation_fee: Optional[Decimal] = Field(
        default=None, max_digits=18, decimal_places=0
    )


class PackageSubscription(PackageSubscriptionBase, table=True):
    __tablename__ = "PackageSubscription"

    subscription_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    pet_id: int = Field(foreign_key="Pet.pet_id")
    package_id: int = Field(foreign_key="VaccinePackage.package_id")


class PackageSubscriptionCreate(PackageSubscriptionBase):
    pet_id: int
    package_id: int


class PackageSubscriptionRead(PackageSubscriptionBase):
    subscription_id: int
    pet_id: int
    package_id: int


class PackageSubscriptionUpdate(SQLModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    remaining_shots: Optional[int] = None
    cancelation_fee: Optional[Decimal] = None
