from typing import Optional
from decimal import Decimal
from enum import Enum
from sqlmodel import Field, SQLModel


class ServiceOrderStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ServiceOrderBase(SQLModel):
    service_name: Optional[str] = Field(default=None, max_length=100)
    price: Optional[Decimal] = Field(
        default=None, gt=0, max_digits=18, decimal_places=0
    )
    discount: Optional[float] = None
    status: ServiceOrderStatus = Field(default=ServiceOrderStatus.PENDING)
    note: Optional[str] = None


class ServiceOrder(ServiceOrderBase, table=True):
    __tablename__ = "ServiceOrder"

    order_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    visit_id: int = Field(foreign_key="Visit.visit_id")
    service_id: int = Field(foreign_key="Service.service_id")
    pet_id: int = Field(foreign_key="Pet.pet_id")


class ServiceOrderCreate(ServiceOrderBase):
    visit_id: int
    service_id: int
    pet_id: int


class ServiceOrderRead(ServiceOrderBase):
    order_id: int
    visit_id: int
    service_id: int
    pet_id: int


class ServiceOrderUpdate(SQLModel):
    service_name: Optional[str] = Field(default=None, max_length=100)
    price: Optional[Decimal] = None
    discount: Optional[float] = None
    status: Optional[ServiceOrderStatus] = None
    note: Optional[str] = None
