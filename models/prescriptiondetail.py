from typing import Optional
from sqlmodel import Field, SQLModel


class PrescriptionDetailBase(SQLModel):
    dosage: Optional[str] = Field(default=None, max_length=100)
    quantity: Optional[int] = None
    usage_instruction: Optional[str] = None
    note: Optional[str] = None


class PrescriptionDetail(PrescriptionDetailBase, table=True):
    __tablename__ = "PrescriptionDetail"

    prescription_id: int = Field(
        foreign_key="Prescription.prescription_id", primary_key=True
    )
    drug_id: int = Field(foreign_key="Product.product_id", primary_key=True)


class PrescriptionDetailCreate(PrescriptionDetailBase):
    prescription_id: int
    drug_id: int


class PrescriptionDetailRead(PrescriptionDetailBase):
    prescription_id: int
    drug_id: int


class PrescriptionDetailUpdate(SQLModel):
    dosage: Optional[str] = Field(default=None, max_length=100)
    quantity: Optional[int] = None
    usage_instruction: Optional[str] = None
    note: Optional[str] = None
