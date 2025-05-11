from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.job import Job, JobCreate, JobUpdate
from app.models.user import User, UserRole
from app.services.auth import get_current_user, get_db

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/", response_model=Job)
async def create_job(
   job: JobCreate,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   # Only employers can create jobs
   if current_user.role != UserRole.EMPLOYER and current_user.role != UserRole.ADMIN:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Only employers can create job postings"
       )
   
   job_dict = job.dict()
   job_dict["_id"] = str(ObjectId())
   job_dict["created_at"] = datetime.utcnow()
   job_dict["updated_at"] = datetime.utcnow()
   job_dict["company_id"] = current_user.id
   
   await db.jobs.insert_one(job_dict)
   return job_dict

@router.get("/", response_model=List[Job])
async def get_jobs(
   skip: int = 0, 
   limit: int = 10,
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   jobs = await db.jobs.find({"active": True}).skip(skip).limit(limit).to_list(limit)
   return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job(
   job_id: str,
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   job = await db.jobs.find_one({"_id": job_id})
   if job is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Job not found"
       )
   return job

@router.put("/{job_id}", response_model=Job)
async def update_job(
   job_id: str,
   job_update: JobUpdate,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   job = await db.jobs.find_one({"_id": job_id})
   if job is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Job not found"
       )
   
   # Only the job creator or admin can update
   if job["company_id"] != current_user.id and current_user.role != UserRole.ADMIN:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Not authorized to update this job"
       )
   
   update_data = {k: v for k, v in job_update.dict(exclude_unset=True).items()}
   update_data["updated_at"] = datetime.utcnow()
   
   await db.jobs.update_one({"_id": job_id}, {"$set": update_data})
   
   return await db.jobs.find_one({"_id": job_id})

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
   job_id: str,
   current_user: User = Depends(get_current_user),
   db: AsyncIOMotorDatabase = Depends(get_db)
):
   job = await db.jobs.find_one({"_id": job_id})
   if job is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="Job not found"
       )
   
   # Only the job creator or admin can delete
   if job["company_id"] != current_user.id and current_user.role != UserRole.ADMIN:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Not authorized to delete this job"
       )
   
   await db.jobs.delete_one({"_id": job_id})

