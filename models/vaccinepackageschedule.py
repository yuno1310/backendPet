from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class VaccinePackageScheduleBase(SQLModel):
    next_dose_date: Optional[date] = None


class VaccinePackageSchedule(VaccinePackageScheduleBase, table=True):
    __tablename__ = "VaccinePackageSchedule"

    subscription_id: int = Field(
        primary_key=True, foreign_key="PackageSubscription.subscription_id"
    )


class VaccinePackageScheduleCreate(VaccinePackageScheduleBase):
    subscription_id: int


class VaccinePackageScheduleRead(VaccinePackageScheduleBase):
    subscription_id: int


class VaccinePackageScheduleUpdate(SQLModel):
    next_dose_date: Optional[date] = None
