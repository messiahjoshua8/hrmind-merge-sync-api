#!/usr/bin/env python3
from supabase import create_client, Client
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration 
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

def create_test_application():
    """Create a test application that matches one of our interview records."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # First, get all interviews to find one to use
        response = supabase.table("interviews").select("*").execute()
        if not response.data:
            print("No interviews found in the database.")
            return
        
        # Let's use the most recently imported interview (the last one with FAILED status)
        interview = None
        for i in response.data:
            if i.get('status') == 'FAILED':
                interview = i
                break
        
        if not interview:
            # If no FAILED interview, use the first one
            interview = response.data[0]
        
        candidate_id = interview.get('candidate_id')
        job_id = interview.get('job_id')
        
        print(f"Selected interview {interview.get('id')} with candidate_id {candidate_id} and job_id {job_id}")
        
        # Get job details
        job_response = supabase.table("jobs").select("*").eq('id', job_id).execute()
        if not job_response.data or len(job_response.data) == 0:
            print(f"Job with ID {job_id} not found")
            return
            
        # Create a new application
        application_id = str(uuid.uuid4())
        
        application_data = {
            "id": application_id,
            "organization_id": "05b3cc97-5d8a-4632-9959-29d0fc379fc9",
            "user_id": "e3c418cc-4b8a-4d7b-b76d-18d0752a2e4c",
            "created_by": "e3c418cc-4b8a-4d7b-b76d-18d0752a2e4c",
            "candidate_id": candidate_id,
            "job_posting_id": job_id,  # Use the job_id from the interview as job_posting_id
            "status": "APPLIED",
            "applied_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Insert the new application
        insert_response = supabase.table('applications').insert(application_data).execute()
        
        print(f"Created new application with ID {application_id}")
        print(f"Candidate ID: {candidate_id}")
        print(f"Job Posting ID: {job_id}")
        
        return application_id
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    create_test_application() 