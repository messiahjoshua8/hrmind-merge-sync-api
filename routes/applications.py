#!/usr/bin/env python3
"""
Applications sync route handler.
This file provides the route handler for syncing applications with Merge API.
"""
import os
import logging
import base64
import tempfile
import traceback
import uuid
from flask import Blueprint, request, jsonify

# Import the applications manager
from applications_manager import ApplicationsManager

logger = logging.getLogger(__name__)

# Create a blueprint for applications routes
applications_bp = Blueprint('applications', __name__, url_prefix='/applications')

@applications_bp.route('/', methods=['POST'])
def sync_applications():
    """Sync applications from Merge API or CSV.
    
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
    logger.info(f"Received request to sync applications")
    
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
        manager = ApplicationsManager()
        
        # Check if CSV file is provided
        if data.get('csv_file'):
            # Handle CSV import
            # CSV import mode - requires base64 encoded CSV content
            csv_content = base64.b64decode(data['csv_file'])
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
                temp_file.write(csv_content)
                temp_file_path = temp_file.name
            
            try:
                # Import from CSV
                results = manager.import_from_csv(temp_file_path, data['user_id'], data['organization_id'])
                os.unlink(temp_file_path)  # Clean up temp file
                
                return jsonify({
                    "status": "success",
                    "source": "csv",
                    "inserted": results['inserted'],
                    "updated": results['updated']
                })
            except Exception as e:
                # Clean up temp file in case of exception
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise e
        else:
            # Import from Merge API
            logger.info(f"Importing applications from Merge API")
            
            # Fetch applications using the provided user token
            test_mode = data.get('test_mode', False)
            applications = manager.fetch_merge_applications(
                data['user_id'], 
                data['organization_id'],
                user_token=user_token,
                test_mode=test_mode
            )
            
            results = manager.upsert_applications(applications)
            
            return jsonify({
                "status": "success",
                "source": "merge_api",
                "inserted": results['inserted'],
                "updated": results['updated']
            })
    except ValueError as e:
        # Handle expected validation errors
        logger.error(f"Validation error in sync_applications: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400        
    except Exception as e:
        logger.error(f"Error in sync_applications: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 