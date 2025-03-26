import os
import logging
import base64
import tempfile
import traceback
from flask import Blueprint, request, jsonify
import uuid

# Import the CandidatesManager
from candidates_manager import CandidatesManager

# Create a blueprint for the candidates route
candidates_bp = Blueprint('candidates', __name__, url_prefix='/candidates')

@candidates_bp.route('/', methods=['POST'])
def sync_candidates():
    """Sync candidates from Merge API or CSV.
    
    Expected JSON body:
    {
        "user_id": str,           # Required - The user ID
        "organization_id": str,   # Required - The organization ID
        "csv_file": str,          # Optional - Base64 encoded CSV file
        "test_mode": bool         # Optional - If true, use test data
    }
    
    Headers:
    - Authorization: Bearer <token> - User's auth token or a Merge account token
    
    Returns:
        JSON response with status and counts
    """
    logger.info(f"Received request to sync candidates")
    
    # Extract request data
    if not request.is_json:
        logger.error("Request must be JSON")
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400
    
    data = request.json
    logger.debug(f"Request data: {data}")
    
    # Validate required fields
    required_fields = ['user_id', 'organization_id']
    for field in required_fields:
        if field not in data:
            error_id = str(uuid.uuid4())
            logger.error(f"Error {error_id}: Missing required field: {field}")
            return jsonify({
                "status": "error",
                "error_id": error_id,
                "message": f"Missing required field: {field}"
            }), 400
    
    # Extract token from Authorization header
    user_token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        user_token = auth_header.split('Bearer ')[1].strip()
    
    # Create manager
    try:
        manager = CandidatesManager()
        
        # Check if CSV file is provided
        if data.get('csv_file'):
            # Handle CSV import
            logger.info("Processing CSV import mode")
            
            # Decode the base64 content
            try:
                csv_content = base64.b64decode(data["csv_file"])
            except Exception as e:
                logger.error(f"Error decoding CSV content: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Error decoding CSV content: {str(e)}"
                }), 400
                
            # Write to a temporary file
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
                    f.write(csv_content)
                    temp_file = f.name
                    
                # Import from the CSV file
                result = manager.import_from_csv(temp_file, data['user_id'], data['organization_id'])
                
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
            logger.info(f"Importing candidates from Merge API")
            
            # Fetch candidates using the provided user token
            test_mode = data.get('test_mode', False)
            candidates = manager.fetch_merge_candidates(
                data['user_id'], 
                data['organization_id'],
                user_token=user_token,
                test_mode=test_mode
            )
            
            result = manager.upsert_candidates(candidates)
            
            return jsonify({
                "status": "success",
                "source": "merge_api",
                "inserted": result.get("inserted", 0),
                "updated": result.get("updated", 0)
            })
    except ValueError as e:
        # Handle expected validation errors
        error_id = str(uuid.uuid4())
        logger.error(f"Validation error (ID: {error_id}): {str(e)}")
        
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_id": error_id
        }), 400
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"Error ID: {error_id} - {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": f"An error occurred while syncing candidates: {str(e)}",
            "error_id": error_id
        }), 500 