import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test that we can fetch all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_activity_structure():
    """Test that activity data has correct structure"""
    response = client.get("/activities")
    activities = response.json()
    activity = activities["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "test@example.com" in result["message"]

def test_signup_duplicate():
    """Test that duplicate signup is rejected"""
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for activity that doesn't exist"""
    response = client.post("/activities/Nonexistent Club/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    client.post("/activities/Tennis Club/signup?email=test2@example.com")
    # Then unregister
    response = client.delete("/activities/Tennis Club/unregister?email=test2@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]

def test_unregister_nonexistent_participant():
    """Test unregistering someone not signed up"""
    response = client.delete("/activities/Tennis Club/unregister?email=notregistered@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]