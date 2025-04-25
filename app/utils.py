from typing import Dict, Any
from datetime import date, datetime
from app.models import Task
# Use direct calculation instead of pandas for stability
# import pandas as pd

def get_dashboard_metrics(user_id: int) -> Dict[str, Any]:
    """Generate dashboard metrics for the user's tasks."""
    # Get all active (non-archived) tasks for the user
    tasks = Task.query.filter_by(user_id=user_id, archived=False).all()
    
    if not tasks:
        return {
            "total": 0,
            "completed": 0,
            "completed_percent": 0,
            "overdue": 0,
            "pending": 0
        }
    
    # Calculate metrics directly without pandas
    today = date.today()
    total = len(tasks)
    
    # Count completed tasks
    completed = sum(1 for task in tasks if task.completed)
    completed_percent = int((completed / total) * 100) if total > 0 else 0
    
    # Count overdue tasks (not completed and due date is in the past)
    overdue = sum(1 for task in tasks if not task.completed and task.due_date and task.due_date < today)
    
    # Count pending tasks (not completed and not overdue)
    pending = total - completed - overdue
    
    # Print debug info to console
    print(f"Dashboard metrics: Total={total}, Completed={completed}, Overdue={overdue}, Pending={pending}")
    print(f"Today's date: {today}")
    for task in tasks:
        print(f"Task: {task.title}, Due: {task.due_date}, Completed: {task.completed}, Is overdue: {task.is_overdue}")
    
    return {
        "total": total,
        "completed": completed,
        "completed_percent": completed_percent,
        "overdue": overdue,
        "pending": pending
    }
