#!/usr/bin/env python3
from candidates_manager import CandidatesManager

def list_candidates():
    """List all candidates in the database."""
    try:
        manager = CandidatesManager()
        response = manager.supabase.table('candidates').select('*').execute()
        
        if not response.data:
            print("No candidates found.")
            return
            
        print(f"Total candidates: {len(response.data)}")
        print("\nCandidates summary:")
        print("=" * 80)
        
        for idx, candidate in enumerate(response.data):
            print(f"{idx+1}. {candidate.get('name', 'N/A')} ({candidate.get('role', 'N/A')})")
            print(f"   ID: {candidate.get('id', 'N/A')}")
            print(f"   Skills: {candidate.get('skills', [])}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_candidates() 