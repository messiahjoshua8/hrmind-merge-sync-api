import os
from flask import Flask
from flask_cors import CORS

def setup_cors(app: Flask) -> None:
    """
    Set up CORS for the Flask application.
    
    Args:
        app: The Flask application instance
    """
    # Get allowed origins from environment variable
    allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
    
    # Parse allowed origins if not "*"
    if allowed_origins != "*":
        allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]
    
    # Configure CORS settings
    cors_config = {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        "supports_credentials": True
    }
    
    # Apply CORS to the app
    CORS(app, resources={r"/*": cors_config})
    
    # Log CORS configuration
    app.logger.info(f"CORS configured with allowed origins: {allowed_origins}") 