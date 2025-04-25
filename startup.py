#!/usr/bin/env python3
"""
Startup script for the Task Manager application
This script:
1. Creates a fresh database
2. Seeds it with sample data
3. Starts the Flask application
"""

import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('startup')

def main():
    # Print welcome message
    print("\n=== Task Manager Application Startup ===\n")
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Import the necessary modules
    try:
        # Reset and seed the database
        print("Step 1: Resetting and seeding the database...")
        import reset_db
        reset_db.reset_database()
        
        # Import app
        from app import create_app, db
        from app.models import Task
        
        # Create the application instance
        app = create_app({"DEBUG": True})
        
        # Verify database status
        with app.app_context():
            task_count = Task.query.count()
            print(f"\nVerification: Database contains {task_count} tasks")
            
            # Print accessible URLs
            print("\n=== Application Ready ===")
            print("The application will be available at:")
            print("- Main page: http://localhost:5003/")
            print("- Dashboard: http://localhost:5003/dashboard/")
            print("- Debug page: http://localhost:5003/app-debug")
            print("\nPress Ctrl+C to stop the server when you're done\n")
        
        # Start the application
        app.run(host="0.0.0.0", port=5003, debug=True)
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()