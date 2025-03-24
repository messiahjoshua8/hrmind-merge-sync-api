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
from flask import Blueprint, request, jsonify

# Assuming applications_manager.py is similar to interviews_manager.py
# If the actual implementation is different, this would need to be adjusted
from interviews_manager import InterviewsManager  # Placeholder, replace with actual import

logger = logging.getLogger(__name__)

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/sync/applications', methods=['POST'])
def sync_applications():
    """Sync applications from Merge API or CSV"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'organization_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "status": "error", 
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Extract fields
        user_id = data.get('user_id')
        organization_id = data.get('organization_id')
        test_mode = data.get('test_mode', False)
        
        # Create manager instance
        # In a real implementation, use the actual applications manager
        # For now, using the interviews manager as a placeholder
        manager = InterviewsManager()  # Replace with ApplicationsManager() when available
        
        # Choose appropriate action based on data
        if 'csv_file' in data:
            # CSV import mode - requires base64 encoded CSV content
            csv_content = base64.b64decode(data['csv_file'])
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
                temp_file.write(csv_content)
                temp_file_path = temp_file.name
            
            try:
                # Import from CSV - replace with actual method when available
                results = manager.import_from_csv(temp_file_path, user_id, organization_id)
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
            # Merge API import mode - replace with actual method when available
            applications = manager.fetch_merge_interviews(user_id, organization_id, test_mode=test_mode)
            results = manager.upsert_interviews(applications)
            
            return jsonify({
                "status": "success",
                "source": "merge_api",
                "inserted": results['inserted'],
                "updated": results['updated']
            })
            
    except Exception as e:
        logger.error(f"Error in sync_applications: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 