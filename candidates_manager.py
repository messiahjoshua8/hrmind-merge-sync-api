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
    
CANDIDATES_TABLE = "candidates"
MERGE_BASE_URL = "https://api.merge.dev/api/ats/v1"

class CandidatesManager:
    """Manager for handling candidates data in Supabase."""
    
    def __init__(self):
        """Initialize the CandidatesManager with Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
            
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def check_table_exists(self) -> bool:
        """Check if the candidates table exists."""
        try:
            # Try to select a single row to check if the table exists
            response = self.supabase.table(CANDIDATES_TABLE).select("id").limit(1).execute()
            logger.info("Candidates table exists")
            return True
        except Exception as e:
            logger.error(f"Error checking table: {str(e)}")
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

    def fetch_merge_candidates(self, user_id: str, org_id: str, test_mode=False) -> List[Dict[str, Any]]:
        """Fetch candidates from Merge.dev API using a secure token exchange.
        
        Args:
            user_id: The UUID of the user associated with this data
            org_id: The UUID of the organization associated with this data
            test_mode: If True, use a dummy token for testing
        """
        # For test mode, return sample data without making API calls
        if test_mode:
            logger.info("TEST MODE: Using sample candidate data")
            sample_candidates = [
                {
                    "remote_id": "test123",
                    "first_name": "John",
                    "last_name": "Test",
                    "emails": [{"type": "primary", "value": "john.test@example.com"}],
                    "phone_numbers": [{"type": "primary", "value": "123-456-7890"}],
                    "current_title": "Software Engineer",
                    "current_company": "Test Company",
                    "resume_url": "https://example.com/resume.pdf",
                    "skills": ["Python", "JavaScript", "SQL"],
                    "years_experience": 5,
                    "past_titles": ["Junior Developer", "Developer"]
                },
                {
                    "remote_id": "test456",
                    "first_name": "Jane",
                    "last_name": "Sample",
                    "emails": [{"type": "primary", "value": "jane.sample@example.com"}],
                    "phone_numbers": [{"type": "primary", "value": "234-567-8901"}],
                    "current_title": "Product Manager",
                    "current_company": "Sample Inc",
                    "resume_url": "https://example.com/resume2.pdf",
                    "skills": ["Product Management", "Agile", "UX"],
                    "years_experience": 7,
                    "past_titles": ["Associate PM", "Business Analyst"]
                }
            ]
            
            transformed_candidates = []
            for candidate in sample_candidates:
                candidate_data = self.transform_merge_candidate(candidate, user_id, org_id)
                transformed_candidates.append(candidate_data)
                
            logger.info(f"TEST MODE: Generated {len(transformed_candidates)} sample candidates")
            return transformed_candidates
            
        # Normal mode - get a secure token from Supabase function and make API calls
        try:
            account_token = self.get_merge_token(test_mode=test_mode)
            
            if not MERGE_API_KEY:
                raise ValueError("Missing Merge API Key. Check your environment variables.")
                
            headers = {
                "Authorization": f"Bearer {MERGE_API_KEY}",
                "X-Account-Token": account_token
            }
            
            candidates = []
            next_page_url = f"{MERGE_BASE_URL}/candidates"
            
            while next_page_url:
                try:
                    response = requests.get(next_page_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    for candidate in data.get("results", []):
                        candidate_data = self.transform_merge_candidate(candidate, user_id, org_id)
                        candidates.append(candidate_data)
                    
                    next_page_url = data.get("next")
                except requests.RequestException as e:
                    logger.error(f"Error fetching candidates from Merge API: {str(e)}")
                    break
                    
            logger.info(f"Fetched {len(candidates)} candidates from Merge API")
            return candidates
        except Exception as e:
            logger.error(f"Error in fetch_merge_candidates: {str(e)}")
            raise
    
    def transform_merge_candidate(self, merge_data: Dict[str, Any], user_id: str, org_id: str) -> Dict[str, Any]:
        """Transform candidate data from Merge API to match our schema."""
        # Generate a UUID from the Merge remote ID to ensure consistency
        remote_id = merge_data.get("remote_id", "")
        candidate_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"merge-{remote_id}"))
        
        # Extract name components
        first_name = merge_data.get("first_name", "")
        last_name = merge_data.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # Extract emails and get primary one
        emails = merge_data.get("emails", [])
        email = next((e.get("value", "") for e in emails if e.get("type", "").lower() == "primary"), "")
        if not email and emails:
            email = emails[0].get("value", "")
        
        # Current role and company
        current_title = merge_data.get("current_title", "")
        current_company = merge_data.get("current_company", "")
        
        # Resume URL
        resume_url = merge_data.get("resume_url", "")
        
        # Get past titles for previous_role
        past_titles = merge_data.get("past_titles", [])
        previous_role = past_titles[0] if past_titles and len(past_titles) > 0 else "Previous Position"
        
        # Skills as an array
        skills = merge_data.get("skills", [])
        
        # Years of experience
        years_experience = merge_data.get("years_experience")
        
        # Default image URL (required by current schema)
        default_image_url = "https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTJ8fHByb2ZpbGUlMjBpbWFnZXxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60"
        
        # Transform to match known schema fields only
        return {
            "id": candidate_id,
            "organization_id": org_id,
            "created_by": user_id,
            "name": full_name,
            "role": current_title,
            "skills": skills,
            "experience": years_experience,
            "previous_role": previous_role,
            "status": "available",
            "image_url": default_image_url,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat()
        }
    
    def upsert_candidates(self, candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insert or update candidates in Supabase."""
        if not candidates:
            logger.info("No candidates to upsert")
            return {"inserted": 0, "updated": 0}
            
        inserted = 0
        updated = 0
        
        for candidate in candidates:
            try:
                # Check if the candidate already exists by ID or name
                existing = None
                
                if candidate.get("id"):
                    # Try to find by ID first
                    existing_response = self.supabase.table(CANDIDATES_TABLE) \
                        .select("id") \
                        .eq("id", candidate["id"]) \
                        .execute()
                    
                    if existing_response.data:
                        existing = existing_response.data
                
                # If we still haven't found a match, try by name as a last resort
                if not existing and candidate.get("name"):
                    existing_response = self.supabase.table(CANDIDATES_TABLE) \
                        .select("id") \
                        .eq("name", candidate["name"]) \
                        .execute()
                    
                    if existing_response.data:
                        existing = existing_response.data
                        # Update the ID to match the existing record
                        if existing and len(existing) > 0:
                            candidate["id"] = existing[0]["id"]
                
                if existing and len(existing) > 0:
                    # Update existing record
                    candidate["modified_at"] = datetime.now().isoformat()
                    
                    # Remove fields that don't exist in the schema or might cause problems
                    if "updated_at" in candidate:
                        del candidate["updated_at"]
                    
                    # Log the update
                    candidate_name = candidate.get("name", "")
                    logger.info(f"Updating candidate {candidate['id']} ({candidate_name})")
                    
                    self.supabase.table(CANDIDATES_TABLE) \
                        .update(candidate) \
                        .eq("id", candidate["id"]) \
                        .execute()
                    updated += 1
                else:
                    # Insert new record
                    candidate["created_at"] = datetime.now().isoformat()
                    candidate["modified_at"] = datetime.now().isoformat()
                    
                    # Remove fields that don't exist in the schema or might cause problems
                    if "updated_at" in candidate:
                        del candidate["updated_at"]
                    
                    # Generate ID if not provided
                    if not candidate.get("id"):
                        candidate["id"] = str(uuid.uuid4())
                    
                    # Log the insert
                    candidate_name = candidate.get("name", "")
                    logger.info(f"Inserting new candidate {candidate['id']} ({candidate_name})")
                    
                    self.supabase.table(CANDIDATES_TABLE) \
                        .insert(candidate) \
                        .execute()
                    inserted += 1
            except Exception as e:
                logger.error(f"Error upserting candidate {candidate.get('id')}: {str(e)}")
        
        logger.info(f"Upsert complete. Inserted: {inserted}, Updated: {updated}")
        return {"inserted": inserted, "updated": updated}
    
    def import_from_csv(self, csv_path: str, user_id: str, org_id: str) -> Dict[str, int]:
        """Import candidates from a CSV file."""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Validate required columns
            required_cols = ["first_name", "last_name"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in CSV: {', '.join(missing_cols)}")
            
            # Default image URL (required by current schema)
            default_image_url = "https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTJ8fHByb2ZpbGUlMjBpbWFnZXxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60"
            
            # Transform data to match our schema
            candidates = []
            for _, row in df.iterrows():
                # Create a deterministic UUID based on email or name
                row_dict = row.to_dict()
                first_name = row_dict.get("first_name", "")
                last_name = row_dict.get("last_name", "")
                full_name = f"{first_name} {last_name}".strip()
                
                email = row_dict.get("email", "")
                unique_id = email if email else full_name
                candidate_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"csv-{unique_id}")) if unique_id else str(uuid.uuid4())
                
                # Parse skills
                skills_text = row_dict.get("skills", "")
                skills = []
                if isinstance(skills_text, str) and skills_text:
                    skills = [skill.strip() for skill in skills_text.split(",")]
                
                # Parse past_titles for previous_role
                past_titles_text = row_dict.get("past_titles", "")
                past_titles = []
                if isinstance(past_titles_text, str) and past_titles_text:
                    past_titles = [title.strip() for title in past_titles_text.split(",")]
                
                previous_role = past_titles[0] if past_titles else "Previous Position"
                
                # Current role and company
                current_title = row_dict.get("current_title", "")
                
                # Transform to match known schema fields only
                candidate = {
                    "id": row_dict.get("id", candidate_id),
                    "organization_id": org_id,
                    "created_by": user_id,
                    "name": full_name,
                    "role": current_title,
                    "skills": skills,
                    "experience": row_dict.get("years_experience"),
                    "previous_role": previous_role,
                    "status": "available",
                    "image_url": default_image_url,
                    "created_at": datetime.now().isoformat(),
                    "modified_at": datetime.now().isoformat()
                }
                
                candidates.append(candidate)
            
            # Upsert candidates
            return self.upsert_candidates(candidates)
        except Exception as e:
            logger.error(f"Error importing from CSV: {str(e)}")
            raise

    def validate_merge_token(self, account_token: str) -> bool:
        """Validate a Merge account token by making a test API call."""
        if not MERGE_API_KEY:
            logger.error("Missing Merge API Key. Please set MERGE_API_KEY in your environment variables.")
            return False
            
        headers = {
            "Authorization": f"Bearer {MERGE_API_KEY}",
            "X-Account-Token": account_token
        }
        
        try:
            # Make a simple API call to check if the token is valid
            response = requests.get(f"{MERGE_BASE_URL}/candidates?limit=1", headers=headers)
            response.raise_for_status()
            logger.info("Merge account token is valid.")
            return True
        except requests.RequestException as e:
            logger.error(f"Error validating Merge account token: {str(e)}")
            return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage candidates data in Supabase")
    parser.add_argument("--check-table", action="store_true", help="Check if the candidates table exists")
    parser.add_argument("--merge-import", action="store_true", help="Import candidates from Merge.dev API")
    parser.add_argument("--csv-import", type=str, help="Import candidates from a CSV file")
    parser.add_argument("--user-id", type=str, help="User ID for the import")
    parser.add_argument("--org-id", type=str, help="Organization ID for the import")
    parser.add_argument("--test-mode", action="store_true", help="Use test mode with mock data for development")
    
    args = parser.parse_args()
    
    try:
        manager = CandidatesManager()
        
        if args.check_table:
            exists = manager.check_table_exists()
            print(f"Candidates table exists: {exists}")
            
        if args.merge_import:
            if not args.user_id or not args.org_id:
                parser.error("--merge-import requires --user-id and --org-id")
                
            candidates = manager.fetch_merge_candidates(args.user_id, args.org_id, test_mode=args.test_mode)
            results = manager.upsert_candidates(candidates)
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