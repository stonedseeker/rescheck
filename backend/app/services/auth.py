import datetime
from datetime import timedelta
from typing import Optional
from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings
from app.models.user import UserInDB, User, UserCreate, UserRole
from app.utils.security import verify_password, get_password_hash, create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_db() -> AsyncIOMotorDatabase:
   client = AsyncIOMotorClient(settings.MONGODB_URL)
   return client[settings.MONGODB_DB]

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
   user_data = await db.users.find_one({"email": email})
   if user_data:
       return UserInDB(**user_data)
   return None

async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[UserInDB]:
   user = await get_user_by_email(db, email)
   if not user:
       return None
   if not user.hashed_password:
       return None
   if not verify_password(password, user.hashed_password):
       return None
   return user


async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> User:
   user_exists = await get_user_by_email(db, user.email)
   if user_exists:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="Email already registered"
       )
   
   user_dict = user.dict()
   if user.password:
       user_dict["hashed_password"] = get_password_hash(user.password)
   del user_dict["password"]
   
   # Generate ID and timestamps
   user_dict["_id"] = str(ObjectId())
   user_dict["created_at"] = datetime.datetime.now()
   user_dict["updated_at"] = datetime.datetime.now()
   
   await db.users.insert_one(user_dict)
   
   # For the return object, map _id to id as expected by User model
   return_dict = user_dict.copy()
   return_dict["id"] = return_dict["_id"]
   
   return User(**return_dict)


async def get_current_user(
   token: str = Depends(oauth2_scheme),
   db: AsyncIOMotorDatabase = Depends(get_db)
) -> User:
   credentials_exception = HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Could not validate credentials",
       headers={"WWW-Authenticate": "Bearer"},
   )
   try:
       payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
       email: str = payload.get("sub")
       if email is None:
           raise credentials_exception
   except JWTError:
       raise credentials_exception
   
   user = await get_user_by_email(db, email)
   if user is None:
       raise credentials_exception
   return User(**user.dict())

async def verify_google_token(token: str) -> dict:
   try:
       idinfo = id_token.verify_oauth2_token(
           token, requests.Request(), settings.GOOGLE_CLIENT_ID
       )
       return idinfo
   except Exception as e:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail=f"Invalid Google token: {str(e)}"
       )

