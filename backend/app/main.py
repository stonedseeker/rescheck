# app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.routers import auth, jobs, applications

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Application Platform")

# CORS configuration
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:3000"],  # React frontend URL
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)

@app.on_event("startup")
async def startup_db_client():
   try:
       app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
       app.mongodb = app.mongodb_client[settings.MONGODB_DB]
       logger.debug(f"Connected to MongoDB: {settings.MONGODB_URL}")
       
       # Create indexes for faster queries
       await app.mongodb.users.create_index("email", unique=True)
       await app.mongodb.jobs.create_index("company_id")
       await app.mongodb.applications.create_index([("job_id", 1), ("applicant_id", 1)], unique=True)
   except Exception as e:
       logger.error(f"Failed to connect to MongoDB: {str(e)}")
       raise

@app.on_event("shutdown")
async def shutdown_db_client():
   app.mongodb_client.close()

@app.get("/")
async def root():
   return {"message": "Welcome to the Job Application Platform API"}

@app.get("/api/health")
async def health_check():
   return {"status": "healthy"}

if __name__ == "__main__":
   import uvicorn
   uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from motor.motor_asyncio import AsyncIOMotorClient
#
# from app.config import settings
# from app.routers import auth
# import logging
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
# app = FastAPI(title="Job Application Platform")
#
# # CORS configuration
# app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["http://localhost:3000"],  # React frontend URL
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(auth.router)
#
# @app.on_event("startup")
# async def startup_db_client():
#    try:
#        app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
#        app.mongodb = app.mongodb_client[settings.MONGODB_DB]
#        logger.debug(f"Connected to MongoDB: {settings.MONGODB_URL}")
#
#        # Create indexes for faster queries
#        await app.mongodb.users.create_index("email", unique=True)
#    except Exception as e:
#        logger.error(f"Failed to connect to MongoDB: {str(e)}")
#        raise
#
#
#
#
# @app.on_event("shutdown")
# async def shutdown_db_client():
#    app.mongodb_client.close()
#
# @app.get("/api/health")
# def health_check():
#    return {"status": "healthy"}
#
# @app.get("/")
# def read_root():
#    return {"message": "Jobs Platform API is live"}
#
# if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
#
