from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class ApplicationStatus(str, Enum):
   PENDING = "pending"
   REVIEWING = "reviewing"
   INTERVIEW = "interview"
   REJECTED = "rejected"
   ACCEPTED = "accepted"

class ApplicationBase(BaseModel):
   job_id: str
   applicant_id: str
   cover_letter: Optional[str] = None
   resume_url: str
   status: ApplicationStatus = ApplicationStatus.PENDING

class ApplicationCreate(BaseModel):
   job_id: str
   cover_letter: Optional[str] = None
   resume_url: str

class ApplicationUpdate(BaseModel):
   status: Optional[ApplicationStatus] = None
   feedback: Optional[str] = None
   
class AIFeedback(BaseModel):
   score: float
   analysis: Dict[str, Any]
   match_percentage: float
   skills_matched: List[str]
   skills_missing: List[str]
   recommendations: List[str]

class Application(ApplicationBase):
   id: str = Field(..., alias="_id")
   created_at: datetime
   updated_at: datetime
   feedback: Optional[str] = None
   ai_feedback: Optional[AIFeedback] = None
   
   class Config:
       orm_mode = True


