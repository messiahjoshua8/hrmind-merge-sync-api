#!/usr/bin/env python3
from supabase import create_client, Client
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration 
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

# Valid status values
VALID_STATUSES = ["PENDING", "SCHEDULED", "PASSED", "FAILED", "CANCELED", "NO_SHOW", "OTHER"]

# Status mapping from interview status to application status
STATUS_MAPPING = {
    "PASSED": "INTERVIEWING",  # Move to next interview round
    "FAILED": "REJECTED",      # Reject the candidate
    "CANCELED": None,          # No change
    "NO_SHOW": "REJECTED",     # Reject the candidate for not showing up
    "PENDING": None,           # No change
    "SCHEDULED": None,         # No change
    "OTHER": None              # No change
}

def list_interviews():
    """List all interviews in the database."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query for interviews
        print("Querying interviews table...")
        response = supabase.table("interviews").select("*").execute()
        
        if not response.data:
            print("No interviews found in the database.")
            return
        
        print(f"Found {len(response.data)} interviews")
        print("\nInterviews summary:")
        print("=" * 80)
        
        for idx, interview in enumerate(response.data):
            print(f"{idx+1}. Interview ID: {interview.get('id', 'N/A')}")
            print(f"   Date: {interview.get('date', 'N/A')}")
            print(f"   Status: {interview.get('status', 'N/A')}")
            print(f"   Notes: {interview.get('notes', 'N/A')[:50]}..." if interview.get('notes') and len(interview.get('notes')) > 50 else f"   Notes: {interview.get('notes', 'N/A')}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error: {str(e)}")

def get_interview(interview_id):
    """Get details for a specific interview."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get the interview data
        response = supabase.table('interviews').select('*').eq('id', interview_id).execute()
        if not response.data or len(response.data) == 0:
            print(f"Interview with ID {interview_id} not found")
            return None
            
        interview = response.data[0]
        print("\nInterview details:")
        print(f"Interview ID: {interview['id']}")
        print(f"Date: {interview.get('date', 'N/A')}")
        print(f"Time: {interview.get('time', 'N/A')}")
        print(f"Status: {interview.get('status', 'N/A')}")
        print(f"Notes: {interview.get('notes', 'N/A')}")
        print(f"Candidate ID: {interview.get('candidate_id', 'N/A')}")
        print(f"Job ID: {interview.get('job_id', 'N/A')}")
        print(f"Organization ID: {interview.get('organization_id', 'N/A')}")
        print(f"Created at: {interview.get('created_at', 'N/A')}")
        
        return interview
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def update_application_status(candidate_id, job_id, new_status):
    """Update the application status based on interview results."""
    if not candidate_id or not new_status:
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Find the application record by candidate_id only
        response = supabase.table('applications').select('*').eq('candidate_id', candidate_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"No application found for candidate {candidate_id}")
            return False
        
        # If multiple applications, log a warning but proceed with the first one
        if len(response.data) > 1:
            logger.warning(f"Multiple applications found for candidate {candidate_id}, updating the first one")
        
        application = response.data[0]
        application_id = application['id']
        current_status = application.get('status', '')
        job_posting_id = application.get('job_posting_id', '')
        
        print(f"Found application {application_id} with current status: {current_status}")
        print(f"Job Posting ID: {job_posting_id}")
        
        # Update the application status
        update_response = supabase.table('applications').update({
            'status': new_status,
            'last_updated': datetime.now().isoformat()  # Use last_updated instead of updated_at
        }).eq('id', application_id).execute()
        
        print(f"Application status updated from {current_status} to {new_status}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        return False

def update_interview(interview_id, status=None, notes_append=None, update_application=False):
    """Update a specific interview record."""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check if interviews table exists
        print("Checking if the interviews table exists...")
        check_response = supabase.table('interviews').select('id').limit(1).execute()
        if not check_response.data:
            print("No interviews found or the table doesn't exist")
            return
        
        # If no interview ID provided, get the first one from the database
        if not interview_id:
            list_response = supabase.table('interviews').select('*').limit(1).execute()
            if not list_response.data or len(list_response.data) == 0:
                print("No interviews found in the database")
                return
            interview = list_response.data[0]
            interview_id = interview['id']
            
        # Get the current interview data
        get_response = supabase.table('interviews').select('*').eq('id', interview_id).execute()
        if not get_response.data or len(get_response.data) == 0:
            print(f"Interview with ID {interview_id} not found")
            return
            
        interview = get_response.data[0]
        print("\nCurrent interview:")
        print(f"Interview ID: {interview['id']}")
        print(f"Date: {interview.get('date', 'N/A')}")
        print(f"Status: {interview.get('status', 'N/A')}")
        print(f"Notes: {interview.get('notes', 'N/A')}")
        
        # Create update data
        updated_interview = {}
        
        # Add status if provided and valid
        if status:
            if status not in VALID_STATUSES:
                print(f"Invalid status: {status}. Valid values are: {', '.join(VALID_STATUSES)}")
                return
            updated_interview["status"] = status
        
        # Add notes if provided
        if notes_append:
            # Format with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_note = f"\n\n[{timestamp}] {notes_append}"
            updated_interview["notes"] = interview.get('notes', '') + formatted_note
        
        # If nothing to update, exit
        if not updated_interview:
            print("No updates specified.")
            return
            
        # Perform the update
        update_response = supabase.table('interviews').update(updated_interview).eq('id', interview_id).execute()
        
        print(f"\nInterview updated successfully")
        
        # Update the application status if requested and status mapping exists
        if update_application and status and STATUS_MAPPING.get(status):
            candidate_id = interview.get('candidate_id')
            job_id = interview.get('job_id')
            
            if candidate_id and job_id:
                new_app_status = STATUS_MAPPING.get(status)
                if new_app_status:
                    print(f"Updating application status to {new_app_status}...")
                    update_application_status(candidate_id, job_id, new_app_status)
            else:
                print("Cannot update application status: Missing candidate_id or job_id")
        
        # Verify the update
        verify_response = supabase.table('interviews').select('*').eq('id', interview_id).execute()
        if verify_response.data and len(verify_response.data) > 0:
            updated = verify_response.data[0]
            print("\nUpdated interview:")
            print(f"Interview ID: {updated['id']}")
            print(f"Date: {updated.get('date', 'N/A')}")
            print(f"Status: {updated.get('status', 'N/A')}")
            print(f"Notes: {updated.get('notes', 'N/A')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage interview records")
    parser.add_argument("--list", action="store_true", help="List all interviews")
    parser.add_argument("--get", type=str, help="Get details for a specific interview ID")
    parser.add_argument("--update", type=str, help="Interview ID to update")
    parser.add_argument("--status", type=str, help="New status for the interview (PENDING, PASSED, FAILED, etc.)")
    parser.add_argument("--notes", type=str, help="Additional notes to append to the interview")
    parser.add_argument("--update-application", action="store_true", help="Also update the application status based on interview result")
    
    args = parser.parse_args()
    
    if args.list:
        list_interviews()
    elif args.get:
        get_interview(args.get)
    elif args.update:
        update_interview(args.update, args.status, args.notes, args.update_application)
    else:
        parser.print_help() 