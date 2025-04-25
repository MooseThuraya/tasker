# Tasker - A Modern Task Management Application

A production-ready Flask application for task management with comprehensive metrics dashboard.

## Features

- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Set task priorities (high, medium, low)
- Add tags to tasks
- Filter and search tasks
- Archive completed tasks
- Dashboard with task metrics
- Mobile-responsive design

## Technical Stack

- **Backend**: Python 3.11+, Flask 2.x
- **ORM**: SQLAlchemy 2.0 with Declarative API and full type hints
- **Database**: SQLite (dev), configurable for SQL Server via DATABASE_URL
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: Jinja2 templates, Bootstrap 5
- **Containerization**: Docker with docker-compose
- **CI/CD**: GitHub Actions workflow
- **Testing**: pytest suite with smoke tests

## Quick Start

```bash
# Clone the repository
git clone https://github.com/MooseThuraya/tasker.git
cd tasker

# Use the startup script
python startup.py
```

The application will be available at `http://localhost:5003`

### Alternative Startup Methods

On Linux/macOS:
```bash
chmod +x run.sh
./run.sh
```

On Windows:
```bash
run.bat
```

### Using Docker

```bash
docker-compose up -d
```

The Docker version will be available at `http://localhost:5001`

## Project Structure

```
tasker/
├── app/                    # Application package
│   ├── __init__.py         # Application factory
│   ├── models.py           # SQLAlchemy models
│   ├── forms.py            # WTForms definitions
│   ├── utils.py            # Utility functions
│   └── blueprints/         # Route blueprints
│       ├── tasks.py        # Task-related routes
│       └── dashboard.py    # Dashboard routes
├── static/                 # Static assets
│   └── css/                # CSS files
├── templates/              # Jinja2 templates
├── migrations/             # Database migrations
├── instance/               # Instance-specific data
├── tests/                  # Test suite
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
├── app.py                  # Application entry point
├── startup.py              # Simplified startup script
├── docker-compose.yml      # Docker Compose config
└── Dockerfile              # Docker config
```

## Task Management Features

- **Task Creation**: Create tasks with title, description, due date, priority, and tags
- **Task Viewing**: View all tasks in a sortable, filterable list
- **Task Editing**: Update task details, mark as complete, change priority
- **Task Archiving**: Archive completed tasks to keep the main list clean
- **Task Filtering**: Filter by status (completed, pending, overdue) and priority
- **Task Search**: Search for tasks by title

## Dashboard

The dashboard provides analytical insights:

- Total task count
- Completion rate (count and percentage)
- Overdue task count
- Visual progress indicators

## Configuration

Configuration is managed through environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///tasks.db` |
| `SECRET_KEY` | Cryptographic key for sessions | `dev` |
| `FLASK_ENV` | Runtime environment | `development` |

## Note for macOS Users

Port 5000 is used by AirPlay Receiver on macOS. The application uses ports 5001 (Docker) or 5003 (local) by default to avoid conflicts.