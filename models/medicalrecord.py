from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel


class MedicalRecordBase(SQLModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    re_exam_date: Optional[date] = None
    notes: Optional[str] = None


class MedicalRecord(MedicalRecordBase, table=True):
    __tablename__ = "MedicalRecord"

    medical_id: int = Field(
        primary_key=True, foreign_key="ServiceRecord.service_record_id"
    )
    vet_id: int = Field(foreign_key="Employee.employee_id")
    pet_id: int = Field(foreign_key="Pet.pet_id")


class MedicalRecordCreate(MedicalRecordBase):
    medical_id: int
    vet_id: int
    pet_id: int


class MedicalRecordRead(MedicalRecordBase):
    medical_id: int
    vet_id: int
    pet_id: int


class MedicalRecordUpdate(SQLModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    re_exam_date: Optional[date] = None
    notes: Optional[str] = None
