from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class PurchaseDetailsBase(SQLModel):
    quantity: Optional[int] = None
    price: Optional[Decimal] = Field(default=None, max_digits=18, decimal_places=0)


class PurchaseDetails(PurchaseDetailsBase, table=True):
    __tablename__ = "PurchaseDetails"

    purchase_record_id: int = Field(
        foreign_key="PurchaseRecord.purchase_record_id", primary_key=True
    )
    product_id: int = Field(foreign_key="Product.product_id", primary_key=True)
    package_id: int = Field(foreign_key="VaccinePackage.package_id", primary_key=True)


class PurchaseDetailsCreate(PurchaseDetailsBase):
    purchase_record_id: int
    product_id: int
    package_id: int


class PurchaseDetailsRead(PurchaseDetailsBase):
    purchase_record_id: int
    product_id: int
    package_id: int


class PurchaseDetailsUpdate(SQLModel):
    quantity: Optional[int] = None
    price: Optional[Decimal] = None
