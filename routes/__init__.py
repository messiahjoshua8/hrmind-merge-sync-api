"""Routes package for the Flask API.

This package contains all the route modules for the API.
"""

from flask import Blueprint

# Create a parent blueprint for all sync routes
sync_bp = Blueprint('sync', __name__, url_prefix='/sync')

# Import route modules
from routes.interviews import interviews_bp
from routes.applications import applications_bp
from routes.jobs import jobs_bp
from routes.job_postings import job_postings_bp
from routes.candidates import candidates_bp

# Register blueprints with the sync blueprint
sync_bp.register_blueprint(interviews_bp)
sync_bp.register_blueprint(applications_bp)
sync_bp.register_blueprint(jobs_bp)
sync_bp.register_blueprint(job_postings_bp)
sync_bp.register_blueprint(candidates_bp)

# Export the blueprints
__all__ = ['sync_bp'] 