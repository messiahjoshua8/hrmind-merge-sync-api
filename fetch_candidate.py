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

# Fetch a single candidate to examine the structure
try:
    print("Fetching a sample candidate record...")
    response = supabase.table("candidates").select("*").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        print("\nCandidate record structure:")
        # Pretty print the first record to see its structure
        print(json.dumps(response.data[0], indent=2))
        
        # Show the column names
        print("\nColumn names:")
        print(list(response.data[0].keys()))
    else:
        print("No candidates found in the table.")
        
except Exception as e:
    print(f"Error fetching sample candidate: {str(e)}") 