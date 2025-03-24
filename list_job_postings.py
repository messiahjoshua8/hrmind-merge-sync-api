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

def list_job_postings():
    """List all job postings in the database."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for job postings
        print("Querying job_postings table...")
        response = supabase.table("job_postings").select("*").execute()
        
        if not response.data:
            print("No job postings found in the database.")
            return
        
        print(f"Found {len(response.data)} job postings")
        print("\nJob Postings summary:")
        print("=" * 80)
        
        for idx, job in enumerate(response.data):
            print(f"{idx+1}. Job Posting ID: {job.get('id', 'N/A')}")
            print(f"   Name: {job.get('name', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Status: {job.get('status', 'N/A')}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_job_postings() 