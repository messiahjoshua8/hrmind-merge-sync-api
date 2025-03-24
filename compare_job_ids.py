#!/usr/bin/env python3
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration 
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

def compare_job_ids():
    """Compare job IDs between tables to find matches."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all job IDs
        jobs_response = supabase.table("jobs").select("id,title").execute()
        job_postings_response = supabase.table("job_postings").select("id,name").execute()
        interviews_response = supabase.table("interviews").select("id,job_id,candidate_id").execute()
        
        # Extract the IDs
        job_ids = {job.get('id'): job.get('title') for job in jobs_response.data} if jobs_response.data else {}
        job_posting_ids = {jp.get('id'): jp.get('name') for jp in job_postings_response.data} if job_postings_response.data else {}
        interview_job_ids = {interview.get('id'): {'job_id': interview.get('job_id'), 'candidate_id': interview.get('candidate_id')} 
                         for interview in interviews_response.data} if interviews_response.data else {}
        
        print(f"Found {len(job_ids)} jobs, {len(job_posting_ids)} job postings, and {len(interview_job_ids)} interviews")
        
        # Check if any job IDs in interviews match job IDs in jobs table
        matching_job_ids = []
        missing_job_ids = []
        for interview_id, data in interview_job_ids.items():
            job_id = data.get('job_id')
            if job_id in job_ids:
                matching_job_ids.append((interview_id, job_id, job_ids[job_id]))
            elif job_id:
                missing_job_ids.append((interview_id, job_id))
        
        print(f"\nInterviews with job_id matching jobs table: {len(matching_job_ids)}")
        for interview_id, job_id, title in matching_job_ids:
            print(f"Interview {interview_id}: Job {job_id} ({title})")
        
        print(f"\nInterviews with job_id NOT matching jobs table: {len(missing_job_ids)}")
        for interview_id, job_id in missing_job_ids:
            print(f"Interview {interview_id}: Missing job {job_id}")
            
            # Check if this job_id is in job_postings
            if job_id in job_posting_ids:
                print(f"  But found in job_postings: {job_posting_ids[job_id]}")
        
        # Check if any job IDs in interviews match job posting IDs
        matching_job_posting_ids = []
        for interview_id, data in interview_job_ids.items():
            job_id = data.get('job_id')
            if job_id in job_posting_ids:
                matching_job_posting_ids.append((interview_id, job_id, job_posting_ids[job_id]))
        
        print(f"\nInterviews with job_id matching job_postings table: {len(matching_job_posting_ids)}")
        for interview_id, job_id, name in matching_job_posting_ids:
            print(f"Interview {interview_id}: Job Posting {job_id} ({name})")
        
        # Check if there are job postings without matching jobs
        job_postings_without_jobs = []
        for jp_id, name in job_posting_ids.items():
            if jp_id not in job_ids:
                job_postings_without_jobs.append((jp_id, name))
        
        print(f"\nJob postings without matching jobs: {len(job_postings_without_jobs)}")
        for jp_id, name in job_postings_without_jobs:
            print(f"Job Posting {jp_id}: {name}")
            
        # Finally, suggest a job ID that exists in both jobs and job_postings
        common_ids = set(job_ids.keys()) & set(job_posting_ids.keys())
        if common_ids:
            print(f"\nCommon IDs between jobs and job_postings: {len(common_ids)}")
            for job_id in common_ids:
                print(f"Job ID: {job_id}")
                print(f"  Job Title: {job_ids[job_id]}")
                print(f"  Job Posting Name: {job_posting_ids[job_id]}")
        else:
            print("\nNo common IDs between jobs and job_postings")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    compare_job_ids() 