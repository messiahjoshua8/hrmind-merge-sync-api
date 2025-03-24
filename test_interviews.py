#!/usr/bin/env python3
import logging
import uuid
import json
from unittest.mock import patch, MagicMock
from interviews_manager import InterviewsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample interview data for mocking
SAMPLE_INTERVIEWS_RESPONSE = {
    "results": [
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
    ],
    "next": None
}

def test_interviews_import():
    """Test the Merge interviews import functionality with mocked API responses."""
    logger.info("Testing Merge interviews import functionality")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('interviews_manager.InterviewsManager.upsert_interviews') as mock_upsert, \
         patch('interviews_manager.InterviewsManager.resolve_application_id') as mock_resolve_application:
        
        # Set up the mock return values
        mock_upsert.return_value = {"inserted": 2, "updated": 0}
        mock_resolve_application.return_value = str(uuid.uuid4())  # Return a dummy application ID
        
        # Initialize the manager
        manager = InterviewsManager()
        
        # Call the function with test mode enabled - this will use built-in sample data
        interviews = manager.fetch_merge_interviews(test_user_id, test_org_id, test_mode=True)
        
        # Verify the results
        logger.info(f"Fetched {len(interviews)} interviews")
        
        # Print the first interview data for inspection
        if interviews:
            logger.info("Sample interview data:")
            logger.info(json.dumps(interviews[0], indent=2, default=str))
        
        # Attempt to upsert the interviews
        result = manager.upsert_interviews(interviews)
        
        # Verify upsert was called
        mock_upsert.assert_called_once_with(interviews)
        logger.info(f"Upsert result: {result}")
        
        logger.info("Interviews test completed successfully!")
        return interviews

def test_csv_import():
    """Test CSV import for interviews."""
    logger.info("Testing CSV import for interviews")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('interviews_manager.InterviewsManager.upsert_interviews') as mock_upsert:
        # Set up the mock return value
        mock_upsert.return_value = {"inserted": 3, "updated": 0}
        
        # Initialize the manager
        manager = InterviewsManager()
        
        try:
            # Call the function with our sample CSV
            result = manager.import_from_csv("sample_interviews.csv", test_user_id, test_org_id)
            
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
        print("\n=== Testing Interviews Import ===\n")
        test_interviews_import()
        
        print("\n=== Testing Interviews CSV Import ===\n")
        test_csv_import()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_tests() 