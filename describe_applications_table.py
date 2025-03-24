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

def describe_table():
    """Describe the applications table structure."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for table information (this won't tell us column info but will confirm if the table exists)
        print("Checking if the applications table exists...")
        response = supabase.table("applications").select("*").limit(1).execute()
        print(f"Table exists, found {len(response.data or [])} records")
        
        # Try to query metadata information
        # Fallback: Try to get a record and list its keys
        response = supabase.table("applications").select("*").limit(1).execute()
        if response.data and len(response.data) > 0:
            print("\nColumns detected from a record:")
            for key in response.data[0].keys():
                print(f"  - {key}")
            
            # Print the complete record as an example
            print("\nSample record:")
            for key, value in response.data[0].items():
                print(f"  {key}: {value}")
        else:
            print("No records found in the table to infer structure")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    describe_table() 