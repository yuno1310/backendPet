from typing import Optional
from sqlmodel import Field, SQLModel


class ServiceTypeBase(SQLModel):
    type_name: str = Field(max_length=100)


class ServiceType(ServiceTypeBase, table=True):
    __tablename__ = "ServiceType"

    type_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )


class ServiceTypeCreate(ServiceTypeBase):
    pass


class ServiceTypeRead(ServiceTypeBase):
    type_id: int


class ServiceTypeUpdate(SQLModel):
    type_name: Optional[str] = Field(default=None, max_length=100)
