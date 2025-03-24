#!/usr/bin/env python3
import os
import logging
from supabase import create_client
import json
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direct configuration from .env values
SUPABASE_URL = "https://yrfefwxupqobntszugjr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlyZmVmd3h1cHFvYm50c3p1Z2pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzA2MzI1NywiZXhwIjoyMDUyNjM5MjU3fQ.QJ0jVi_bmds16i7huTwR5TppB--7xJK3K5wpKxyjyMM"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Essential columns that should be kept
ESSENTIAL_COLUMNS = [
    "id", 
    "organization_id", 
    "created_by", 
    "first_name", 
    "last_name", 
    "email_addresses", 
    "phone_numbers", 
    "role", 
    "company", 
    "urls", 
    "skills", 
    "experience", 
    "created_at", 
    "modified_at",
    "previous_role"
]

def get_columns():
    """Get all columns of the candidates table."""
    try:
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'candidates' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
        """
        
        response = supabase.rpc(
            fn="execute_safe_query", 
            params={"query_text": query}
        ).execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error getting columns: {str(e)}")
        return []

def analyze_columns(columns):
    """Analyze columns to determine which can be removed."""
    essential = []
    non_essential = []
    required_but_non_essential = []
    
    for column in columns:
        column_name = column['column_name']
        is_nullable = column['is_nullable'] == 'YES'
        has_default = column['column_default'] is not None
        
        if column_name in ESSENTIAL_COLUMNS:
            essential.append({
                'name': column_name,
                'is_nullable': is_nullable,
                'has_default': has_default
            })
        else:
            if not is_nullable and not has_default:
                required_but_non_essential.append({
                    'name': column_name,
                    'is_nullable': is_nullable,
                    'has_default': has_default
                })
            else:
                non_essential.append({
                    'name': column_name,
                    'is_nullable': is_nullable,
                    'has_default': has_default
                })
    
    return {
        'essential': essential,
        'non_essential': non_essential,
        'required_but_non_essential': required_but_non_essential
    }

def generate_alter_statements(columns_to_modify):
    """Generate SQL statements to make columns nullable or add defaults."""
    statements = []
    
    for column in columns_to_modify:
        column_name = column['name']
        statements.append(f"ALTER TABLE candidates ALTER COLUMN {column_name} DROP NOT NULL;")
    
    return statements

def remove_columns(columns_to_remove):
    """Execute SQL to remove unnecessary columns."""
    for column in columns_to_remove:
        column_name = column['name']
        try:
            query = f"ALTER TABLE candidates DROP COLUMN {column_name};"
            logger.info(f"Executing: {query}")
            
            if not DRY_RUN:
                response = supabase.rpc(
                    fn="execute_safe_query", 
                    params={"query_text": query}
                ).execute()
                logger.info(f"Column {column_name} removed successfully.")
            else:
                logger.info(f"[DRY RUN] Would execute: {query}")
        except Exception as e:
            logger.error(f"Error removing column {column_name}: {str(e)}")

def make_columns_nullable(columns_to_modify):
    """Execute SQL to make columns nullable."""
    for column in columns_to_modify:
        column_name = column['name']
        try:
            query = f"ALTER TABLE candidates ALTER COLUMN {column_name} DROP NOT NULL;"
            logger.info(f"Executing: {query}")
            
            if not DRY_RUN:
                response = supabase.rpc(
                    fn="execute_safe_query", 
                    params={"query_text": query}
                ).execute()
                logger.info(f"Column {column_name} modified to be nullable.")
            else:
                logger.info(f"[DRY RUN] Would execute: {query}")
        except Exception as e:
            logger.error(f"Error modifying column {column_name}: {str(e)}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Clean up candidates table in Supabase")
    parser.add_argument("--analyze", action="store_true", help="Analyze the table structure")
    parser.add_argument("--modify", action="store_true", help="Make required non-essential columns nullable")
    parser.add_argument("--remove", action="store_true", help="Remove non-essential columns")
    parser.add_argument("--dry-run", action="store_true", help="Don't execute SQL, just print what would be done")
    
    args = parser.parse_args()
    
    global DRY_RUN
    DRY_RUN = args.dry_run
    
    if not (args.analyze or args.modify or args.remove):
        parser.error("At least one of --analyze, --modify, or --remove is required")
    
    try:
        # Get current table structure
        columns = get_columns()
        
        if args.analyze:
            # Analyze columns
            analysis = analyze_columns(columns)
            
            print("\nEssential columns to keep:")
            for col in analysis['essential']:
                nullable = "nullable" if col['is_nullable'] else "NOT NULL"
                print(f"- {col['name']} ({nullable})")
            
            print("\nNon-essential columns that can be removed:")
            for col in analysis['non_essential']:
                nullable = "nullable" if col['is_nullable'] else "NOT NULL"
                print(f"- {col['name']} ({nullable})")
            
            print("\nRequired but non-essential columns (need to be made nullable first):")
            for col in analysis['required_but_non_essential']:
                print(f"- {col['name']} (NOT NULL)")
                
            if analysis['required_but_non_essential']:
                print("\nSQL to make required columns nullable:")
                for statement in generate_alter_statements(analysis['required_but_non_essential']):
                    print(statement)
        
        if args.modify:
            # Get columns to modify
            analysis = analyze_columns(columns)
            if analysis['required_but_non_essential']:
                make_columns_nullable(analysis['required_but_non_essential'])
            else:
                print("No required non-essential columns to modify.")
        
        if args.remove:
            # Get columns to remove
            analysis = analyze_columns(columns)
            columns_to_remove = analysis['non_essential']
            
            if args.modify:
                # If we're also modifying columns, we can remove the previously required ones too
                columns_to_remove.extend(analysis['required_but_non_essential'])
            
            if columns_to_remove:
                remove_columns(columns_to_remove)
            else:
                print("No non-essential columns to remove.")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 