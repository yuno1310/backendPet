from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel


class ServiceBase(SQLModel):
    name: str = Field(max_length=100)
    price: Optional[Decimal] = Field(
        default=None, ge=0, max_digits=18, decimal_places=0
    )


class Service(ServiceBase, table=True):
    __tablename__ = "Service"

    service_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    type_id: int = Field(foreign_key="ServiceType.type_id")


class ServiceCreate(ServiceBase):
    type_id: int


class ServiceRead(ServiceBase):
    service_id: int
    type_id: int


class ServiceUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    price: Optional[Decimal] = None
    type_id: Optional[int] = None
