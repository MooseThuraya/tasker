#!/usr/bin/env python3
"""
Script to reset the database and seed it with sample data.
Use this when you need to start fresh or test database migrations.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Configure paths
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Get possible database paths
db_paths = [
    os.path.join(script_dir, 'tasks.db'),
    os.path.join(script_dir, 'instance', 'tasks.db')
]

# Import app to create the database first so we can get the correct instance path
from app import create_app, db
from app.models import User, Task

# Get the application instance to find the correct instance path
app = create_app({"DEBUG": True})
instance_db_path = os.path.join(app.instance_path, 'tasks.db')
db_paths.append(instance_db_path)

# Delete the database if it exists in any location
for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
        print("Database removed.")
    else:
        print(f"No database found at: {db_path}")

def reset_database():
    """Reset the database and seed it with sample data."""
    # Make sure the instance directory exists
    instance_dir = os.path.join(script_dir, 'instance')
    if not os.path.exists(instance_dir):
        print(f"Creating instance directory: {instance_dir}")
        os.makedirs(instance_dir)
        
    print("Creating fresh application instance...")
    app = create_app({
        "DEBUG": True,
        "SQLALCHEMY_ECHO": True,  # Log SQL queries
    })
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Seeding database with sample data...")
        # Check if demo user exists
        demo_user = User.query.filter_by(username='demo_user').first()
        
        print(f"Demo user exists: {demo_user is not None}")
        
        if not demo_user:
            # Create demo user
            print("Creating demo user...")
            demo_user = User(username='demo_user')
            db.session.add(demo_user)
            db.session.commit()
            print(f"Created user with ID: {demo_user.id}")
        else:
            print(f"Using existing demo user with ID: {demo_user.id}")
        
        # Clear existing tasks
        print("Clearing existing tasks...")
        task_count = Task.query.count()
        print(f"Found {task_count} existing tasks")
        Task.query.delete()
        db.session.commit()
        print("All tasks deleted")
        
        # Create sample tasks with various states and dates
        # Use 2025 as our demo year to ensure dates match today's real date
        year = 2025
        month = date.today().month
        day = date.today().day
        
        today = date(year, month, day)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Create a variety of tasks with different states
        tasks = [
            Task(
                title='Complete project setup',
                description='Initialize the Flask project structure and configure dependencies',
                due_date=tomorrow,
                user_id=demo_user.id,
                priority='high',
                tags='work, project'
            ),
            Task(
                title='Write documentation',
                description='Create comprehensive README and architecture documentation',
                due_date=next_week,
                user_id=demo_user.id,
                priority='medium',
                tags='docs, project'
            ),
            Task(
                title='Fix navigation bug',
                description='Address issue with navigation menu on mobile devices',
                due_date=yesterday,
                user_id=demo_user.id,
                priority='high',
                completed=True,
                tags='bug, urgent'
            ),
            Task(
                title='Plan team meeting',
                description='Organize weekly team sync and prepare agenda',
                due_date=today,
                user_id=demo_user.id,
                priority='medium',
                tags='meeting, team'
            ),
            Task(
                title='Research new features',
                description='Investigate potential features for next sprint',
                due_date=next_week,
                user_id=demo_user.id,
                priority='low',
                tags='research, planning'
            ),
            Task(
                title='Old archived task',
                description='This is an old task that has been archived',
                due_date=yesterday - timedelta(days=10),
                user_id=demo_user.id,
                priority='low',
                archived=True,
                archived_at=datetime.utcnow() - timedelta(days=5),
                tags='old, archived'
            )
        ]
        
        db.session.add_all(tasks)
        db.session.commit()
        
        print(f"Database seeded with {len(tasks)} tasks for user 'demo_user'.")
        print("Sample data includes: high/medium/low priorities, tags, completed and archived tasks.")
        
        # Get actual DB path from Flask
        instance_path = app.instance_path
        db_path = os.path.join(instance_path, 'tasks.db')
        print(f"Flask instance path: {instance_path}")
        print(f"Database location: {db_path}")
        print(f"Database exists: {os.path.exists(db_path)}")
        
        # Verify the tasks were created successfully
        print("\nVerifying tasks in database:")
        all_tasks = Task.query.all()
        print(f"Total tasks in database: {len(all_tasks)}")
        
        for task in all_tasks:
            print(f"Task ID: {task.id} | Title: {task.title} | Due: {task.due_date} | Priority: {task.priority} | Completed: {task.completed}")

if __name__ == "__main__":
    try:
        reset_database()
        print("Database reset and seeded successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)