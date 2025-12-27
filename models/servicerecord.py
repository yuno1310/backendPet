from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ServiceRecordBase(SQLModel):
    created_date: datetime = Field(default_factory=datetime.now)


class ServiceRecord(ServiceRecordBase, table=True):
    __tablename__ = "ServiceRecord"

    service_record_id: int = Field(
        primary_key=True, foreign_key="ServiceOrder.order_id"
    )


class ServiceRecordCreate(ServiceRecordBase):
    service_record_id: int


class ServiceRecordRead(ServiceRecordBase):
    service_record_id: int
