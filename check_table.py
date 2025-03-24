#!/usr/bin/env python3
import os
import logging
from supabase import create_client

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

# Check if the candidates table exists
try:
    # Try to select from the table
    response = supabase.table("candidates").select("count(*)", count="exact").execute()
    if hasattr(response, 'count'):
        print(f"Table exists. Row count: {response.count}")
    else:
        print(f"Table exists. Response: {response}")
except Exception as e:
    print(f"Error: {str(e)}")
    print("The candidates table might not exist.")

# List all tables
try:
    print("\nTrying to list all tables...")
    response = supabase.rpc(
        fn="execute_safe_query", 
        params={"query_text": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"}
    ).execute()
    print(f"Tables in your database: {response.data}")
except Exception as e:
    print(f"Error listing tables: {str(e)}") 