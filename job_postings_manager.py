#!/usr/bin/env python3
import os
import uuid
import logging
import json
import argparse
from datetime import datetime
import pandas as pd
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
import pathlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration from .env values
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"
MERGE_API_KEY = "E109kd5kXRTmpikl3mMDms0xgAs_p5OOypOOhRDB71hSxFjjyd73uA"

logger.info(f"SUPABASE_URL: {SUPABASE_URL}")
logger.info(f"SUPABASE_KEY: {SUPABASE_KEY[:10]}...")  # Print only first 10 chars for security
    
JOB_POSTINGS_TABLE = "job_postings"
MERGE_BASE_URL = "https://api.merge.dev/api/ats/v1"

class JobPostingsManager:
    """Manager for handling job postings data in Supabase."""
    
    def __init__(self):
        """Initialize the JobPostingsManager with Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
            
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def check_table_exists(self) -> bool:
        """Check if the job_postings table exists."""
        try:
            # Try to select a single row to check if the table exists
            response = self.supabase.table(JOB_POSTINGS_TABLE).select("id").limit(1).execute()
            logger.info(f"{JOB_POSTINGS_TABLE} table exists")
            return True
        except Exception as e:
            logger.error(f"Error checking table: {str(e)}")
            return False
    
    def create_table_schema(self) -> bool:
        """Create the job_postings table if it doesn't exist."""
        if self.check_table_exists():
            logger.info(f"{JOB_POSTINGS_TABLE} table already exists")
            return True
            
        try:
            # Define the table schema in SQL
            schema_query = f"""
            CREATE TABLE IF NOT EXISTS {JOB_POSTINGS_TABLE} (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL,
                user_id UUID NOT NULL,
                created_by UUID NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                requirements TEXT,
                responsibilities TEXT,
                job_posting_url TEXT,
                code TEXT,
                location TEXT,
                remote BOOLEAN,
                status TEXT,
                hiring_manager TEXT,
                created_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE
            );
            """
            
            # Execute the SQL query directly
            # Note: The client role might not have CREATE TABLE permissions
            # You may need to run this query manually in the SQL editor with admin privileges
            response = self.supabase.table("_schemas").select("*").execute()
            logger.info(f"Note: Table creation may require admin privileges")
            logger.info(f"SQL to run manually if needed: {schema_query}")
            
            # Check if table exists after attempted creation
            exists = self.check_table_exists()
            if exists:
                logger.info(f"Created {JOB_POSTINGS_TABLE} table schema")
                return True
            else:
                logger.warning(f"Table {JOB_POSTINGS_TABLE} does not exist after creation attempt")
                logger.warning("You may need to run the CREATE TABLE query manually with admin privileges")
                return False
        except Exception as e:
            logger.error(f"Error creating table schema: {str(e)}")
            return False
    
    def get_merge_token(self, test_mode=False) -> str:
        """Get a Merge token securely using Supabase functions.
        This eliminates the need to handle tokens directly in the client code.
        
        Args:
            test_mode: If True, return a dummy token for testing
        """
        if test_mode:
            # For testing only - in production, always use the Supabase function
            logger.info("TEST MODE: Using dummy token")
            return "test_merge_token"
            
        try:
            # Call the Supabase function that generates/exchanges Merge tokens
            response = self.supabase.rpc(
                "get_merge_token",  # Replace with your actual function name
                {}  # Add any parameters your function needs
            ).execute()
            
            if not response.data:
                raise ValueError("Failed to get Merge token: No data returned")
                
            # The structure will depend on your function's return format
            token = response.data.get("token")
            if not token:
                raise ValueError("Failed to get Merge token: No token in response")
                
            logger.info("Successfully obtained Merge token")
            return token
        except Exception as e:
            logger.error(f"Error getting Merge token: {str(e)}")
            raise

    def fetch_merge_job_postings(self, user_id: str, org_id: str, test_mode=False) -> List[Dict[str, Any]]:
        """Fetch job postings from Merge.dev API using a secure token exchange.
        
        Args:
            user_id: The UUID of the user associated with this data
            org_id: The UUID of the organization associated with this data
            test_mode: If True, use a dummy token for testing
        """
        # For test mode, return sample data without making API calls
        if test_mode:
            logger.info("TEST MODE: Using sample job posting data")
            sample_job_postings = [
                {
                    "id": "job-123", 
                    "name": "Senior Software Engineer",
                    "description": "We're looking for a Senior Software Engineer with expertise in Python and cloud technologies.",
                    "requirements": "5+ years experience with Python, AWS, and distributed systems.",
                    "responsibilities": "Design, develop, and maintain cloud-based applications and APIs.",
                    "job_posting_url": "https://example.com/jobs/senior-engineer",
                    "code": "ENG-123",
                    "location": "San Francisco, CA",
                    "remote": True,
                    "status": "OPEN",
                    "hiring_manager": "Jane Smith",
                    "created_at": "2023-01-15T00:00:00Z",
                    "modified_at": "2023-01-20T00:00:00Z"
                },
                {
                    "id": "job-456",
                    "name": "Product Manager",
                    "description": "We're seeking a Product Manager to lead our new initiative.",
                    "requirements": "3+ years of product management experience in SaaS.",
                    "responsibilities": "Define product vision, strategy, and roadmap.",
                    "job_posting_url": "https://example.com/jobs/product-manager",
                    "code": "PM-456",
                    "location": "New York, NY",
                    "remote": True,
                    "status": "OPEN",
                    "hiring_manager": "John Doe",
                    "created_at": "2023-02-10T00:00:00Z",
                    "modified_at": "2023-02-15T00:00:00Z"
                }
            ]
            
            transformed_job_postings = []
            for job_posting in sample_job_postings:
                job_posting_data = self.transform_merge_job_posting(job_posting, user_id, org_id)
                transformed_job_postings.append(job_posting_data)
                
            logger.info(f"TEST MODE: Generated {len(transformed_job_postings)} sample job postings")
            return transformed_job_postings
            
        # Normal mode - get a secure token from Supabase function and make API calls
        try:
            account_token = self.get_merge_token(test_mode=test_mode)
            
            if not MERGE_API_KEY:
                raise ValueError("Missing Merge API Key. Check your environment variables.")
                
            headers = {
                "Authorization": f"Bearer {MERGE_API_KEY}",
                "X-Account-Token": account_token
            }
            
            job_postings = []
            next_page_url = f"{MERGE_BASE_URL}/job-postings"
            
            while next_page_url:
                try:
                    response = requests.get(next_page_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    for job_posting in data.get("results", []):
                        job_posting_data = self.transform_merge_job_posting(job_posting, user_id, org_id)
                        job_postings.append(job_posting_data)
                    
                    next_page_url = data.get("next")
                except requests.RequestException as e:
                    logger.error(f"Error fetching job postings from Merge API: {str(e)}")
                    break
                    
            logger.info(f"Fetched {len(job_postings)} job postings from Merge API")
            return job_postings
        except Exception as e:
            logger.error(f"Error in fetch_merge_job_postings: {str(e)}")
            raise
    
    def transform_merge_job_posting(self, merge_data: Dict[str, Any], user_id: str, org_id: str) -> Dict[str, Any]:
        """Transform job posting data from Merge API to match our schema."""
        # Generate a UUID from the Merge ID to ensure consistency
        merge_id = merge_data.get("id", "")
        job_posting_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-job-{merge_id}"))
        
        # Extract basic job posting data
        name = merge_data.get("name", "")
        description = merge_data.get("description", "")
        requirements = merge_data.get("requirements", "")
        responsibilities = merge_data.get("responsibilities", "")
        job_posting_url = merge_data.get("job_posting_url", "")
        code = merge_data.get("code", "")
        location = merge_data.get("location", "")
        remote = merge_data.get("remote", False)
        status = merge_data.get("status", "OPEN")
        hiring_manager = merge_data.get("hiring_manager", "")
        
        # Extract dates
        created_at = merge_data.get("created_at")
        updated_at = merge_data.get("modified_at") or merge_data.get("updated_at")
        
        # Transform to match our schema
        return {
            "id": job_posting_id,
            "organization_id": org_id,
            "user_id": user_id,
            "created_by": user_id,  # User who initiated the import
            "name": name,
            "description": description,
            "requirements": requirements,
            "responsibilities": responsibilities,
            "job_posting_url": job_posting_url,
            "code": code,
            "location": location,
            "remote": remote,
            "status": status,
            "hiring_manager": hiring_manager,
            "created_at": created_at,
            "updated_at": updated_at
        }
    
    def upsert_job_postings(self, job_postings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insert or update job postings in Supabase."""
        if not job_postings:
            logger.info("No job postings to upsert")
            return {"inserted": 0, "updated": 0}
            
        inserted = 0
        updated = 0
        
        for job_posting in job_postings:
            try:
                # Check if the job posting already exists by ID
                existing_response = self.supabase.table(JOB_POSTINGS_TABLE) \
                    .select("id") \
                    .eq("id", job_posting["id"]) \
                    .execute()
                
                existing = existing_response.data
                
                if existing and len(existing) > 0:
                    # Update existing record
                    job_posting["updated_at"] = datetime.now().isoformat()
                    
                    # Log the update
                    job_title = job_posting.get("name", "")
                    logger.info(f"Updating job posting {job_posting['id']} ({job_title})")
                    
                    self.supabase.table(JOB_POSTINGS_TABLE) \
                        .update(job_posting) \
                        .eq("id", job_posting["id"]) \
                        .execute()
                    updated += 1
                else:
                    # Insert new record
                    if not job_posting.get("created_at"):
                        job_posting["created_at"] = datetime.now().isoformat()
                    if not job_posting.get("updated_at"):
                        job_posting["updated_at"] = datetime.now().isoformat()
                    
                    # Generate ID if not provided
                    if not job_posting.get("id"):
                        job_posting["id"] = str(uuid.uuid4())
                    
                    # Log the insert
                    job_title = job_posting.get("name", "")
                    logger.info(f"Inserting new job posting {job_posting['id']} ({job_title})")
                    
                    self.supabase.table(JOB_POSTINGS_TABLE) \
                        .insert(job_posting) \
                        .execute()
                    inserted += 1
            except Exception as e:
                logger.error(f"Error upserting job posting {job_posting.get('id')}: {str(e)}")
        
        logger.info(f"Upsert complete. Inserted: {inserted}, Updated: {updated}")
        return {"inserted": inserted, "updated": updated}
    
    def import_from_csv(self, csv_path: str, user_id: str, org_id: str) -> Dict[str, int]:
        """Import job postings from a CSV file."""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Validate required columns
            required_cols = ["name"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in CSV: {', '.join(missing_cols)}")
            
            # Transform data to match our schema
            job_postings = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                name = row_dict.get("name", "")
                
                # Create a deterministic UUID based on name and code
                code = row_dict.get("code", "")
                unique_id = f"{name}-{code}"
                job_posting_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"csv-job-{unique_id}")) if unique_id else str(uuid.uuid4())
                
                # Parse boolean values
                remote = row_dict.get("remote", False)
                if isinstance(remote, str):
                    remote = remote.lower() in ["true", "yes", "1", "y"]
                
                # Transform to match our schema
                job_posting = {
                    "id": row_dict.get("id", job_posting_id),
                    "organization_id": org_id,
                    "user_id": user_id,
                    "created_by": user_id,  # User who initiated the import
                    "name": name,
                    "description": row_dict.get("description", ""),
                    "requirements": row_dict.get("requirements", ""),
                    "responsibilities": row_dict.get("responsibilities", ""),
                    "job_posting_url": row_dict.get("job_posting_url", ""),
                    "code": code,
                    "location": row_dict.get("location", ""),
                    "remote": remote,
                    "status": row_dict.get("status", "OPEN"),
                    "hiring_manager": row_dict.get("hiring_manager", ""),
                    "created_at": row_dict.get("created_at", datetime.now().isoformat()),
                    "updated_at": row_dict.get("updated_at", datetime.now().isoformat())
                }
                
                job_postings.append(job_posting)
            
            # Upsert job postings
            return self.upsert_job_postings(job_postings)
        except Exception as e:
            logger.error(f"Error importing from CSV: {str(e)}")
            raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage job postings data in Supabase")
    parser.add_argument("--check-table", action="store_true", help="Check if the job_postings table exists")
    parser.add_argument("--create-schema", action="store_true", help="Create the job_postings table schema if it doesn't exist")
    parser.add_argument("--merge-import", action="store_true", help="Import job postings from Merge.dev API")
    parser.add_argument("--csv-import", type=str, help="Import job postings from a CSV file")
    parser.add_argument("--user-id", type=str, help="User ID for the import")
    parser.add_argument("--org-id", type=str, help="Organization ID for the import")
    parser.add_argument("--test-mode", action="store_true", help="Use test mode with mock data for development")
    
    args = parser.parse_args()
    
    try:
        manager = JobPostingsManager()
        
        if args.check_table:
            exists = manager.check_table_exists()
            print(f"Job postings table exists: {exists}")
            
        if args.create_schema:
            success = manager.create_table_schema()
            print(f"Job postings table schema created: {success}")
            
        if args.merge_import:
            if not args.user_id or not args.org_id:
                parser.error("--merge-import requires --user-id and --org-id")
                
            job_postings = manager.fetch_merge_job_postings(args.user_id, args.org_id, test_mode=args.test_mode)
            results = manager.upsert_job_postings(job_postings)
            print(f"Merge import complete. Inserted: {results['inserted']}, Updated: {results['updated']}")
            
        if args.csv_import:
            if not args.user_id or not args.org_id:
                parser.error("--csv-import requires --user-id and --org-id")
                
            results = manager.import_from_csv(args.csv_import, args.user_id, args.org_id)
            print(f"CSV import complete. Inserted: {results['inserted']}, Updated: {results['updated']}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main()) 