from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class JobType(str, Enum):
   FULL_TIME = "full_time"
   PART_TIME = "part_time"
   CONTRACT = "contract"
   INTERNSHIP = "internship"
   FREELANCE = "freelance"

class ExperienceLevel(str, Enum):
   ENTRY = "entry"
   JUNIOR = "junior"
   MID = "mid"
   SENIOR = "senior"
   LEAD = "lead"
   EXECUTIVE = "executive"

class JobBase(BaseModel):
   title: str
   company_id: str
   description: str
   requirements: List[str]
   job_type: JobType
   location: str
   remote: bool = False
   salary_min: Optional[float] = None
   salary_max: Optional[float] = None
   experience_level: ExperienceLevel
   skills: List[str]
   active: bool = True

class JobCreate(JobBase):
   pass

class JobUpdate(BaseModel):
   title: Optional[str] = None
   description: Optional[str] = None
   requirements: Optional[List[str]] = None
   job_type: Optional[JobType] = None
   location: Optional[str] = None
   remote: Optional[bool] = None
   salary_min: Optional[float] = None
   salary_max: Optional[float] = None
   experience_level: Optional[ExperienceLevel] = None
   skills: Optional[List[str]] = None
   active: Optional[bool] = None

class Job(JobBase):
   id: str = Field(..., alias="_id")
   created_at: datetime
   updated_at: datetime
   
   class Config:
       orm_mode = True

