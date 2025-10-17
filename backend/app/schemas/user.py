from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from app.models.user import GenderEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_type: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    phone_number: Optional[str]
    blood_type: Optional[str]
    height_cm: Optional[int]
    weight_kg: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
