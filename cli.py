#!/usr/bin/env python3
"""
Command-line tool for triggering the Merge Integration API.

This CLI provides a convenient way to trigger the various endpoints of the API
without having to manually craft HTTP requests.
"""

import os
import sys
import argparse
import requests
import json
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default API URL
DEFAULT_API_URL = "http://localhost:5000"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Merge Integration API CLI')
    
    # Global options
    parser.add_argument('--api-url', default=os.getenv('API_URL', DEFAULT_API_URL),
                        help=f'API URL (default: {DEFAULT_API_URL})')
    parser.add_argument('--user-id', default=os.getenv('USER_ID'),
                        help='User ID for the request')
    parser.add_argument('--org-id', default=os.getenv('ORGANIZATION_ID'),
                        help='Organization ID for the request')
    parser.add_argument('--test-mode', action='store_true',
                        help='Use test mode (mock data)')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check API health')
    
    # Interviews command
    interviews_parser = subparsers.add_parser('interviews', help='Sync interviews')
    interviews_parser.add_argument('--csv', help='Path to CSV file for import')
    
    # Applications command
    applications_parser = subparsers.add_parser('applications', help='Sync applications')
    applications_parser.add_argument('--csv', help='Path to CSV file for import')
    
    # Candidates command
    candidates_parser = subparsers.add_parser('candidates', help='Sync candidates')
    candidates_parser.add_argument('--csv', help='Path to CSV file for import')
    
    # Jobs command
    jobs_parser = subparsers.add_parser('jobs', help='Sync jobs')
    jobs_parser.add_argument('--csv', help='Path to CSV file for import')
    
    # Job postings command
    job_postings_parser = subparsers.add_parser('job-postings', help='Sync job postings')
    job_postings_parser.add_argument('--csv', help='Path to CSV file for import')
    
    return parser.parse_args()

def check_health(api_url):
    """Check the health of the API."""
    try:
        response = requests.get(f"{api_url}/")
        data = response.json()
        
        if response.status_code == 200:
            print("API is healthy:")
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
            print("  Available endpoints:")
            for endpoint in data.get('endpoints', []):
                print(f"    {endpoint}")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(json.dumps(data, indent=2))
            
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error connecting to API: {str(e)}")
        return False

def build_request_payload(args, csv_path=None):
    """Build the request payload from the arguments."""
    payload = {
        "user_id": args.user_id,
        "organization_id": args.org_id,
        "test_mode": args.test_mode
    }
    
    # Add CSV data if provided
    if csv_path:
        try:
            with open(csv_path, 'rb') as f:
                csv_data = f.read()
                payload["csv_file"] = base64.b64encode(csv_data).decode('utf-8')
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            sys.exit(1)
    
    return payload

def sync_data(api_url, endpoint, payload):
    """Send a sync request to the API."""
    try:
        print(f"Sending request to {api_url}{endpoint}...")
        response = requests.post(f"{api_url}{endpoint}", json=payload)
        data = response.json()
        
        if response.status_code in (200, 201):
            print("Sync completed successfully:")
            print(f"  Status: {data.get('status')}")
            print(f"  Source: {data.get('source')}")
            print(f"  Inserted: {data.get('inserted')}")
            print(f"  Updated: {data.get('updated')}")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(json.dumps(data, indent=2))
            
        return response.status_code in (200, 201)
    except requests.RequestException as e:
        print(f"Error connecting to API: {str(e)}")
        return False

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Validate required arguments
    if args.command in ('interviews', 'applications', 'candidates', 'jobs', 'job-postings'):
        if not args.user_id:
            print("Error: --user-id is required")
            sys.exit(1)
        if not args.org_id:
            print("Error: --org-id is required")
            sys.exit(1)
    
    # Execute the requested command
    if args.command == 'health':
        success = check_health(args.api_url)
    elif args.command == 'interviews':
        payload = build_request_payload(args, args.csv)
        success = sync_data(args.api_url, "/sync/interviews", payload)
    elif args.command == 'applications':
        payload = build_request_payload(args, args.csv)
        success = sync_data(args.api_url, "/sync/applications", payload)
    elif args.command == 'candidates':
        payload = build_request_payload(args, args.csv)
        success = sync_data(args.api_url, "/sync/candidates", payload)
    elif args.command == 'jobs':
        payload = build_request_payload(args, args.csv)
        success = sync_data(args.api_url, "/sync/jobs", payload)
    elif args.command == 'job-postings':
        payload = build_request_payload(args, args.csv)
        success = sync_data(args.api_url, "/sync/job_postings", payload)
    else:
        print("Please specify a command. Use --help for available commands.")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 