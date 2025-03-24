#!/usr/bin/env python3
import logging
import uuid
import json
from unittest.mock import patch, MagicMock
from candidates_manager import CandidatesManager
from job_postings_manager import JobPostingsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample response data for mocking
SAMPLE_CANDIDATES_RESPONSE = {
    "results": [
        {
            "remote_id": "abc123",
            "first_name": "John",
            "last_name": "Test",
            "emails": [
                {"type": "primary", "value": "john.test@example.com"}
            ],
            "phone_numbers": [
                {"type": "primary", "value": "123-456-7890"}
            ],
            "current_title": "Software Engineer",
            "current_company": "Test Company",
            "resume_url": "https://example.com/resume.pdf",
            "skills": ["Python", "JavaScript", "SQL"],
            "years_experience": 5,
            "past_titles": ["Junior Developer", "Developer"]
        },
        {
            "remote_id": "def456",
            "first_name": "Jane",
            "last_name": "Sample",
            "emails": [
                {"type": "primary", "value": "jane.sample@example.com"}
            ],
            "phone_numbers": [
                {"type": "primary", "value": "234-567-8901"}
            ],
            "current_title": "Product Manager",
            "current_company": "Sample Inc",
            "resume_url": "https://example.com/resume2.pdf",
            "skills": ["Product Management", "Agile", "UX"],
            "years_experience": 7,
            "past_titles": ["Associate PM", "Business Analyst"]
        }
    ],
    "next": None
}

# Sample job postings data for mocking
SAMPLE_JOB_POSTINGS_RESPONSE = {
    "results": [
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
    ],
    "next": None
}

def test_candidates_import():
    """Test the Merge candidates import functionality with mocked API responses."""
    logger.info("Testing Merge candidates import functionality")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('candidates_manager.CandidatesManager.upsert_candidates') as mock_upsert:
        # Set up the mock return value
        mock_upsert.return_value = {"inserted": 2, "updated": 0}
        
        # Initialize the manager
        manager = CandidatesManager()
        
        # Call the function with test mode enabled - this will use built-in sample data
        candidates = manager.fetch_merge_candidates(test_user_id, test_org_id, test_mode=True)
        
        # Verify the results
        logger.info(f"Fetched {len(candidates)} candidates")
        
        # Print the first candidate data for inspection
        if candidates:
            logger.info("Sample candidate data:")
            logger.info(json.dumps(candidates[0], indent=2, default=str))
        
        # Attempt to upsert the candidates
        result = manager.upsert_candidates(candidates)
        
        # Verify upsert was called
        mock_upsert.assert_called_once_with(candidates)
        logger.info(f"Upsert result: {result}")
        
        logger.info("Candidates test completed successfully!")
        return candidates

def test_job_postings_import():
    """Test the Merge job postings import functionality with mocked API responses."""
    logger.info("Testing Merge job postings import functionality")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('job_postings_manager.JobPostingsManager.upsert_job_postings') as mock_upsert:
        # Set up the mock return value
        mock_upsert.return_value = {"inserted": 2, "updated": 0}
        
        # Initialize the manager
        manager = JobPostingsManager()
        
        # Call the function with test mode enabled - this will use built-in sample data
        job_postings = manager.fetch_merge_job_postings(test_user_id, test_org_id, test_mode=True)
        
        # Verify the results
        logger.info(f"Fetched {len(job_postings)} job postings")
        
        # Print the first job posting data for inspection
        if job_postings:
            logger.info("Sample job posting data:")
            logger.info(json.dumps(job_postings[0], indent=2, default=str))
        
        # Attempt to upsert the job postings
        result = manager.upsert_job_postings(job_postings)
        
        # Verify upsert was called
        mock_upsert.assert_called_once_with(job_postings)
        logger.info(f"Upsert result: {result}")
        
        logger.info("Job postings test completed successfully!")
        return job_postings

def test_csv_import():
    """Test CSV import for job postings."""
    logger.info("Testing CSV import for job postings")
    
    # Create test IDs
    test_user_id = str(uuid.uuid4())
    test_org_id = str(uuid.uuid4())
    
    with patch('job_postings_manager.JobPostingsManager.upsert_job_postings') as mock_upsert:
        # Set up the mock return value
        mock_upsert.return_value = {"inserted": 3, "updated": 0}
        
        # Initialize the manager
        manager = JobPostingsManager()
        
        try:
            # Call the function with our sample CSV
            result = manager.import_from_csv("sample_job_postings.csv", test_user_id, test_org_id)
            
            # Verify upsert was called
            assert mock_upsert.call_count == 1
            logger.info(f"CSV import result: {result}")
            
            logger.info("CSV import test completed successfully!")
        except Exception as e:
            logger.error(f"CSV import test failed: {str(e)}")
            
if __name__ == "__main__":
    try:
        # Test both candidates and job postings functionality
        print("\n=== Testing Candidates Import ===\n")
        test_candidates_import()
        
        print("\n=== Testing Job Postings Import ===\n")
        test_job_postings_import()
        
        print("\n=== Testing Job Postings CSV Import ===\n")
        test_csv_import()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}") 