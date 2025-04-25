from flask import Blueprint, render_template, jsonify
from app.utils import get_dashboard_metrics
from typing import Dict, Any, Union

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard() -> str:
    """Dashboard view with task metrics."""
    user_id = 1  # Hardcoded for demo
    metrics = get_dashboard_metrics(user_id)
    return render_template('dashboard.html', metrics=metrics)

@dashboard_bp.route('/api/metrics')
def metrics_api() -> Dict[str, Any]:
    """API endpoint for dashboard metrics."""
    user_id = 1  # Hardcoded for demo
    metrics = get_dashboard_metrics(user_id)
    return jsonify(metrics)
