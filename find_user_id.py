#!/usr/bin/env python3
import os
import logging
from supabase import create_client
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration from .env values
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# First try to look up existing candidates
try:
    print("Looking for existing candidates with valid user IDs...")
    response = supabase.table("candidates").select("created_by").not_.is_("created_by", "null").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        user_id = response.data[0]["created_by"]
        print(f"Found valid user ID from candidates table: {user_id}")
        print("\nUse this user ID for your import:")
        print(f"python3 candidates_manager.py --csv-import sample_candidates_updated.csv --user-id {user_id} --org-id 123e4567-e89b-12d3-a456-426614174001")
    else:
        print("No candidates with valid user IDs found.")
        
        # Try to look up users directly
        try:
            print("\nLooking for user IDs in the users table...")
            response = supabase.table("auth.users").select("id").limit(1).execute()
            
            if response.data and len(response.data) > 0:
                user_id = response.data[0]["id"]
                print(f"Found valid user ID from users table: {user_id}")
                print("\nUse this user ID for your import:")
                print(f"python3 candidates_manager.py --csv-import sample_candidates_updated.csv --user-id {user_id} --org-id 123e4567-e89b-12d3-a456-426614174001")
            else:
                # Try looking at all tables with user IDs
                print("\nTrying to find tables that reference users...")
                query = "SELECT * FROM information_schema.columns WHERE column_name = 'user_id' OR column_name = 'created_by'"
                response = supabase.rpc(
                    fn="execute_safe_query", 
                    params={"query_text": query}
                ).execute()
                print("Tables with user_id or created_by columns:")
                print(json.dumps(response.data, indent=2))
        except Exception as e:
            print(f"Error looking up users: {str(e)}")

except Exception as e:
    print(f"Error looking up candidates: {str(e)}") 