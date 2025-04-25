from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os
from typing import Optional, Dict, Any

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Add Jinja filters
    @app.template_filter('pprint')
    def pprint_filter(object):
        import pprint
        return pprint.pformat(object)
    
    # Load configuration
    # Ensure we use absolute path for SQLite database
    db_path = os.path.join(app.instance_path, 'tasks.db')
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f'sqlite:///{db_path}'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    if test_config:
        app.config.update(test_config)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.dashboard import dashboard_bp
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Seed database if no users exist
        from app.models import User, Task
        from datetime import datetime, timedelta
        
        if not User.query.first():
            # Create demo user
            demo_user = User(username='demo_user')
            db.session.add(demo_user)
            db.session.commit()
            
            # Create demo tasks
            today = datetime.now().date()
            task1 = Task(
                title='Complete project setup',
                description='Initialize the Flask project structure',
                due_date=today + timedelta(days=1),
                user_id=demo_user.id
            )
            
            task2 = Task(
                title='Add unit tests',
                description='Write pytest tests for the application',
                due_date=today - timedelta(days=1),  # Overdue task
                user_id=demo_user.id
            )
            
            db.session.add_all([task1, task2])
            db.session.commit()
    
    return app
