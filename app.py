from app import create_app, db
from flask import jsonify
import os

# Create the Flask application instance
application = create_app()
app = application  # For compatibility with both gunicorn and direct running

# Add a direct debug route to the app
@app.route('/app-debug')
def app_debug():
    from app.models import Task
    
    # Get all tasks
    all_tasks = Task.query.all()
    
    response = {
        'task_count': len(all_tasks),
        'tasks': [{
            'id': task.id,
            'title': task.title,
            'completed': task.completed,
            'due_date': str(task.due_date) if task.due_date else None,
            'priority': task.priority
        } for task in all_tasks],
        'database_info': {
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'],
            'instance_path': app.instance_path,
            'instance_db_exists': os.path.exists(os.path.join(app.instance_path, 'tasks.db'))
        },
        'app_config': {
            'debug': app.config['DEBUG'],
            'testing': app.config.get('TESTING', False),
            'template_folder': app.template_folder
        }
    }
    
    return jsonify(response)

if __name__ == "__main__":
    # Import migrations here to avoid circular import
    from migrations.db_migrations import migrate_database
    
    # Create the app context for database operations
    with app.app_context():
        # Run migrations after the database is created
        migrate_database()
        
        # Print debug information
        from app.models import Task
        tasks = Task.query.all()
        print(f"Database contains {len(tasks)} tasks")
        for task in tasks:
            print(f"Task: {task.id} - {task.title} - {task.due_date} - {task.completed}")
    
    # Hide the Flask development server warning
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    cli = os.environ.get('FLASK_CLI', False)
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=True, cli=cli)