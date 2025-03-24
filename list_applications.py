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

def list_applications():
    """List all applications in the database."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for applications
        print("Querying applications table...")
        response = supabase.table("applications").select("*").execute()
        
        if not response.data:
            print("No applications found in the database.")
            return
        
        print(f"Found {len(response.data)} applications")
        print("\nApplications summary:")
        print("=" * 80)
        
        for idx, application in enumerate(response.data):
            print(f"{idx+1}. Application ID: {application.get('id', 'N/A')}")
            print(f"   Candidate ID: {application.get('candidate_id', 'N/A')}")
            print(f"   Job Posting ID: {application.get('job_posting_id', 'N/A')}")
            print(f"   Status: {application.get('status', 'N/A')}")
            print(f"   Applied At: {application.get('applied_at', 'N/A')}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_applications() 