from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class PurchaseRecordBase(SQLModel):
    total_price: Optional[Decimal] = Field(
        default=None, max_digits=18, decimal_places=0
    )


class PurchaseRecord(PurchaseRecordBase, table=True):
    __tablename__ = "PurchaseRecord"

    purchase_record_id: int = Field(
        primary_key=True, foreign_key="ServiceRecord.service_record_id"
    )
    sales_id: int = Field(foreign_key="Employee.employee_id")


class PurchaseRecordCreate(PurchaseRecordBase):
    purchase_record_id: int
    sales_id: int


class PurchaseRecordRead(PurchaseRecordBase):
    purchase_record_id: int
    sales_id: int


class PurchaseRecordUpdate(SQLModel):
    total_price: Optional[Decimal] = None
