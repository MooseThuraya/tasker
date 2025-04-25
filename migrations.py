import sqlite3
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_database():
    """
    Apply migrations to the database to add new columns without losing existing data.
    """
    db_path = os.path.join('instance', 'tasks.db')
    
    if not os.path.exists(db_path):
        logger.warning(f"Database file {db_path} not found. No migration needed.")
        return
    
    logger.info(f"Starting database migration for {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the priority column exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column_info[1] for column_info in cursor.fetchall()]
        
        # Apply migrations only if needed
        if 'priority' not in columns:
            logger.info("Adding new columns to tasks table")
            
            # SQLite doesn't support ALTER TABLE ADD COLUMN with multiple columns,
            # so we need to execute them one by one
            migrations = [
                "ALTER TABLE tasks ADD COLUMN priority TEXT",
                "ALTER TABLE tasks ADD COLUMN tags TEXT",
                "ALTER TABLE tasks ADD COLUMN archived BOOLEAN DEFAULT 0 NOT NULL",
                "ALTER TABLE tasks ADD COLUMN archived_at TIMESTAMP"
            ]
            
            for migration in migrations:
                cursor.execute(migration)
                logger.info(f"Executed: {migration}")
            
            conn.commit()
            logger.info("Migration completed successfully")
        else:
            logger.info("No migration needed, columns already exist")
    
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 