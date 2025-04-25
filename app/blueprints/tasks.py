from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from app.models import Task
from app.forms import TaskForm, TagForm
from app import db
from typing import Union, List
from datetime import date, datetime, time, timedelta

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
def index() -> str:
    """Home page - list all tasks for demo user."""
    user_id = 1  # Hardcoded for demo
    sort_by = request.args.get('sort', 'due_date')
    
    # Debug prints
    print("\n==== DEBUG TASK INDEX ====")
    print(f"User ID: {user_id}")
    print(f"Sort by: {sort_by}")
    
    # First let's check if we have tasks at all
    all_tasks = Task.query.filter_by(user_id=user_id).all()
    print(f"Total tasks in database: {len(all_tasks)}")
    print(f"All Tasks IDs: {[task.id for task in all_tasks]}")
    
    # Apply sorting
    if sort_by == 'title':
        order_clause = Task.title.asc()
    elif sort_by == 'status':
        order_clause = Task.completed.asc()
    elif sort_by == 'priority':
        # Sort by priority (high -> medium -> low -> none)
        order_clause = db.case(
            (Task.priority == 'high', 1),
            (Task.priority == 'medium', 2),
            (Task.priority == 'low', 3),
            else_=4
        ).asc()
    else:  # Default to due_date
        order_clause = Task.due_date.asc()
    
    # Get active (non-archived) tasks
    active_tasks = Task.query.filter_by(
        user_id=user_id, 
        archived=False
    ).order_by(order_clause).all()
    
    # Fix any null or missing values that could cause template errors
    for task in active_tasks:
        if task.priority is None:
            task.priority = 'none'
        if task.tags is None:
            task.tags = ''
        # Important - convert the due_date to a 2025 date if it exists
        if task.due_date and task.due_date.year != 2025:
            # Convert to a 2025 date with the same month and day
            try:
                month = task.due_date.month
                day = task.due_date.day
                # Create a new date object with the 2025 year
                task.due_date = date(2025, month, day)
            except Exception as e:
                print(f"Error converting date for task {task.id}: {e}")
    
    # Debug prints
    print(f"Active tasks count: {len(active_tasks)}")
    for task in active_tasks:
        print(f"Task: {task.id} - {task.title} - Due: {task.due_date}")
    
    # Get archived tasks
    archived_tasks = Task.query.filter_by(
        user_id=user_id, 
        archived=True
    ).order_by(Task.archived_at.desc()).all()
    
    # Calculate today and tomorrow for badge display
    # Use 2025 as our demo year to match reset_db.py
    year = 2025
    month = date.today().month
    day = date.today().day
    
    today = date(year, month, day)
    tomorrow = today + timedelta(days=1)
    
    # More debug prints
    print(f"Today: {today}")
    print(f"Tomorrow: {tomorrow}")
    print("==== END DEBUG ====\n")
    
    show_archived = request.args.get('show_archived', type=bool, default=False)
    
    return render_template(
        'index.html', 
        tasks=active_tasks, 
        archived_tasks=archived_tasks,
        show_archived=show_archived,
        today=today,
        tomorrow=tomorrow
    )

@tasks_bp.route('/task/new', methods=['GET', 'POST'])
def create_task() -> Union[str, redirect]:
    """Create a new task."""
    form = TaskForm()
    if form.validate_on_submit():
        # Create a datetime combining the date and time
        due_datetime = None
        if form.due_date.data:
            due_time = form.due_time.data or time(23, 59)
            due_datetime = datetime.combine(form.due_date.data, due_time)
            
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            tags=form.tags.data,
            user_id=1  # Hardcoded for demo
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.index'))
    return render_template('task_form.html', form=form, title='New Task')

