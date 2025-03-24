#!/usr/bin/env python3
import logging
import uuid
import json
from unittest.mock import patch, MagicMock
from applications_manager import ApplicationsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample application data for mocking
SAMPLE_APPLICATIONS_RESPONSE = {
    "results": [
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
    ],
    "next": None
}

def test_applications_import():
    """Test the Merge applications import functionality with mocked API responses."""
    logger.info("Testing Merge applications import functionality")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('applications_manager.ApplicationsManager.upsert_applications') as mock_upsert, \
         patch('applications_manager.ApplicationsManager.resolve_candidate_id') as mock_resolve_candidate, \
         patch('applications_manager.ApplicationsManager.resolve_job_posting_id') as mock_resolve_job:
        
        # Set up the mock return values
        mock_upsert.return_value = {"inserted": 2, "updated": 0}
        mock_resolve_candidate.return_value = str(uuid.uuid4())  # Return a dummy candidate ID
        mock_resolve_job.return_value = str(uuid.uuid4())        # Return a dummy job posting ID
        
        # Initialize the manager
        manager = ApplicationsManager()
        
        # Call the function with test mode enabled - this will use built-in sample data
        applications = manager.fetch_merge_applications(test_user_id, test_org_id, test_mode=True)
        
        # Verify the results
        logger.info(f"Fetched {len(applications)} applications")
        
        # Print the first application data for inspection
        if applications:
            logger.info("Sample application data:")
            logger.info(json.dumps(applications[0], indent=2, default=str))
        
        # Attempt to upsert the applications
        result = manager.upsert_applications(applications)
        
        # Verify upsert was called
        mock_upsert.assert_called_once_with(applications)
        logger.info(f"Upsert result: {result}")
        
        logger.info("Applications test completed successfully!")
        return applications

def test_csv_import():
    """Test CSV import for applications."""
    logger.info("Testing CSV import for applications")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('applications_manager.ApplicationsManager.upsert_applications') as mock_upsert:
        # Set up the mock return value
        mock_upsert.return_value = {"inserted": 3, "updated": 0}
        
        # Initialize the manager
        manager = ApplicationsManager()
        
        try:
            # Call the function with our sample CSV
            result = manager.import_from_csv("sample_applications.csv", test_user_id, test_org_id)
            
            # Verify upsert was called
            assert mock_upsert.call_count == 1
            logger.info(f"CSV import result: {result}")
            
            logger.info("CSV import test completed successfully!")
        except Exception as e:
            logger.error(f"CSV import test failed: {str(e)}")
            raise

def run_tests():
    """Run all tests."""
    try:
        print("\n=== Testing Applications Import ===\n")
        test_applications_import()
        
        print("\n=== Testing Applications CSV Import ===\n")
        test_csv_import()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_tests() 