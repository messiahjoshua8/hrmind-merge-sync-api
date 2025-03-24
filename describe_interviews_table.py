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
    """Describe the interviews table structure."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for table information (this won't tell us column info but will confirm if the table exists)
        print("Checking if the interviews table exists...")
        response = supabase.table("interviews").select("*").limit(1).execute()
        print(f"Table exists, found {len(response.data or [])} records")
        
        # Try to query metadata information
        # This is PostgreSQL system catalog, might require additional permissions
        print("\nAttempting to query column information...")
        try:
            # Try a raw SQL query to get column information
            response = supabase.rpc(
                'pg_describe_table', 
                {'table_name': 'interviews'}
            ).execute()
            
            if response.data:
                print("Column information:")
                for column in response.data:
                    print(f"Column: {column}")
            else:
                print("No column information returned, might need SQL privileges")
        except Exception as e:
            print(f"Error querying column metadata: {str(e)}")
            print("Falling back to listing existing columns in a record...")
            
            # Fallback: Try to get a record and list its keys
            response = supabase.table("interviews").select("*").limit(1).execute()
            if response.data and len(response.data) > 0:
                print("\nColumns detected from a record:")
                for key in response.data[0].keys():
                    print(f"  - {key}")
            else:
                print("No records found in the table to infer structure")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    describe_table() 