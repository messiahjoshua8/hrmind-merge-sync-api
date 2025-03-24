#!/usr/bin/env python3
import os
import logging
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yrfefwxupqobntszugjr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM")
MERGE_API_KEY = os.getenv("MERGE_API_KEY", "E109kd5kXRTmpikl3mMDms0xgAs_p5OOypOOhRDB71hSxFjjyd73uA")

# Make configuration available to manager classes
os.environ.setdefault("SUPABASE_URL", SUPABASE_URL)
os.environ.setdefault("SUPABASE_KEY", SUPABASE_KEY)
os.environ.setdefault("MERGE_API_KEY", MERGE_API_KEY)

# Set up CORS
try:
    from cors_middleware import setup_cors
    setup_cors(app)
    logger.info("CORS middleware initialized")
except ImportError as e:
    logger.warning(f"CORS middleware not available, continuing without CORS: {str(e)}")

# Import and register blueprints
try:
    from routes import sync_bp
    app.register_blueprint(sync_bp)
    logger.info("Successfully registered sync blueprint")
except ImportError as e:
    logger.error(f"Error importing blueprints: {str(e)}")
    # Fallback direct imports - used for development or if the module structure changes
    try:
        from interviews_manager import InterviewsManager
        # Other manager imports would go here
        
        # Define basic routes directly in app.py as a fallback
        @app.route('/sync/interviews', methods=['POST'])
        def sync_interviews():
            """Fallback route for interviews sync"""
            try:
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
                
                user_id = data.get('user_id')
                organization_id = data.get('organization_id')
                test_mode = data.get('test_mode', False)
                
                manager = InterviewsManager()
                interviews = manager.fetch_merge_interviews(user_id, organization_id, test_mode=test_mode)
                results = manager.upsert_interviews(interviews)
                
                return jsonify({
                    "status": "success",
                    "source": "merge_api",
                    "inserted": results['inserted'],
                    "updated": results['updated']
                })
            except Exception as e:
                logger.error(f"Error in sync_interviews: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
    except ImportError as e:
        logger.error(f"Error importing manager classes: {str(e)}")

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "API is running",
        "version": "1.0.0",
        "endpoints": [
            "/sync/interviews",
            "/sync/applications",
            "/sync/candidates",
            "/sync/jobs",
            "/sync/job_postings"
        ]
    })

# Only include these routes if the blueprint registration failed
if 'sync_bp' not in globals():
    logger.warning("Using fallback routes since blueprint registration failed")
    
    @app.route('/sync/applications', methods=['POST'])
    def sync_applications():
        """Sync applications from Merge API"""
        # Placeholder for applications sync
        return jsonify({
            "status": "error",
            "message": "Applications sync not yet implemented in fallback mode"
        }), 501

    @app.route('/sync/candidates', methods=['POST'])
    def sync_candidates():
        """Sync candidates from Merge API"""
        # Placeholder for candidates sync
        return jsonify({
            "status": "error",
            "message": "Candidates sync not yet implemented in fallback mode"
        }), 501

    @app.route('/sync/jobs', methods=['POST'])
    def sync_jobs():
        """Sync jobs from Merge API"""
        # Placeholder for jobs sync
        return jsonify({
            "status": "error",
            "message": "Jobs sync not yet implemented in fallback mode"
        }), 501

    @app.route('/sync/job_postings', methods=['POST'])
    def sync_job_postings():
        """Sync job postings from Merge API"""
        # Placeholder for job postings sync
        return jsonify({
            "status": "error",
            "message": "Job postings sync not yet implemented in fallback mode"
        }), 501

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        "status": "error",
        "message": f"Method {request.method} not allowed for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    logger.info(f"Starting server on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug) 