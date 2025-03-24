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

# Get columns of the candidates table
try:
    print("Checking columns of the candidates table...")
    query = """
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'candidates' 
    AND table_schema = 'public'
    ORDER BY ordinal_position
    """
    
    response = supabase.rpc(
        fn="execute_safe_query", 
        params={"query_text": query}
    ).execute()
    
    print("\nColumns in the candidates table:")
    for column in response.data:
        print(f"- {column['column_name']} ({column['data_type']}, nullable: {column['is_nullable']})")
        
except Exception as e:
    print(f"Error getting columns: {str(e)}")

# Check if there are any rows in the table
try:
    print("\nChecking if there are any rows in the candidates table...")
    query = "SELECT COUNT(*) FROM candidates"
    response = supabase.rpc(
        fn="execute_safe_query", 
        params={"query_text": query}
    ).execute()
    
    row_count = response.data[0]['count']
    print(f"Row count: {row_count}")
except Exception as e:
    print(f"Error counting rows: {str(e)}") 