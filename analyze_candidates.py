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

# Essential columns that should be kept
ESSENTIAL_COLUMNS = [
    "id", 
    "organization_id", 
    "created_by", 
    "first_name", 
    "last_name", 
    "email_addresses", 
    "phone_numbers", 
    "role", 
    "company", 
    "urls", 
    "skills", 
    "experience", 
    "created_at", 
    "modified_at",
    "previous_role"  # Keep this as user specifically requested
]

def main():
    """Analyze candidates table structure."""
    try:
        # Fetch a sample candidate record
        response = supabase.table("candidates").select("*").limit(1).execute()
        
        if not response.data:
            print("No candidate records found to analyze.")
            return 1
            
        candidate = response.data[0]
        
        print("\n=== CURRENT CANDIDATES TABLE STRUCTURE ===\n")
        print(f"Total fields: {len(candidate.keys())}")
        
        # Separate essential and non-essential fields
        essential_fields = []
        non_essential_fields = []
        
        for field in candidate.keys():
            if field in ESSENTIAL_COLUMNS:
                essential_fields.append(field)
            else:
                non_essential_fields.append(field)
        
        # Print fields categorized
        print("\n=== ESSENTIAL FIELDS ===")
        for field in essential_fields:
            print(f"- {field}: {type(candidate[field]).__name__}")
            
        print("\n=== NON-ESSENTIAL FIELDS (COULD BE REMOVED) ===")
        for field in non_essential_fields:
            print(f"- {field}: {type(candidate[field]).__name__}")
        
        # Generate recommendations
        print("\n=== RECOMMENDATIONS ===")
        print("To clean up the candidates table, you should:")
        print("1. Update your candidates_manager.py script to no longer depend on these fields:")
        for field in non_essential_fields:
            print(f"   - {field}")
            
        print("\n2. Since Supabase RPC functions only allow SELECT queries, you would need to use:")
        print("   - Supabase dashboard to manually remove these columns, or")
        print("   - Use a migration tool or custom script with direct database access")
        
    except Exception as e:
        logger.error(f"Error analyzing candidates table: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 