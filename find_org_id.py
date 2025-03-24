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

# Look for existing candidates with organization IDs
try:
    print("Looking for existing candidates with valid organization IDs...")
    response = supabase.table("candidates").select("organization_id").not_.is_("organization_id", "null").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        org_id = response.data[0]["organization_id"]
        print(f"Found valid organization ID from candidates table: {org_id}")
        
        # Also get a valid user ID
        user_response = supabase.table("candidates").select("created_by").not_.is_("created_by", "null").limit(1).execute()
        if user_response.data and len(user_response.data) > 0:
            user_id = user_response.data[0]["created_by"]
            print(f"Found valid user ID from candidates table: {user_id}")
            
            print("\nUse these IDs for your import:")
            print(f"python3 candidates_manager.py --csv-import sample_candidates_updated.csv --user-id {user_id} --org-id {org_id}")
    else:
        print("No candidates with valid organization IDs found.")
        
        # Try to look up organizations directly
        try:
            print("\nLooking for organization IDs in the organizations table...")
            response = supabase.table("organizations").select("id").limit(1).execute()
            
            if response.data and len(response.data) > 0:
                org_id = response.data[0]["id"]
                print(f"Found valid organization ID from organizations table: {org_id}")
                
                # Get a valid user ID
                user_response = supabase.table("candidates").select("created_by").not_.is_("created_by", "null").limit(1).execute()
                if user_response.data and len(user_response.data) > 0:
                    user_id = user_response.data[0]["created_by"]
                    print(f"Found valid user ID from candidates table: {user_id}")
                    
                    print("\nUse these IDs for your import:")
                    print(f"python3 candidates_manager.py --csv-import sample_candidates_updated.csv --user-id {user_id} --org-id {org_id}")
            else:
                print("No organizations found.")
        except Exception as e:
            print(f"Error looking up organizations: {str(e)}")
        
except Exception as e:
    print(f"Error looking up candidates: {str(e)}") 