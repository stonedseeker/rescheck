from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class UserRole(str, Enum):
   APPLICANT = "applicant"
   EMPLOYER = "employer"
   ADMIN = "admin"

class UserBase(BaseModel):
   email: EmailStr
   name: str
   role: UserRole = UserRole.APPLICANT
   is_active: bool = True

class UserCreate(UserBase):
   password: Optional[str] = None

class UserInDB(UserBase):
   id: str = Field(..., alias="_id")
   hashed_password: Optional[str] = None
   created_at: datetime = Field(default_factory=datetime.utcnow)
   updated_at: datetime = Field(default_factory=datetime.utcnow)
   google_id: Optional[str] = None
   profile_picture: Optional[str] = None

class User(UserBase):
   id: str
   created_at: datetime
   profile_picture: Optional[str] = None

   class Config:
       orm_mode = True

