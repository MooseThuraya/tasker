import pytest
from app import create_app, db
from app.models import User, Task

@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_home_page(client):
    """Test that home page loads and contains task list."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Your Tasks' in response.data
    
def test_dashboard_metrics_api(client):
    """Test that the metrics API returns expected keys."""
    response = client.get('/dashboard/api/metrics')
    assert response.status_code == 200
    
    data = response.json
    assert 'total' in data
    assert 'completed' in data
    assert 'completed_percent' in data
    assert 'overdue' in data