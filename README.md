# Merge Integration API

A Flask-based REST API for synchronizing data between Merge.dev and Supabase.

## Overview

This API wraps the existing Python scripts for syncing candidates, job postings, applications, and interviews into Flask route handlers. It allows for programmatic access to the sync functionality through REST API endpoints.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd merge-integration-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and fill in your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor
   ```

## Running Locally

```bash
python app.py
```

Or with gunicorn:
```bash
gunicorn app:app
```

## API Endpoints

### Health Check

```
GET /
```

Returns status information about the API.

### Sync Interviews

```
POST /sync/interviews
```

Syncs interviews from Merge API or from a CSV file.

**Request Body (API Mode):**
```json
{
  "user_id": "e3c418cc-4b8a-4d7b-b76d-18d0752a2e4c",
  "organization_id": "05b3cc97-5d8a-4632-9959-29d0fc379fc9",
  "test_mode": false
}
```

**Request Body (CSV Mode):**
```json
{
  "user_id": "e3c418cc-4b8a-4d7b-b76d-18d0752a2e4c",
  "organization_id": "05b3cc97-5d8a-4632-9959-29d0fc379fc9",
  "csv_file": "base64-encoded-csv-content"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "source": "merge_api",
  "inserted": 3,
  "updated": 1
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

### Sync Applications

```
POST /sync/applications
```

Syncs applications from Merge API or from a CSV file.

**Request/Response format is similar to the interviews endpoint.**

### Sync Candidates

```
POST /sync/candidates
```

Syncs candidates from Merge API or from a CSV file.

**Request/Response format is similar to the interviews endpoint.**

### Sync Jobs

```
POST /sync/jobs
```

Syncs jobs from Merge API or from a CSV file.

**Request/Response format is similar to the interviews endpoint.**

### Sync Job Postings

```
POST /sync/job_postings
```

Syncs job postings from Merge API or from a CSV file.

**Request/Response format is similar to the interviews endpoint.**

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | https://yrfefwxupqobntszugjr.supabase.co |
| `SUPABASE_KEY` | Supabase service role key | - |
| `MERGE_API_KEY` | Merge API key | - |
| `PORT` | Port for the server to listen on | 5000 |
| `FLASK_ENV` | Flask environment (development/production) | production |

## Deployment on Railway

This project is configured for deployment on Railway:

1. Create a new project on Railway and connect your GitHub repository.
2. Add the required environment variables in Railway's settings.
3. Railway will automatically use the provided `Procfile` for deployment.

For more detailed deployment instructions, including Docker, Heroku, and local deployment, see the [Deployment Guide](DEPLOYMENT.md).

## Testing

To run the tests:
```bash
python -m unittest discover
```

## CLI Tool

A command-line interface (CLI) tool is included to facilitate interactions with the API:

```bash
# Make the CLI script executable if it's not already
chmod +x cli.py

# Check the API health
./cli.py health --api-url http://localhost:5000

# Sync interviews from Merge API
./cli.py interviews --user-id [user-id] --org-id [org-id]

# Sync interviews from a CSV file
./cli.py interviews --user-id [user-id] --org-id [org-id] --csv path/to/interviews.csv

# Use test mode (mock data)
./cli.py interviews --user-id [user-id] --org-id [org-id] --test-mode
```

The CLI supports all the sync endpoints:
- interviews
- applications
- candidates
- jobs
- job-postings

You can also set default values in your `.env` file:
```
API_URL=http://localhost:5000
USER_ID=your-default-user-id
ORGANIZATION_ID=your-default-org-id
```

## Modular Structure

The project is organized with the following structure:

```
/
├── app.py                    # Main Flask application
├── routes/                   # Module for route handlers
│   ├── __init__.py           # Blueprint registration
│   ├── applications.py       # Applications routes
│   ├── candidates.py         # Candidates routes
│   ├── interviews.py         # Interviews routes
│   ├── jobs.py               # Jobs routes
│   └── job_postings.py       # Job Postings routes
├── requirements.txt          # Dependencies
├── Procfile                  # For Railway deployment
├── railway.json              # Railway configuration
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Architecture

The API follows a modular architecture with clear separation of concerns:

1. **Route Handlers** (`routes/` directory):
   - Blueprint-based route organization
   - Each entity (interviews, applications, etc.) has its own module
   - Handles HTTP requests/responses, validation, and error handling

2. **Data Managers** (e.g., `interviews_manager.py`):
   - Responsible for data operations
   - Interfaces with both the Merge API and Supabase database
   - Handles transformations between data formats
   - Takes care of CSV import/export operations

3. **Main Application** (`app.py`):
   - Sets up the Flask application
   - Configures middleware (CORS, etc.)
   - Registers blueprints and fallback routes
   - Handles global error cases

4. **CLI Tool** (`cli.py`):
   - Provides a command-line interface to the API
   - Makes it easy to test and use the API without writing HTTP clients

### Data Flow

1. **API Mode**:
   ```
   Client Request → Route Handler → Data Manager → Merge API → Data Manager → Supabase → Response
   ```

2. **CSV Mode**:
   ```
   Client Request (with CSV) → Route Handler → Data Manager → Supabase → Response
   ```

## Security Considerations

- All sensitive credentials are stored as environment variables, not in the code.
- Input validation is performed on all API requests.
- Error handling prevents exposure of sensitive information.
- CORS policies should be configured appropriately for production use.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push the branch: `git push origin feature-name`
5. Submit a pull request 