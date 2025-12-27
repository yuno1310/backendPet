from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class InvoiceBase(SQLModel):
    create_date: datetime = Field(default_factory=datetime.now)
    sub_total: Optional[Decimal] = Field(default=None, max_digits=18, decimal_places=0)
    discount_amount: Optional[Decimal] = Field(
        default=None, max_digits=18, decimal_places=0
    )
    total_amount: Optional[Decimal] = Field(
        default=None, max_digits=18, decimal_places=0
    )
    payment_method: Optional[str] = Field(default=None, max_length=50)


class Invoice(InvoiceBase, table=True):
    __tablename__ = "Invoice"

    invoice_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    visit_id: Optional[int] = Field(default=None, foreign_key="Visit.visit_id")
    customer_id: int = Field(foreign_key="Customer.customer_id")
    receptionist_id: int = Field(foreign_key="Employee.employee_id")


class InvoiceCreate(InvoiceBase):
    visit_id: Optional[int] = None
    customer_id: int
    receptionist_id: int


class InvoiceRead(InvoiceBase):
    invoice_id: int
    visit_id: Optional[int]
    customer_id: int
    receptionist_id: int


class InvoiceUpdate(SQLModel):
    create_date: Optional[datetime] = None
    sub_total: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    payment_method: Optional[str] = Field(default=None, max_length=50)
