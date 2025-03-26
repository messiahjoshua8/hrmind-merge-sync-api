#!/usr/bin/env python3
"""
Token Service for interacting with Supabase Edge Functions.

This module provides a service for exchanging tokens securely using
Supabase Edge Functions instead of direct database access.
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class TokenService:
    """Service for secure token exchange using Supabase Edge Functions."""
    
    def __init__(self):
        """Initialize the token service with configuration from environment."""
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Missing required Supabase configuration")
            # Don't raise here, let specific methods fail with clear error messages
    
    def get_edge_function_url(self, function_name: str) -> str:
        """Get the URL for a Supabase Edge Function.
        
        Args:
            function_name: The name of the Edge Function
            
        Returns:
            The complete URL for the Edge Function
        """
        # Standard Edge Function URL pattern
        return f"{self.supabase_url}/functions/v1/{function_name}"
    
    def get_merge_token(self, user_token: str = None, test_mode: bool = False) -> Optional[str]:
        """Get a Merge API token via Supabase Edge Function.
        
        Args:
            user_token: The authenticated user's JWT token from the frontend request
                        OR a Merge account token directly
            test_mode: If True, return a dummy token for testing purposes
            
        Returns:
            The Merge API token or None if there was an error
            
        Raises:
            ValueError: If there's an issue with the request or response
        """
        if test_mode:
            logger.info("TEST MODE: Using dummy token")
            return "test_merge_token"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
        
        if not user_token:
            raise ValueError("Missing user token. Authentication required.")
        
        # Check if user_token appears to be a Merge account token already
        # Merge tokens typically start with specific patterns and have specific formats
        if len(user_token) > 20 and not user_token.startswith("ey"):  # Not a JWT token (which starts with "ey")
            logger.info("Token appears to be a Merge account token, using it directly")
            return user_token
        
        try:
            # Token is a user JWT, so exchange it via Edge Function
            # Construct the Edge Function URL
            url = self.get_edge_function_url("exchange-token")
            logger.info(f"Calling Edge Function at: {url}")
            
            # Set up headers
            headers = {
                "Authorization": f"Bearer {user_token}",
                "apikey": self.supabase_key,
                "Content-Type": "application/json"
            }
            
            # Call the Edge Function
            response = requests.post(
                url,
                headers=headers,
                json={"action": "get_merge_token"}  # Add clear payload
            )
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract the token from the response
            token = data.get("token")
            if not token:
                logger.error("No token in Edge Function response")
                raise ValueError("No token returned from Edge Function")
            
            logger.info("Successfully obtained Merge token from Edge Function")
            return token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error calling Edge Function: {str(e)}")
            if hasattr(e, 'response') and e.response:
                status_code = e.response.status_code
                if 400 <= status_code < 500:
                    logger.error(f"Client error (HTTP {status_code}): Check your request and authentication")
                elif 500 <= status_code < 600:
                    logger.error(f"Server error (HTTP {status_code}): Edge Function may be unavailable")
                
                # Log the response body if available
                try:
                    error_body = e.response.json()
                    logger.error(f"Error response: {error_body}")
                except Exception:
                    logger.error(f"Error response body: {e.response.text}")
            raise ValueError(f"Failed to fetch Merge token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting Merge token: {str(e)}")
            raise ValueError(f"Failed to fetch Merge token: {str(e)}")


# Singleton instance for easy import
token_service = TokenService() 