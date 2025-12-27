from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class VaccinationRecordBase(SQLModel):
    injection_date: Optional[datetime] = None
    dose: Optional[str] = Field(default=None, max_length=50)


class VaccinationRecord(VaccinationRecordBase, table=True):
    __tablename__ = "VaccinationRecord"

    vaccination_id: int = Field(
        primary_key=True, foreign_key="ServiceRecord.service_record_id"
    )
    vet_id: int = Field(foreign_key="Employee.employee_id")
    pet_id: int = Field(foreign_key="Pet.pet_id")
    vaccine_id: int = Field(foreign_key="Vaccine.vaccine_id")
    subscription_id: Optional[int] = Field(
        default=None, foreign_key="PackageSubscription.subscription_id"
    )


class VaccinationRecordCreate(VaccinationRecordBase):
    vaccination_id: int
    vet_id: int
    pet_id: int
    vaccine_id: int
    subscription_id: Optional[int] = None


class VaccinationRecordRead(VaccinationRecordBase):
    vaccination_id: int
    vet_id: int
    pet_id: int
    vaccine_id: int
    subscription_id: Optional[int]


class VaccinationRecordUpdate(SQLModel):
    injection_date: Optional[datetime] = None
    dose: Optional[str] = Field(default=None, max_length=50)
    subscription_id: Optional[int] = None
