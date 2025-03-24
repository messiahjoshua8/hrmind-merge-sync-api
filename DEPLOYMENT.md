# Deployment Guide

This document outlines the steps to deploy the Merge Integration API to various environments.

## Prerequisites

- Python 3.8 or higher
- pip or pip3
- Git
- A Supabase account with project set up
- A Merge.dev account with API credentials

## Local Deployment

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

3. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor
   ```

4. Run the application:
   ```bash
   python app.py
   # Or with gunicorn:
   gunicorn app:app
   ```

5. Test the API:
   ```bash
   # Using the CLI tool
   ./cli.py health
   ```

## Railway Deployment

1. Create a Railway account at https://railway.app/ if you don't have one already.

2. Create a new project in Railway.

3. Connect your GitHub repository to Railway:
   - Click on "Deploy" and select "GitHub Repo"
   - Find and select your repository
   - Click "Deploy Now"

4. Set the required environment variables in Railway:
   - Navigate to your project's "Variables" tab
   - Add the following variables:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `MERGE_API_KEY`
     - `FLASK_ENV`
     - `CORS_ALLOWED_ORIGINS`

5. Railway should automatically detect the Procfile and deploy your application.

6. Once deployed, you can find your application URL in the "Deployments" tab.

## Heroku Deployment

1. Create a Heroku account at https://signup.heroku.com/ if you don't have one already.

2. Install the Heroku CLI:
   ```bash
   # For macOS (using Homebrew)
   brew install heroku/brew/heroku

   # For Windows (using Chocolatey)
   choco install heroku-cli

   # For Ubuntu/Debian
   curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
   ```

3. Log in to the Heroku CLI:
   ```bash
   heroku login
   ```

4. Create a new Heroku app:
   ```bash
   heroku create merge-integration-api
   ```

5. Set the required environment variables:
   ```bash
   heroku config:set SUPABASE_URL=your-supabase-url
   heroku config:set SUPABASE_KEY=your-supabase-key
   heroku config:set MERGE_API_KEY=your-merge-api-key
   heroku config:set FLASK_ENV=production
   heroku config:set CORS_ALLOWED_ORIGINS=*
   ```

6. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

7. Ensure at least one instance is running:
   ```bash
   heroku ps:scale web=1
   ```

8. Open your deployed app:
   ```bash
   heroku open
   ```

## Docker Deployment

1. Make sure Docker is installed on your system.

2. Build the Docker image:
   ```bash
   docker build -t merge-integration-api .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 5000:5000 \
     -e SUPABASE_URL=your-supabase-url \
     -e SUPABASE_KEY=your-supabase-key \
     -e MERGE_API_KEY=your-merge-api-key \
     -e FLASK_ENV=production \
     -e CORS_ALLOWED_ORIGINS=* \
     merge-integration-api
   ```

4. Access the API at http://localhost:5000

## Troubleshooting

### Common Issues

1. **Connection to Supabase fails**:
   - Ensure the `SUPABASE_URL` and `SUPABASE_KEY` environment variables are set correctly
   - Check that the Supabase project is up and running
   - Verify that the service role key has the necessary permissions

2. **Merge API authentication fails**:
   - Verify that the `MERGE_API_KEY` is correct and has not expired
   - Check that your Merge account has the necessary permissions

3. **CORS issues**:
   - Set `CORS_ALLOWED_ORIGINS` to include your frontend origin
   - For local testing, you can set it to `*`

4. **Database migration issues**:
   - Ensure your Supabase database schema matches the expected schema for the application

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the application logs:
   ```bash
   # For Railway
   railway logs

   # For Heroku
   heroku logs --tail
   ```

2. Submit an issue on the GitHub repository with:
   - A description of the problem
   - Steps to reproduce
   - Error messages or stack traces
   - Environment information (OS, Python version, etc.) 