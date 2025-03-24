#!/usr/bin/env python3
from job_postings_manager import JobPostingsManager

def update_job_posting():
    """Update a specific job posting to test the update functionality."""
    try:
        # Use the first Senior Software Engineer from the Merge API test
        job_id = "23256380-b3fd-58a4-9899-c09381f6ba52"
        
        manager = JobPostingsManager()
        
        # First, get the current data
        response = manager.supabase.table('job_postings').select('*').eq('id', job_id).execute()
        
        if not response.data or len(response.data) == 0:
            print(f"Job posting with ID {job_id} not found.")
            return
            
        job = response.data[0]
        print(f"Current job posting: {job['name']} ({job['status']})")
        
        # Update with new data
        updated_job = {
            "status": "FILLED",
            "description": job.get("description", "") + "\n\nUPDATED: This position has been filled.",
            "hiring_manager": "Alex Thompson (New Manager)"
        }
        
        # Perform the update
        update_response = manager.supabase.table('job_postings').update(updated_job).eq('id', job_id).execute()
        
        print(f"Job posting updated. New status: FILLED")
        
        # Verify the update
        verify_response = manager.supabase.table('job_postings').select('*').eq('id', job_id).execute()
        if verify_response.data and len(verify_response.data) > 0:
            updated = verify_response.data[0]
            print("\nUpdated job posting:")
            print(f"Name: {updated['name']}")
            print(f"Status: {updated['status']}")
            print(f"Hiring Manager: {updated['hiring_manager']}")
            print(f"Description: {updated['description'][:100]}...")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_job_posting() 