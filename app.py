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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MERGE_API_KEY = os.getenv("MERGE_API_KEY")

# Check for required environment variables
missing_vars = []
if not SUPABASE_URL:
    missing_vars.append("SUPABASE_URL")
if not SUPABASE_KEY:
    missing_vars.append("SUPABASE_KEY")
if not MERGE_API_KEY:
    missing_vars.append("MERGE_API_KEY")

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please set these variables in your environment or .env file")
    # Don't hard fail here, let the app continue but individual operations will fail securely

# Make configuration available to manager classes
os.environ.setdefault("SUPABASE_URL", SUPABASE_URL or "")
os.environ.setdefault("SUPABASE_KEY", SUPABASE_KEY or "")
os.environ.setdefault("MERGE_API_KEY", MERGE_API_KEY or "")

# Set up CORS
try:
    from cors_middleware import setup_cors
    setup_cors(app)
    logger.info("CORS middleware initialized")
except ImportError as e:
    logger.warning(f"CORS middleware not available, continuing without CORS: {str(e)}")

# Register blueprints
try:
    from routes import sync_bp
    app.register_blueprint(sync_bp)
    logger.info("Successfully registered sync blueprint")
except ImportError as e:
    logger.error(f"Error importing blueprints: {str(e)}")
    logger.warning("Using fallback routes since blueprint registration failed")

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