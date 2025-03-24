#!/usr/bin/env python3
from supabase import create_client, Client
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration 
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

def align_job_ids():
    """Update the job_id in interviews to match the job_posting_id in applications."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # First, get all interviews
        response = supabase.table("interviews").select("*").execute()
        if not response.data:
            print("No interviews found in the database.")
            return
        
        print(f"Found {len(response.data)} interviews")
        
        # Get all applications
        app_response = supabase.table("applications").select("*").execute()
        if not app_response.data:
            print("No applications found in the database.")
            return
        
        print(f"Found {len(app_response.data)} applications")
        
        # Build a mapping of candidate_id to job_posting_id from applications
        candidate_job_map = {}
        for app in app_response.data:
            candidate_id = app.get('candidate_id')
            job_posting_id = app.get('job_posting_id')
            
            if candidate_id and job_posting_id:
                # Store all job_posting_ids for each candidate
                if candidate_id not in candidate_job_map:
                    candidate_job_map[candidate_id] = []
                candidate_job_map[candidate_id].append(job_posting_id)
        
        print(f"Built mapping for {len(candidate_job_map)} candidates")
        
        # Create a test update for the first interview
        if len(response.data) == 0:
            print("No interviews to update")
            return
            
        # For each interview, try to find a matching application
        updated_count = 0
        for interview in response.data:
            interview_id = interview.get('id')
            candidate_id = interview.get('candidate_id')
            current_job_id = interview.get('job_id')
            
            if not candidate_id:
                print(f"Interview {interview_id}: No candidate_id, skipping")
                continue

            if candidate_id in candidate_job_map:
                # Get the first job_posting_id for this candidate (assuming one application per candidate)
                new_job_id = candidate_job_map[candidate_id][0]
                
                if current_job_id == new_job_id:
                    print(f"Interview {interview_id}: Job ID already matches {new_job_id}, skipping")
                    continue
                    
                # Update the interview with the new job_id
                update_response = supabase.table('interviews').update({
                    'job_id': new_job_id
                }).eq('id', interview_id).execute()
                
                print(f"Interview {interview_id}: Updated job_id from {current_job_id} to {new_job_id}")
                updated_count += 1
            else:
                print(f"Interview {interview_id}: No matching application for candidate {candidate_id}, skipping")
                
        print(f"\nUpdate complete. Updated {updated_count} interviews.")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    align_job_ids() 