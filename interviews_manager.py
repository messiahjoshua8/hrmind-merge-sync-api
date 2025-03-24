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
    
INTERVIEWS_TABLE = "interviews"
APPLICATIONS_TABLE = "applications"
MERGE_BASE_URL = "https://api.merge.dev/api/ats/v1"

# Valid interview type values
VALID_INTERVIEW_TYPES = ["PHONE", "VIRTUAL", "ONSITE", "TECHNICAL", "BEHAVIORAL", "OTHER"]

# Valid result values
VALID_RESULTS = ["PASSED", "FAILED", "PENDING", "CANCELED", "NO_SHOW", "OTHER"]

class InterviewsManager:
    """Manager for handling interviews data in Supabase."""
    
    def __init__(self):
        """Initialize the InterviewsManager with Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
            
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def check_table_exists(self) -> bool:
        """Check if the interviews table exists."""
        try:
            # Try to select a single row to check if the table exists
            response = self.supabase.table(INTERVIEWS_TABLE).select("id").limit(1).execute()
            logger.info(f"{INTERVIEWS_TABLE} table exists")
            return True
        except Exception as e:
            logger.error(f"Error checking table: {str(e)}")
            return False
    
    def create_table_schema(self) -> bool:
        """Create the interviews table if it doesn't exist."""
        if self.check_table_exists():
            logger.info(f"{INTERVIEWS_TABLE} table already exists")
            return True
            
        try:
            # Define the table schema in SQL
            schema_query = f"""
            CREATE TABLE IF NOT EXISTS {INTERVIEWS_TABLE} (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL,
                created_by UUID NOT NULL,
                candidate_id UUID REFERENCES candidates(id),
                job_id UUID REFERENCES job_postings(id),
                date TIMESTAMP WITH TIME ZONE,
                time TEXT,
                status TEXT,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                calendar_event_id TEXT,
                deleted_at TIMESTAMP WITH TIME ZONE,
                deleted_by UUID,
                restore_until TIMESTAMP WITH TIME ZONE
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
                logger.info(f"Created {INTERVIEWS_TABLE} table schema")
                return True
            else:
                logger.warning(f"Table {INTERVIEWS_TABLE} does not exist after creation attempt")
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

    def fetch_merge_interviews(self, user_id: str, org_id: str, test_mode=False) -> List[Dict[str, Any]]:
        """Fetch interviews from Merge.dev API using a secure token exchange.
        
        Args:
            user_id: The UUID of the user associated with this data
            org_id: The UUID of the organization associated with this data
            test_mode: If True, use a dummy token for testing
        """
        # For test mode, return sample data without making API calls
        if test_mode:
            logger.info("TEST MODE: Using sample interview data")
            sample_interviews = [
                {
                    "id": "interview-123",
                    "application": "app-123",  # Merge application ID 
                    "interviewer": "John Smith",
                    "organizer": "HR Department",
                    "status": "SCHEDULED",
                    "start_time": "2023-06-15T10:00:00Z",
                    "end_time": "2023-06-15T11:00:00Z",
                    "location": "Virtual - Zoom",
                    "interview_type": "VIRTUAL",
                    "result": "PENDING",
                    "remote_created_at": "2023-06-01T10:00:00Z", 
                    "remote_updated_at": "2023-06-01T10:00:00Z"
                },
                {
                    "id": "interview-456",
                    "application": "app-456",  # Merge application ID
                    "interviewer": "Sarah Johnson",
                    "organizer": "Engineering Team",
                    "status": "COMPLETED",
                    "start_time": "2023-05-20T13:00:00Z",
                    "end_time": "2023-05-20T14:30:00Z",
                    "location": "Onsite - Conference Room A",
                    "interview_type": "TECHNICAL",
                    "result": "PASSED",
                    "feedback": "Great technical skills and problem-solving abilities.",
                    "remote_created_at": "2023-05-15T09:00:00Z",
                    "remote_updated_at": "2023-05-20T15:00:00Z"
                }
            ]
            
            transformed_interviews = []
            for interview in sample_interviews:
                interview_data = self.transform_merge_interview(interview, user_id, org_id)
                transformed_interviews.append(interview_data)
                
            logger.info(f"TEST MODE: Generated {len(transformed_interviews)} sample interviews")
            return transformed_interviews
            
        # Normal mode - get a secure token from Supabase function and make API calls
        try:
            account_token = self.get_merge_token(test_mode=test_mode)
            
            if not MERGE_API_KEY:
                raise ValueError("Missing Merge API Key. Check your environment variables.")
                
            headers = {
                "Authorization": f"Bearer {MERGE_API_KEY}",
                "X-Account-Token": account_token
            }
            
            interviews = []
            next_page_url = f"{MERGE_BASE_URL}/interviews"
            
            while next_page_url:
                try:
                    response = requests.get(next_page_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    for interview in data.get("results", []):
                        interview_data = self.transform_merge_interview(interview, user_id, org_id)
                        if interview_data:  # Only add if transformed successfully
                            interviews.append(interview_data)
                    
                    next_page_url = data.get("next")
                except requests.RequestException as e:
                    logger.error(f"Error fetching interviews from Merge API: {str(e)}")
                    break
                    
            logger.info(f"Fetched {len(interviews)} interviews from Merge API")
            return interviews
        except Exception as e:
            logger.error(f"Error in fetch_merge_interviews: {str(e)}")
            raise
    
    def transform_merge_interview(self, merge_data: Dict[str, Any], user_id: str, org_id: str) -> Dict[str, Any]:
        """Transform interview data from Merge API to match our schema."""
        # Generate a UUID from the Merge ID to ensure consistency
        merge_id = merge_data.get("id", "")
        interview_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-interview-{merge_id}"))
        
        # Get application ID from Merge reference
        merge_application_id = merge_data.get("application", "")
        
        # Try to resolve application info to get candidate and job IDs
        application_info = self.resolve_application_info(merge_application_id)
        candidate_id = application_info.get("candidate_id") if application_info else None
        job_id = application_info.get("job_id") if application_info else None
        
        # If we can't find the application, log a warning
        if not candidate_id or not job_id:
            logger.warning(f"Could not resolve application info for {merge_application_id}")
            # We'll still proceed with what we have
        
        # Get interview status based on result
        result = merge_data.get("result", "")
        if result and result in VALID_RESULTS:
            status = result
        else:
            # If status is SCHEDULED, set as PENDING
            if merge_data.get("status") == "SCHEDULED":
                status = "PENDING"
            else:
                status = "OTHER"
        
        # Extract dates and time
        # Use start_time as date and parse hour/minute for time
        interview_datetime = merge_data.get("start_time")
        date = interview_datetime  # Store the full datetime in the date field
        
        # For time, extract the time portion or store a default format
        time = None
        if interview_datetime:
            try:
                dt = datetime.fromisoformat(interview_datetime.replace('Z', '+00:00'))
                time = dt.strftime("%H:%M")  # Format as HH:MM 
            except Exception as e:
                logger.warning(f"Error parsing interview datetime: {str(e)}")
        
        # Extract notes/feedback
        notes = merge_data.get("feedback", "")
        if merge_data.get("location"):
            notes += f"\nLocation: {merge_data.get('location')}"
        
        # Extract interviewer info as notes if available
        interviewer = merge_data.get("interviewer", "")
        if interviewer:
            notes += f"\nInterviewer: {interviewer}"
        
        # Get interview type and include in notes
        interview_type = merge_data.get("interview_type", "")
        if interview_type:
            notes += f"\nType: {interview_type}"
        
        # Add created_at from remote_created_at
        created_at = merge_data.get("remote_created_at") or datetime.now().isoformat()
        
        # Transform to match our schema
        # Omit job_id if not found to prevent foreign key constraint errors
        interview_data = {
            "id": interview_id,
            "organization_id": org_id,
            "created_by": user_id,  # User who initiated the import
            "date": date,
            "time": time,
            "status": status,
            "notes": notes,
            "created_at": created_at,
            "calendar_event_id": merge_data.get("id", "")  # Use Merge ID as calendar event ID
        }
        
        # Only add candidate_id and job_id if they exist to avoid FK constraint errors
        if candidate_id:
            interview_data["candidate_id"] = candidate_id
        
        return interview_data
    
    def resolve_application_info(self, merge_application_id: str) -> Optional[Dict[str, Any]]:
        """Resolve a Merge application ID to get candidate_id and job_id."""
        if not merge_application_id:
            return None
            
        try:
            # Generate the deterministic UUID we use in our database
            application_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-app-{merge_application_id}"))
            
            # Check if this application exists in our database
            response = self.supabase.table(APPLICATIONS_TABLE) \
                .select("candidate_id,job_posting_id") \
                .eq("id", application_id) \
                .execute()
                
            if response.data and len(response.data) > 0:
                app = response.data[0]
                
                # Get job ID from job_postings table and map it to the jobs table if needed
                job_posting_id = app.get("job_posting_id")
                job_id = None
                
                if job_posting_id:
                    # Try to find corresponding job ID in the jobs table
                    try:
                        # This is a guess - we don't know the exact relationship between job_postings and jobs
                        # You might need to adjust this query based on your actual schema
                        job_response = self.supabase.table("jobs") \
                            .select("id") \
                            .eq("id", job_posting_id) \
                            .execute()
                            
                        if job_response.data and len(job_response.data) > 0:
                            job_id = job_response.data[0]["id"]
                        else:
                            logger.warning(f"Job posting with ID {job_posting_id} not found in jobs table")
                    except Exception as e:
                        logger.error(f"Error finding job ID: {str(e)}")
                
                return {
                    "candidate_id": app.get("candidate_id"),
                    "job_id": job_id
                }
            else:
                logger.warning(f"Application with ID {application_id} (from Merge ID {merge_application_id}) not found in database")
                return None
        except Exception as e:
            logger.error(f"Error resolving application info: {str(e)}")
            return None
    
    def upsert_interviews(self, interviews: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insert or update interviews in Supabase."""
        if not interviews:
            logger.info("No interviews to upsert")
            return {"inserted": 0, "updated": 0}
            
        inserted = 0
        updated = 0
        
        for interview in interviews:
            try:
                # Check if the interview already exists by ID
                existing_response = self.supabase.table(INTERVIEWS_TABLE) \
                    .select("id") \
                    .eq("id", interview["id"]) \
                    .execute()
                
                existing = existing_response.data
                
                if existing and len(existing) > 0:
                    # Update existing record
                    
                    # Log the update
                    logger.info(f"Updating interview {interview['id']} (Status: {interview['status']})")
                    
                    self.supabase.table(INTERVIEWS_TABLE) \
                        .update(interview) \
                        .eq("id", interview["id"]) \
                        .execute()
                    updated += 1
                else:
                    # Insert new record
                    if not interview.get("date"):
                        interview["date"] = datetime.now().isoformat()
                    if not interview.get("created_at"):
                        interview["created_at"] = datetime.now().isoformat()
                    
                    # Generate ID if not provided
                    if not interview.get("id"):
                        interview["id"] = str(uuid.uuid4())
                    
                    # Log the insert
                    logger.info(f"Inserting new interview {interview['id']} (Status: {interview['status']})")
                    
                    self.supabase.table(INTERVIEWS_TABLE) \
                        .insert(interview) \
                        .execute()
                    inserted += 1
            except Exception as e:
                logger.error(f"Error upserting interview {interview.get('id')}: {str(e)}")
        
        logger.info(f"Upsert complete. Inserted: {inserted}, Updated: {updated}")
        return {"inserted": inserted, "updated": updated}
    
    def import_from_csv(self, csv_path: str, user_id: str, org_id: str) -> Dict[str, int]:
        """Import interviews from a CSV file."""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Transform data to match our schema
            interviews = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                
                # Get required fields from CSV
                application_id = row_dict.get("application_id")
                
                # Get job_id directly from CSV if available
                job_id = row_dict.get("job_id")
                
                # Try to resolve candidate_id from application if available
                candidate_id = None
                
                # Check if the application exists in our database
                if application_id:
                    try:
                        response = self.supabase.table(APPLICATIONS_TABLE) \
                            .select("candidate_id") \
                            .eq("id", application_id) \
                            .execute()
                            
                        if response.data and len(response.data) > 0:
                            app = response.data[0]
                            candidate_id = app.get("candidate_id")
                    except Exception as e:
                        logger.warning(f"Error resolving application {application_id}: {str(e)}")
                
                # Get interview date and time
                interview_datetime = row_dict.get("interview_date")
                date = interview_datetime  # Store the full datetime in the date field
                
                # For time, extract the time portion or leave as None
                time = None
                if interview_datetime:
                    try:
                        dt = datetime.fromisoformat(interview_datetime.replace('Z', '+00:00'))
                        time = dt.strftime("%H:%M")  # Format as HH:MM
                    except Exception as e:
                        logger.warning(f"Error parsing interview datetime: {str(e)}")
                
                # Get interviewer and add to notes
                interviewer = row_dict.get("interviewer", "")
                
                # Get interview type and result
                interview_type = row_dict.get("interview_type", "").upper()
                result = row_dict.get("result", "").upper()
                
                # Compile notes
                notes = row_dict.get("feedback", "")
                if interviewer:
                    notes += f"\nInterviewer: {interviewer}"
                if interview_type:
                    notes += f"\nType: {interview_type}"
                
                # Create a deterministic UUID based on application and interview date
                unique_id = f"{application_id}-{interview_datetime}-{interview_type}"
                interview_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"csv-interview-{unique_id}")) if unique_id else str(uuid.uuid4())
                
                # Transform to match our schema - include job_id from CSV
                interview_data = {
                    "id": row_dict.get("id", interview_id),
                    "organization_id": org_id,
                    "created_by": user_id,  # User who initiated the import
                    "job_id": job_id,  # Use job_id directly from CSV
                    "date": date,
                    "time": time,
                    "status": result,  # Use result as status
                    "notes": notes,
                    "created_at": row_dict.get("remote_created_at", datetime.now().isoformat())
                }
                
                # Only add candidate_id if it exists to avoid FK constraint errors
                if candidate_id:
                    interview_data["candidate_id"] = candidate_id
                
                interviews.append(interview_data)
            
            # Upsert interviews
            return self.upsert_interviews(interviews)
        except Exception as e:
            logger.error(f"Error importing from CSV: {str(e)}")
            raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage interviews data in Supabase")
    parser.add_argument("--check-table", action="store_true", help="Check if the interviews table exists")
    parser.add_argument("--create-schema", action="store_true", help="Create the interviews table schema if it doesn't exist")
    parser.add_argument("--merge-import", action="store_true", help="Import interviews from Merge.dev API")
    parser.add_argument("--csv-import", type=str, help="Import interviews from a CSV file")
    parser.add_argument("--user-id", type=str, help="User ID for the import")
    parser.add_argument("--org-id", type=str, help="Organization ID for the import")
    parser.add_argument("--test-mode", action="store_true", help="Use test mode with mock data for development")
    
    args = parser.parse_args()
    
    try:
        manager = InterviewsManager()
        
        if args.check_table:
            exists = manager.check_table_exists()
            print(f"Interviews table exists: {exists}")
            
        if args.create_schema:
            success = manager.create_table_schema()
            print(f"Interviews table schema created: {success}")
            
        if args.merge_import:
            if not args.user_id or not args.org_id:
                parser.error("--merge-import requires --user-id and --org-id")
                
            interviews = manager.fetch_merge_interviews(args.user_id, args.org_id, test_mode=args.test_mode)
            results = manager.upsert_interviews(interviews)
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