from typing import Optional
from sqlmodel import Field, SQLModel


class PackageDetailsBase(SQLModel):
    scheduled_week: Optional[int] = None


class PackageDetails(PackageDetailsBase, table=True):
    __tablename__ = "PackageDetails"

    package_id: int = Field(foreign_key="VaccinePackage.package_id", primary_key=True)
    vaccine_id: int = Field(foreign_key="Vaccine.vaccine_id", primary_key=True)


class PackageDetailsCreate(PackageDetailsBase):
    package_id: int
    vaccine_id: int


class PackageDetailsRead(PackageDetailsBase):
    package_id: int
    vaccine_id: int


class PackageDetailsUpdate(SQLModel):
    scheduled_week: Optional[int] = None