@tasks_bp.route('/task/<int:task_id>')
def task_detail(task_id: int) -> str:
    """Display task details."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    # For tag management
    tag_form = TagForm()
    
    return render_template('task_detail.html', task=task, tag_form=tag_form)

@tasks_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id: int) -> Union[str, redirect]:
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    # Prevent editing completed tasks
    if task.completed:
        flash('Completed tasks cannot be edited.', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    
    # For existing tasks, we need to preserve the original due date if it's in the past
    original_due_date = task.due_date
    
    form = TaskForm(obj=task)
    
    # Special handling for tasks with past due dates
    if request.method == 'GET' and original_due_date and original_due_date < date.today():
        form.due_date.data = original_due_date  # Preserve the original date for display
    
    if form.validate_on_submit():
        # If the due date was changed, ensure it's not in the past
        if form.due_date.data != original_due_date and form.due_date.data and form.due_date.data < date.today():
            form.due_date.errors.append('Due date cannot be in the past. Please select a future date.')
            return render_template('task_form.html', form=form, title='Edit Task')
        
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.tags = form.tags.data
        task.completed = form.completed.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    
    return render_template('task_form.html', form=form, title='Edit Task')

@tasks_bp.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id: int) -> redirect:
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id: int) -> redirect:
    """Toggle task completion status."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    task.completed = not task.completed
    db.session.commit()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'task_id': task.id,
            'completed': task.completed
        })
    
    return redirect(request.referrer or url_for('tasks.index'))

@tasks_bp.route('/task/<int:task_id>/archive', methods=['GET', 'POST'])
def archive_task(task_id: int) -> redirect:
    """Archive a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    task.archive()
    db.session.commit()
    flash('Task archived successfully!', 'success')
    
    return redirect(request.referrer or url_for('tasks.index'))

@tasks_bp.route('/task/<int:task_id>/unarchive', methods=['POST'])
def unarchive_task(task_id: int) -> redirect:
    """Unarchive a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    task.unarchive()
    db.session.commit()
    flash('Task unarchived successfully!', 'success')
    
    return redirect(request.referrer or url_for('tasks.index'))

@tasks_bp.route('/task/<int:task_id>/set_priority/<priority>', methods=['POST'])
def set_priority(task_id: int, priority: str) -> redirect:
    """Set task priority."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    if priority not in ['high', 'medium', 'low', 'none']:
        abort(400)
    
    task.priority = None if priority == 'none' else priority
    db.session.commit()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'task_id': task.id,
            'priority': task.priority
        })
    
    return redirect(request.referrer or url_for('tasks.index'))

@tasks_bp.route('/task/<int:task_id>/add_tag', methods=['POST'])
def add_tag(task_id: int) -> redirect:
    """Add a tag to a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    form = TagForm()
    if form.validate_on_submit():
        task.add_tag(form.name.data)
        db.session.commit()
        flash(f'Tag "{form.name.data}" added!', 'success')
    
    return redirect(url_for('tasks.task_detail', task_id=task.id))

