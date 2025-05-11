from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from bson.objectid import ObjectId

from app.models.user import UserCreate, User, UserRole
from app.services.auth import (
   authenticate_user, create_user, get_db,
   create_access_token, verify_google_token
)
from app.config import settings

class GoogleLoginRequest(BaseModel):
   token: str

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=User)
async def register_user(
   user_create: UserCreate,
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   return await create_user(db, user_create)

@router.post("/token")
async def login_for_access_token(
   form_data: OAuth2PasswordRequestForm = Depends(),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   user = await authenticate_user(db, form_data.username, form_data.password)
   if not user:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Incorrect email or password",
           headers={"WWW-Authenticate": "Bearer"},
       )
   
   access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
   access_token = create_access_token(
       data={"sub": user.email}, expires_delta=access_token_expires
   )
   
   return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google/login")
async def google_login(
   request: GoogleLoginRequest,
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   token = request.token
   
   if not token:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="Token is required"
       )
   
   user_data = await verify_google_token(token)
   
   # Check if user exists
   user_exists = await db.users.find_one({"email": user_data["email"]})
   
   if not user_exists:
       # Create new user
       new_user = {
           "_id": str(ObjectId()),
           "email": user_data["email"],
           "name": user_data.get("name", ""),
           "is_active": True,
           "role": UserRole.APPLICANT,
           "google_id": user_data["sub"],
           "profile_picture": user_data.get("picture"),
           "created_at": datetime.now(),
           "updated_at": datetime.now()
       }
       await db.users.insert_one(new_user)
   else:
       # Update existing user
       await db.users.update_one(
           {"email": user_data["email"]},
           {"$set": {
               "google_id": user_data["sub"],
               "profile_picture": user_data.get("picture"),
               "updated_at": datetime.now()
           }}
       )
   
   access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
   access_token = create_access_token(
       data={"sub": user_data["email"]}, expires_delta=access_token_expires
   )
   
   return {"access_token": access_token, "token_type": "bearer"}

