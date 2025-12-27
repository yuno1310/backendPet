from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    product_name: str = Field(max_length=100)
    retail_price: Optional[Decimal] = Field(
        default=None, ge=0, max_digits=18, decimal_places=0
    )
    product_type: str = Field(max_length=50, description="Drug, Food, Accessory")


class Product(ProductBase, table=True):
    __tablename__ = "Product"

    product_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    product_id: int


class ProductUpdate(SQLModel):
    product_name: Optional[str] = Field(default=None, max_length=100)
    retail_price: Optional[Decimal] = None
    product_type: Optional[str] = Field(default=None, max_length=50)