@tasks_bp.route('/task/<int:task_id>/remove_tag/<tag>', methods=['POST'])
def remove_tag(task_id: int, tag: str) -> redirect:
    """Remove a tag from a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != 1:  # Hardcoded for demo
        abort(403)
    
    task.remove_tag(tag)
    db.session.commit()
    flash(f'Tag "{tag}" removed!', 'success')
    
    return redirect(url_for('tasks.task_detail', task_id=task.id))

@tasks_bp.route('/batch_action', methods=['POST'])
def batch_action() -> redirect:
    """Handle batch actions on multiple tasks."""
    action = request.form.get('action')
    task_ids = request.form.getlist('task_ids')
    
    if not action or not task_ids:
        flash('No action or tasks selected.', 'warning')
        return redirect(url_for('tasks.index'))
    
    tasks = Task.query.filter(Task.id.in_(task_ids), Task.user_id==1).all()
    
    if action == 'complete':
        for task in tasks:
            task.completed = True
        flash(f'{len(tasks)} tasks marked as completed!', 'success')
    
    elif action == 'archive':
        for task in tasks:
            task.archive()
        flash(f'{len(tasks)} tasks archived!', 'success')
    
    elif action == 'delete':
        for task in tasks:
            db.session.delete(task)
        flash(f'{len(tasks)} tasks deleted!', 'success')
    
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/debug')
@tasks_bp.route('/tasks/debug')
@tasks_bp.route('/debug-tasks')
def debug_tasks() -> str:
    """Debug route to see all tasks directly."""
    user_id = 1  # Hardcoded for demo
    
    # Get all tasks
    all_tasks = Task.query.filter_by(user_id=user_id).all()
    
    # Create a simple string representation for debugging
    task_list = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Tasks</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
    """
    
    task_list += "<h1>All Tasks (Debug View)</h1>"
    task_list += f"<p>Found {len(all_tasks)} tasks for user_id {user_id}</p>"
    
    # Add database information
    import sqlite3
    import os
    from flask import current_app
    
    db_path = os.path.join(os.getcwd(), 'tasks.db')
    instance_db_path = os.path.join(os.getcwd(), 'instance', 'tasks.db')
    
    task_list += f"<p>Current directory: {os.getcwd()}</p>"
    task_list += f"<p>Direct DB path: {db_path} (exists: {os.path.exists(db_path)})</p>"
    task_list += f"<p>Instance DB path: {instance_db_path} (exists: {os.path.exists(instance_db_path)})</p>"
    task_list += f"<p>Database URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}</p>"
    
    # Add all routes information
    task_list += "<h2>Application Routes</h2>"
    task_list += "<ul>"
    for rule in current_app.url_map.iter_rules():
        task_list += f"<li>{rule.endpoint}: {rule}</li>"
    task_list += "</ul>"
    
    # Add table headers
    task_list += """
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Due Date</th>
                <th>Priority</th>
                <th>Tags</th>
                <th>Completed</th>
                <th>Archived</th>
                <th>Created</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Add each task as a row
    for task in all_tasks:
        task_list += f"""
        <tr>
            <td>{task.id}</td>
            <td>{task.title}</td>
            <td>{task.description or ''}</td>
            <td>{task.due_date}</td>
            <td>{task.priority or 'None'}</td>
            <td>{task.tags or ''}</td>
            <td>{task.completed}</td>
            <td>{task.archived}</td>
            <td>{task.created_at}</td>
        </tr>
        """
    
    # Close the table
    task_list += """
        </tbody>
    </table>
    """
    
    # Add links
    task_list += """
    <div style="margin-top: 20px;">
        <a href='/' style="margin-right: 10px;">Go to Home</a>
        <a href='/dashboard/'>Go to Dashboard</a>
    </div>
    """
    
    # Close the HTML
    task_list += """
    </body>
    </html>
    """
    
    return task_list

@tasks_bp.route('/app-debug')
def app_debug() -> str:
    """Debug version of the main app route with date issues fixed."""
    user_id = 1  # Hardcoded for demo
    sort_by = request.args.get('sort', 'due_date')
    
    print("\n==== DEBUG APP ====")
    
    # Get active (non-archived) tasks
    active_tasks = Task.query.filter_by(
        user_id=user_id, 
        archived=False
    ).all()
    
    # Fix any null or missing values that could cause template errors
    for task in active_tasks:
        if task.priority is None:
            task.priority = 'none'
        if task.tags is None:
            task.tags = ''
        # Important - convert the due_date to a 2025 date if it exists
        if task.due_date:
            # Convert to a 2025 date with the same month and day
            task.due_date = date(2025, task.due_date.month, task.due_date.day)
    
    # Get archived tasks
    archived_tasks = Task.query.filter_by(
        user_id=user_id, 
        archived=True
    ).all()
    
    # Use 2025 as our demo year to match reset_db.py
    year = 2025
    month = date.today().month
    day = date.today().day
    
    today = date(year, month, day)
    tomorrow = today + timedelta(days=1)
    
    print(f"Today (debug): {today}")
    for task in active_tasks:
        print(f"Task (debug): {task.id} - {task.title} - Due: {task.due_date}")
    
    print("==== END DEBUG APP ====\n")
    
    show_archived = request.args.get('show_archived', type=bool, default=False)
    
    # Use a special flag to indicate we're in debug mode
    return render_template(
        'index.html', 
        tasks=active_tasks, 
        archived_tasks=archived_tasks,
        show_archived=show_archived,
        today=today,
        tomorrow=tomorrow,
        app_debug=True
    )
