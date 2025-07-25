"""
Sample tests for the Employee API endpoints.
"""
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_employees_empty(client):
    response = client.get('/employees')
    assert response.status_code == 200
    assert response.json == [] 