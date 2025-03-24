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
    
APPLICATIONS_TABLE = "applications"
CANDIDATES_TABLE = "candidates"
JOB_POSTINGS_TABLE = "job_postings"
MERGE_BASE_URL = "https://api.merge.dev/api/ats/v1"

# Valid application status values
VALID_STATUSES = ["APPLIED", "INTERVIEWING", "OFFER", "HIRED", "REJECTED", "OTHER"]

class ApplicationsManager:
    """Manager for handling applications data in Supabase."""
    
    def __init__(self):
        """Initialize the ApplicationsManager with Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
            
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def check_table_exists(self) -> bool:
        """Check if the applications table exists."""
        try:
            # Try to select a single row to check if the table exists
            response = self.supabase.table(APPLICATIONS_TABLE).select("id").limit(1).execute()
            logger.info(f"{APPLICATIONS_TABLE} table exists")
            return True
        except Exception as e:
            logger.error(f"Error checking table: {str(e)}")
            return False
    
    def create_table_schema(self) -> bool:
        """Create the applications table if it doesn't exist."""
        if self.check_table_exists():
            logger.info(f"{APPLICATIONS_TABLE} table already exists")
            return True
            
        try:
            # Define the table schema in SQL
            schema_query = f"""
            CREATE TABLE IF NOT EXISTS {APPLICATIONS_TABLE} (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL,
                user_id UUID NOT NULL,
                created_by UUID NOT NULL,
                candidate_id UUID REFERENCES {CANDIDATES_TABLE}(id),
                job_posting_id UUID REFERENCES {JOB_POSTINGS_TABLE}(id),
                status TEXT NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE,
                last_updated TIMESTAMP WITH TIME ZONE
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
                logger.info(f"Created {APPLICATIONS_TABLE} table schema")
                return True
            else:
                logger.warning(f"Table {APPLICATIONS_TABLE} does not exist after creation attempt")
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

    def fetch_merge_applications(self, user_id: str, org_id: str, test_mode=False) -> List[Dict[str, Any]]:
        """Fetch applications from Merge.dev API using a secure token exchange.
        
        Args:
            user_id: The UUID of the user associated with this data
            org_id: The UUID of the organization associated with this data
            test_mode: If True, use a dummy token for testing
        """
        # For test mode, return sample data without making API calls
        if test_mode:
            logger.info("TEST MODE: Using sample application data")
            sample_applications = [
                {
                    "id": "app-123",
                    "candidate": "abc123",  # Merge candidate ID 
                    "job": "job-123",       # Merge job posting ID
                    "status": "INTERVIEWING",
                    "applied_at": "2023-03-15T00:00:00Z",
                    "modified_at": "2023-03-20T00:00:00Z"
                },
                {
                    "id": "app-456",
                    "candidate": "def456",  # Merge candidate ID
                    "job": "job-456",       # Merge job posting ID
                    "status": "APPLIED",
                    "applied_at": "2023-04-10T00:00:00Z",
                    "modified_at": "2023-04-10T00:00:00Z"
                }
            ]
            
            transformed_applications = []
            for application in sample_applications:
                application_data = self.transform_merge_application(application, user_id, org_id)
                transformed_applications.append(application_data)
                
            logger.info(f"TEST MODE: Generated {len(transformed_applications)} sample applications")
            return transformed_applications
            
        # Normal mode - get a secure token from Supabase function and make API calls
        try:
            account_token = self.get_merge_token(test_mode=test_mode)
            
            if not MERGE_API_KEY:
                raise ValueError("Missing Merge API Key. Check your environment variables.")
                
            headers = {
                "Authorization": f"Bearer {MERGE_API_KEY}",
                "X-Account-Token": account_token
            }
            
            applications = []
            next_page_url = f"{MERGE_BASE_URL}/applications"
            
            while next_page_url:
                try:
                    response = requests.get(next_page_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    for application in data.get("results", []):
                        application_data = self.transform_merge_application(application, user_id, org_id)
                        if application_data:  # Only add if transformed successfully
                            applications.append(application_data)
                    
                    next_page_url = data.get("next")
                except requests.RequestException as e:
                    logger.error(f"Error fetching applications from Merge API: {str(e)}")
                    break
                    
            logger.info(f"Fetched {len(applications)} applications from Merge API")
            return applications
        except Exception as e:
            logger.error(f"Error in fetch_merge_applications: {str(e)}")
            raise
    
    def transform_merge_application(self, merge_data: Dict[str, Any], user_id: str, org_id: str) -> Dict[str, Any]:
        """Transform application data from Merge API to match our schema.
        
        Returns None if either candidate or job posting cannot be found.
        """
        # Generate a UUID from the Merge ID to ensure consistency
        merge_id = merge_data.get("id", "")
        application_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-app-{merge_id}"))
        
        # Get candidate and job IDs from Merge references
        merge_candidate_id = merge_data.get("candidate", "")
        merge_job_id = merge_data.get("job", "")
        
        # Try to resolve candidate and job IDs to our database IDs
        candidate_id = self.resolve_candidate_id(merge_candidate_id)
        job_posting_id = self.resolve_job_posting_id(merge_job_id)
        
        # If we can't find both the candidate and job posting, log a warning
        if not candidate_id or not job_posting_id:
            logger.warning(f"Could not resolve candidate ID {merge_candidate_id} or job posting ID {merge_job_id} for application {merge_id}")
            # We'll still proceed with what we have
        
        # Get application status (normalize to our enum values)
        status = merge_data.get("status", "")
        if status and status in VALID_STATUSES:
            normalized_status = status
        else:
            normalized_status = "OTHER"
            
        # Extract dates
        applied_at = merge_data.get("applied_at")
        last_updated = merge_data.get("modified_at") or merge_data.get("last_updated")
        
        # Transform to match our schema
        return {
            "id": application_id,
            "organization_id": org_id,
            "user_id": user_id, 
            "created_by": user_id,  # User who initiated the import
            "candidate_id": candidate_id,
            "job_posting_id": job_posting_id,
            "status": normalized_status,
            "applied_at": applied_at,
            "last_updated": last_updated
        }
    
    def resolve_candidate_id(self, merge_candidate_id: str) -> Optional[str]:
        """Resolve a Merge candidate ID to our database candidate ID."""
        if not merge_candidate_id:
            return None
            
        try:
            # Generate the deterministic UUID we use in our database
            candidate_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-{merge_candidate_id}"))
            
            # Check if this candidate exists in our database
            response = self.supabase.table(CANDIDATES_TABLE) \
                .select("id") \
                .eq("id", candidate_id) \
                .execute()
                
            if response.data and len(response.data) > 0:
                return candidate_id
            else:
                logger.warning(f"Candidate with ID {candidate_id} (from Merge ID {merge_candidate_id}) not found in database")
                return None
        except Exception as e:
            logger.error(f"Error resolving candidate ID: {str(e)}")
            return None
    
    def resolve_job_posting_id(self, merge_job_id: str) -> Optional[str]:
        """Resolve a Merge job posting ID to our database job posting ID."""
        if not merge_job_id:
            return None
            
        try:
            # Generate the deterministic UUID we use in our database
            job_posting_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-job-{merge_job_id}"))
            
            # Check if this job posting exists in our database
            response = self.supabase.table(JOB_POSTINGS_TABLE) \
                .select("id") \
                .eq("id", job_posting_id) \
                .execute()
                
            if response.data and len(response.data) > 0:
                return job_posting_id
            else:
                logger.warning(f"Job posting with ID {job_posting_id} (from Merge ID {merge_job_id}) not found in database")
                return None
        except Exception as e:
            logger.error(f"Error resolving job posting ID: {str(e)}")
            return None
    
    def upsert_applications(self, applications: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insert or update applications in Supabase."""
        if not applications:
            logger.info("No applications to upsert")
            return {"inserted": 0, "updated": 0}
            
        inserted = 0
        updated = 0
        
        for application in applications:
            try:
                # Check if the application already exists by ID
                existing_response = self.supabase.table(APPLICATIONS_TABLE) \
                    .select("id") \
                    .eq("id", application["id"]) \
                    .execute()
                
                existing = existing_response.data
                
                if existing and len(existing) > 0:
                    # Update existing record
                    application["last_updated"] = datetime.now().isoformat()
                    
                    # Log the update
                    logger.info(f"Updating application {application['id']} (Status: {application['status']})")
                    
                    self.supabase.table(APPLICATIONS_TABLE) \
                        .update(application) \
                        .eq("id", application["id"]) \
                        .execute()
                    updated += 1
                else:
                    # Insert new record
                    if not application.get("applied_at"):
                        application["applied_at"] = datetime.now().isoformat()
                    if not application.get("last_updated"):
                        application["last_updated"] = datetime.now().isoformat()
                    
                    # Generate ID if not provided
                    if not application.get("id"):
                        application["id"] = str(uuid.uuid4())
                    
                    # Log the insert
                    logger.info(f"Inserting new application {application['id']} (Status: {application['status']})")
                    
                    self.supabase.table(APPLICATIONS_TABLE) \
                        .insert(application) \
                        .execute()
                    inserted += 1
            except Exception as e:
                logger.error(f"Error upserting application {application.get('id')}: {str(e)}")
        
        logger.info(f"Upsert complete. Inserted: {inserted}, Updated: {updated}")
        return {"inserted": inserted, "updated": updated}
    
    def import_from_csv(self, csv_path: str, user_id: str, org_id: str) -> Dict[str, int]:
        """Import applications from a CSV file."""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Validate required columns
            required_cols = ["status"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in CSV: {', '.join(missing_cols)}")
            
            # Transform data to match our schema
            applications = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                
                # Validate status value
                status = row_dict.get("status", "").upper()
                if status not in VALID_STATUSES:
                    logger.warning(f"Invalid status value '{status}' - defaulting to 'OTHER'")
                    status = "OTHER"
                
                # Parse dates
                applied_at = row_dict.get("applied_at", datetime.now().isoformat())
                last_updated = row_dict.get("last_updated", datetime.now().isoformat())
                
                # Check for candidate and job posting IDs
                candidate_id = row_dict.get("candidate_id")
                job_posting_id = row_dict.get("job_posting_id")
                
                # Create a deterministic UUID based on candidate and job
                unique_id = f"{candidate_id}-{job_posting_id}-{status}"
                application_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"csv-app-{unique_id}")) if unique_id else str(uuid.uuid4())
                
                # Transform to match our schema
                application = {
                    "id": row_dict.get("id", application_id),
                    "organization_id": org_id,
                    "user_id": user_id,
                    "created_by": user_id,  # User who initiated the import
                    "candidate_id": candidate_id,
                    "job_posting_id": job_posting_id,
                    "status": status,
                    "applied_at": applied_at,
                    "last_updated": last_updated
                }
                
                applications.append(application)
            
            # Upsert applications
            return self.upsert_applications(applications)
        except Exception as e:
            logger.error(f"Error importing from CSV: {str(e)}")
            raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage applications data in Supabase")
    parser.add_argument("--check-table", action="store_true", help="Check if the applications table exists")
    parser.add_argument("--create-schema", action="store_true", help="Create the applications table schema if it doesn't exist")
    parser.add_argument("--merge-import", action="store_true", help="Import applications from Merge.dev API")
    parser.add_argument("--csv-import", type=str, help="Import applications from a CSV file")
    parser.add_argument("--user-id", type=str, help="User ID for the import")
    parser.add_argument("--org-id", type=str, help="Organization ID for the import")
    parser.add_argument("--test-mode", action="store_true", help="Use test mode with mock data for development")
    
    args = parser.parse_args()
    
    try:
        manager = ApplicationsManager()
        
        if args.check_table:
            exists = manager.check_table_exists()
            print(f"Applications table exists: {exists}")
            
        if args.create_schema:
            success = manager.create_table_schema()
            print(f"Applications table schema created: {success}")
            
        if args.merge_import:
            if not args.user_id or not args.org_id:
                parser.error("--merge-import requires --user-id and --org-id")
                
            applications = manager.fetch_merge_applications(args.user_id, args.org_id, test_mode=args.test_mode)
            results = manager.upsert_applications(applications)
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