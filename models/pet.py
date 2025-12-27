from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum


# Enum for Gender validation
class PetGender(str, Enum):
    MALE = "Đực"
    FEMALE = "Cái"


# Base Pet model with shared fields
class PetBase(SQLModel):
    """Base model containing fields common to all Pet models"""

    pet_name: str = Field(max_length=100, description="Tên thú cưng")
    species: str = Field(max_length=50, description="Loài (chó, mèo, ...)")
    breed: Optional[str] = Field(default=None, max_length=50, description="Giống")
    date_of_birth: Optional[date] = Field(default=None, description="Ngày sinh")
    gender: Optional[PetGender] = Field(default=None, description="Giới tính (Đực/Cái)")
    health_status: Optional[str] = Field(
        default=None, description="Tình trạng sức khỏe"
    )


# Database table model (with table=True)
class Pet(PetBase, table=True):
    """
    Pet table model - represents the actual database table
    Maps to [dbo].[Pet] in SQL Server
    """

    __tablename__ = "Pet"

    pet_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
        description="ID thú cưng (auto-increment)",
    )

    customer_id: int = Field(
        foreign_key="Customer.customer_id", description="ID khách hàng sở hữu"
    )

    # Relationship with Customer (assuming you have a Customer model)
    # customer: Optional["Customer"] = Relationship(back_populates="pets")


# Create model (for POST requests - no pet_id needed)
class PetCreate(PetBase):
    """Model for creating a new pet - used in POST /pets/"""

    customer_id: int = Field(description="ID khách hàng sở hữu")


# Read model (for GET responses - includes pet_id)
class PetRead(PetBase):
    """Model for reading pet data - used in GET responses"""

    pet_id: int
    customer_id: int


# Update model (all fields optional for PATCH requests)
class PetUpdate(SQLModel):
    pet_name: Optional[str] = Field(default=None, max_length=100)
    species: Optional[str] = Field(default=None, max_length=50)
    breed: Optional[str] = Field(default=None, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[PetGender] = None
    health_status: Optional[str] = None
    customer_id: Optional[int] = None
