import os
import logging
import base64
import tempfile
import traceback
from flask import Blueprint, request, jsonify
import uuid

# Import the JobPostingsManager (assuming it exists similar to InterviewsManager)
# from job_postings_manager import JobPostingsManager

# Create a blueprint for the job postings route
job_postings_bp = Blueprint('job_postings', __name__, url_prefix='/job_postings')

@job_postings_bp.route('/', methods=['POST'])
def sync_job_postings():
    """
    Handle POST requests to sync job postings from Merge API or from a CSV file.
    
    Expected JSON body:
    {
        "user_id": "string (required)",
        "organization_id": "string (required)",
        "csv_file": "base64-encoded CSV content (for CSV import mode)",
        "test_mode": "boolean (optional, default: false)"
    }
    
    Returns:
    JSON response with status and results
    """
    logging.info("Received request to sync job postings")
    
    # Check if we have JSON data
    if not request.is_json:
        logging.error("Request is not JSON")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["user_id", "organization_id"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        logging.error(f"Missing required fields: {missing_fields}")
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {missing_fields}"
        }), 400
    
    user_id = data["user_id"]
    organization_id = data["organization_id"]
    test_mode = data.get("test_mode", False)
    
    # Initialize the JobPostingsManager (replace this when actual manager is available)
    # job_postings_manager = JobPostingsManager(user_id, organization_id)
    
    # For demonstration purposes, simulate JobPostingsManager
    class DummyJobPostingsManager:
        def __init__(self, user_id, organization_id):
            self.user_id = user_id
            self.organization_id = organization_id
            
        def import_from_csv(self, csv_file):
            logging.info(f"Importing job postings from CSV: {csv_file}")
            # In a real implementation, this would import job postings from the CSV file
            return {"inserted": 3, "updated": 1}
            
        def import_from_merge(self, test_mode=False):
            logging.info(f"Importing job postings from Merge API (test_mode={test_mode})")
            # In a real implementation, this would import job postings from the Merge API
            return {"inserted": 2, "updated": 0}
    
    # Use the dummy manager for now
    job_postings_manager = DummyJobPostingsManager(user_id, organization_id)
    
    try:
        # Process CSV file if provided
        if "csv_file" in data and data["csv_file"]:
            logging.info("Processing CSV import mode")
            
            # Decode the base64 content
            try:
                csv_content = base64.b64decode(data["csv_file"]).decode('utf-8')
            except Exception as e:
                logging.error(f"Error decoding CSV content: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Error decoding CSV content: {str(e)}"
                }), 400
                
            # Write to a temporary file
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as f:
                    f.write(csv_content)
                    temp_file = f.name
                    
                # Import from the CSV file
                result = job_postings_manager.import_from_csv(temp_file)
                
                return jsonify({
                    "status": "success",
                    "source": "csv",
                    "inserted": result.get("inserted", 0),
                    "updated": result.get("updated", 0)
                })
            finally:
                # Clean up the temporary file
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
        else:
            # Import from Merge API
            logging.info("Processing Merge API import mode")
            result = job_postings_manager.import_from_merge(test_mode=test_mode)
            
            return jsonify({
                "status": "success",
                "source": "merge_api",
                "inserted": result.get("inserted", 0),
                "updated": result.get("updated", 0)
            })
    except Exception as e:
        error_id = str(uuid.uuid4())
        logging.error(f"Error ID: {error_id} - {str(e)}")
        logging.error(traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": f"An error occurred while syncing job postings: {str(e)}",
            "error_id": error_id
        }), 500 