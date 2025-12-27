from typing import Optional
from sqlmodel import Field, SQLModel


class PrescriptionBase(SQLModel):
    note: Optional[str] = None


class Prescription(PrescriptionBase, table=True):
    __tablename__ = "Prescription"

    prescription_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    medical_id: Optional[int] = Field(
        default=None, foreign_key="MedicalRecord.medical_id", unique=True
    )


class PrescriptionCreate(PrescriptionBase):
    medical_id: Optional[int] = None


class PrescriptionRead(PrescriptionBase):
    prescription_id: int
    medical_id: Optional[int]


class PrescriptionUpdate(SQLModel):
    note: Optional[str] = None
