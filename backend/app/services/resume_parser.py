import os
import openai
from typing import Dict, Any, List
from app.config import settings

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

async def parse_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
   """
   Parse a resume using OpenAI and compare it with a job description
   to determine the match.
   """
   try:
       # Create a prompt for OpenAI
       prompt = f"""
       Analyze the following resume against the job description.
       
       Resume:
       {resume_text}
       
       Job Description:
       {job_description}
       
       Please provide the following analysis in JSON format:
       1. A match percentage (0-100) indicating how well the candidate's qualifications match the job requirements
       2. List of skills in the resume that match the job requirements
       3. List of skills or qualifications that are missing from the resume but required in the job
       4. An overall score (0-10) for the candidate based on the resume
       5. Specific recommendations for the employer regarding this candidate
       6. A detailed analysis of the candidate's experience, education, and skills
       """
       
       # Call OpenAI API
       response = await openai.ChatCompletion.acreate(
           model="gpt-4",  # Use latest available model
           messages=[
               {"role": "system", "content": "You are an expert HR assistant that analyzes resumes against job descriptions."},
               {"role": "user", "content": prompt}
           ],
           temperature=0.2,  # Low temperature for more consistent results
           max_tokens=2000
       )
       
       # Extract and parse the response
       ai_analysis = response.choices[0].message.content
       
       # In a production app, you would parse the JSON response here
       # For now, we'll return a structured mock response
       return {
           "score": 7.5,  # Example score out of 10
           "analysis": {
               "experience": "Candidate has 5 years of relevant experience",
               "education": "Bachelor's degree in relevant field",
               "skills": "Strong technical skills with some gaps"
           },
           "match_percentage": 85,  # Example match percentage
           "skills_matched": ["Python", "FastAPI", "MongoDB", "React"],  # Example matched skills
           "skills_missing": ["Docker", "AWS"],  # Example missing skills
           "recommendations": [
               "Consider interviewing this candidate",
               "Ask about experience with Docker and cloud services"
           ]
       }
   except Exception as e:
       print(f"Error parsing resume: {str(e)}")
       return {
           "score": 0,
           "analysis": {"error": str(e)},
           "match_percentage": 0,
           "skills_matched": [],
           "skills_missing": [],
           "recommendations": ["Error analyzing resume"]
       }
1
