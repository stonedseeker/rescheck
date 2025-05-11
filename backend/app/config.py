from pydantic import BaseSettings, EmailStr

class Settings(BaseSettings):
   # MongoDB settings
   MONGODB_URL: str
   MONGODB_DB: str
   
   # JWT settings
   SECRET_KEY: str
   ALGORITHM: str = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
   
   # Google OAuth
   GOOGLE_CLIENT_ID: str
   GOOGLE_CLIENT_SECRET: str
   GOOGLE_REDIRECT_URI: str
   
   # OpenAI
   OPENAI_API_KEY: str

   class Config:
       env_file = ".env"

settings = Settings()

