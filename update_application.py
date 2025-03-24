#!/usr/bin/env python3
from applications_manager import ApplicationsManager

def update_application():
    """Update a specific application to test the update functionality."""
    try:
        # Use one of the applications we imported earlier
        application_id = "a5ba1cfe-eb96-5d3a-85af-5ae9f721c08a"  # This is the INTERVIEWING status application
        
        manager = ApplicationsManager()
        
        # First, get the current data
        response = manager.supabase.table('applications').select('*').eq('id', application_id).execute()
        
        if not response.data or len(response.data) == 0:
            print(f"Application with ID {application_id} not found.")
            return
            
        application = response.data[0]
        print(f"Current application status: {application['status']}")
        print(f"For candidate ID: {application['candidate_id']}")
        print(f"For job posting ID: {application['job_posting_id']}")
        
        # Update with new data - changing status from INTERVIEWING to OFFER
        updated_application = {
            "status": "OFFER",
            "last_updated": "2023-05-25T10:00:00+00:00"  # Update the last updated timestamp
        }
        
        # Perform the update
        update_response = manager.supabase.table('applications').update(updated_application).eq('id', application_id).execute()
        
        print(f"Application updated. New status: OFFER")
        
        # Verify the update
        verify_response = manager.supabase.table('applications').select('*').eq('id', application_id).execute()
        if verify_response.data and len(verify_response.data) > 0:
            updated = verify_response.data[0]
            print("\nUpdated application:")
            print(f"Application ID: {updated['id']}")
            print(f"Status: {updated['status']}")
            print(f"Candidate ID: {updated['candidate_id']}")
            print(f"Job Posting ID: {updated['job_posting_id']}")
            print(f"Applied At: {updated['applied_at']}")
            print(f"Last Updated: {updated['last_updated']}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_application() 