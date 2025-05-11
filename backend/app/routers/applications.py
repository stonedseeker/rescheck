from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from datetime import datetime
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.application import Application, ApplicationCreate, ApplicationUpdate, ApplicationStatus
from app.models.user import User, UserRole
from app.services.auth import get_current_user, get_db
from app.services.resume_parser import parse_resume

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.post("/", response_model=Application)
async def create_application(
   application: ApplicationCreate,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   # Check if job exists
   job = await db.jobs.find_one({"_id": application.job_id})
   if not job:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Job not found"
       )
   
   # Check if user already applied
   existing_application = await db.applications.find_one({
       "job_id": application.job_id,
       "applicant_id": current_user.id
   })
   
   if existing_application:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="You have already applied for this job"
       )
   
   application_dict = application.dict()
   application_dict["_id"] = str(ObjectId())
   application_dict["applicant_id"] = current_user.id
   application_dict["created_at"] = datetime.utcnow()
   application_dict["updated_at"] = datetime.utcnow()
   application_dict["status"] = ApplicationStatus.PENDING
   
   await db.applications.insert_one(application_dict)
   return application_dict

@router.get("/", response_model=List[Application])
async def get_applications(
   job_id: Optional[str] = None,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   query = {}
   
   # Regular users can only see their own applications
   if current_user.role == UserRole.APPLICANT:
       query["applicant_id"] = current_user.id
   
   # Employers can see applications for their jobs
   elif current_user.role == UserRole.EMPLOYER:
       if job_id:
           # Check if this employer owns this job
           job = await db.jobs.find_one({"_id": job_id, "company_id": current_user.id})
           if not job:
               raise HTTPException(
                   status_code=status.HTTP_403_FORBIDDEN,
                   detail="Not authorized to view applications for this job"
               )
           query["job_id"] = job_id
       else:
           # Get all jobs by this employer
           jobs = await db.jobs.find({"company_id": current_user.id}).to_list(1000)
           job_ids = [job["_id"] for job in jobs]
           query["job_id"] = {"$in": job_ids}
   
   # If specific job_id is provided for any user type
   elif job_id:
       query["job_id"] = job_id
   
   applications = await db.applications.find(query).to_list(1000)
   return applications

@router.get("/{application_id}", response_model=Application)
async def get_application(
   application_id: str,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   application = await db.applications.find_one({"_id": application_id})
   if not application:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Application not found"
       )
   
   # Check permissions
   if (current_user.role == UserRole.APPLICANT and application["applicant_id"] != current_user.id):
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Not authorized to view this application"
       )
   
   if current_user.role == UserRole.EMPLOYER:
       job = await db.jobs.find_one({"_id": application["job_id"]})
       if job and job["company_id"] != current_user.id:
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Not authorized to view this application"
           )
   
   return application

@router.put("/{application_id}", response_model=Application)
async def update_application(
   application_id: str,
   application_update: ApplicationUpdate,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   application = await db.applications.find_one({"_id": application_id})
   if not application:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Application not found"
       )
   
   # Only employers who own the job or admins can update status
   if current_user.role not in [UserRole.ADMIN, UserRole.EMPLOYER]:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Not authorized to update application status"
       )
   
   if current_user.role == UserRole.EMPLOYER:
       job = await db.jobs.find_one({"_id": application["job_id"]})
       if job["company_id"] != current_user.id:
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Not authorized to update this application"
           )
   
   update_data = {k: v for k, v in application_update.dict(exclude_unset=True).items()}
   update_data["updated_at"] = datetime.utcnow()
   
   await db.applications.update_one({"_id": application_id}, {"$set": update_data})
   
   return await db.applications.find_one({"_id": application_id})

@router.post("/upload-resume")
async def upload_resume(
   file: UploadFile = File(...),
   current_user: User = Depends(get_current_user)
):
   # This is a placeholder for file upload logic
   # In a real implementation, you would:
   # 1. Save the file to cloud storage (AWS S3, Google Cloud Storage, etc.)
   # 2. Return the URL to the saved file
   
   # For now, we'll just return a mock URL
   file_location = f"resumes/{current_user.id}/{file.filename}"
   return {"resume_url": file_location}

