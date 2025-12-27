from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class InventoryBase(SQLModel):
    quantity: int = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.now)


class Inventory(InventoryBase, table=True):
    __tablename__ = "Inventory"

    branch_id: int = Field(foreign_key="Branch.branch_id", primary_key=True)
    product_id: int = Field(foreign_key="Product.product_id", primary_key=True)


class InventoryCreate(InventoryBase):
    branch_id: int
    product_id: int


class InventoryRead(InventoryBase):
    branch_id: int
    product_id: int


class InventoryUpdate(SQLModel):
    quantity: Optional[int] = Field(default=None, ge=0)
