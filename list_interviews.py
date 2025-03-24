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

def list_interviews():
    """List all interviews in the database."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for interviews
        print("Querying interviews table...")
        response = supabase.table("interviews").select("*").execute()
        
        if not response.data:
            print("No interviews found in the database.")
            return
        
        print(f"Found {len(response.data)} interviews")
        print("\nInterviews summary:")
        print("=" * 80)
        
        for idx, interview in enumerate(response.data):
            print(f"{idx+1}. Interview ID: {interview.get('id', 'N/A')}")
            print(f"   Application ID: {interview.get('application_id', 'N/A')}")
            print(f"   Job ID: {interview.get('job_id', 'N/A')}")
            print(f"   Candidate ID: {interview.get('candidate_id', 'N/A')}")
            print(f"   Date: {interview.get('date', 'N/A')}")
            print(f"   Result: {interview.get('result', 'N/A')}")
            print(f"   Feedback: {interview.get('feedback', 'N/A')}")
            print(f"   Notes: {interview.get('notes', 'N/A')}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_interviews() 