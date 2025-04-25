import sqlite3
from pathlib import Path
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_migrations')

def migrate_database():
    """Apply database migrations to add new fields and update schema"""
    logger.info("Starting database migrations...")
    
    try:
        # Get the database path from environment or use default
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
        
        # Check both possible database locations
        instance_db_path = os.path.join(os.getcwd(), 'instance', 'tasks.db')
        direct_db_path = os.path.join(os.getcwd(), 'tasks.db')
        
        if os.path.exists(instance_db_path):
            db_file = Path(instance_db_path)
            logger.info(f"Using database at: {instance_db_path}")
        elif os.path.exists(direct_db_path):
            db_file = Path(direct_db_path)
            logger.info(f"Using database at: {direct_db_path}")
        elif db_url.startswith('sqlite:///'):
            # Extract the filename from the SQLite URL
            db_path = db_url[10:]
            db_file = Path(db_path)
            
            # If using a relative path, make it relative to the current directory
            if not db_file.is_absolute():
                db_file = Path.cwd() / db_path
                
            logger.info(f"Using database path from URL: {db_file}")
        else:
            logger.info("Not a SQLite database, skipping migrations")
            return
        
        # Check if database exists
        if not db_file.exists():
            logger.info(f"Database {db_file} does not exist yet, skipping migrations")
            return
        
        # Connect to database
        logger.info(f"Connecting to database: {db_file}")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Migration 1: Add priority field to tasks table
        try:
            # Check if column already exists
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'priority' not in columns:
                logger.info("Adding 'priority' column to tasks table")
                cursor.execute("ALTER TABLE tasks ADD COLUMN priority VARCHAR(10)")
            else:
                logger.info("Column 'priority' already exists")
            
            # Migration 2: Add tags field to tasks table
            if 'tags' not in columns:
                logger.info("Adding 'tags' column to tasks table")
                cursor.execute("ALTER TABLE tasks ADD COLUMN tags TEXT")
            else:
                logger.info("Column 'tags' already exists")
            
            # Migration 3: Add archived fields to tasks table
            if 'archived' not in columns:
                logger.info("Adding 'archived' column to tasks table")
                cursor.execute("ALTER TABLE tasks ADD COLUMN archived BOOLEAN DEFAULT 0")
            else:
                logger.info("Column 'archived' already exists")
            
            if 'archived_at' not in columns:
                logger.info("Adding 'archived_at' column to tasks table")
                cursor.execute("ALTER TABLE tasks ADD COLUMN archived_at TIMESTAMP")
            else:
                logger.info("Column 'archived_at' already exists")
            
            # Commit changes
            conn.commit()
            logger.info("Database migrations completed successfully")
            
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    except Exception as e:
        logger.error(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_database()