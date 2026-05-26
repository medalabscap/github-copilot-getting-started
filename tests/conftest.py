"""
Pytest configuration and fixtures for API tests
"""

import pytest
from fastapi.testclient import TestClient
from src import app as app_module


@pytest.fixture
def client():
    """
    Create a TestClient instance for testing the FastAPI application.
    The TestClient allows making requests to the app without running a live server.
    
    This fixture also resets the activities dict before each test to ensure
    test isolation and prevent state leakage between tests.
    """
    # Store original activities state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the school basketball team for practice and league games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Develop soccer skills, play friendly matches, and stay active",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Work on acting, stagecraft, and theatrical performances",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["emma@mergington.edu", "harper@mergington.edu"]
        },
        "Science Explorers": {
            "description": "Conduct experiments and investigate scientific topics",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["eli@mergington.edu", "nora@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Tackle challenging problems and prepare for math competitions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["noah@mergington.edu", "sophia@mergington.edu"]
        }
    }
    
    # Reset the activities dict to original state
    app_module.activities.clear()
    app_module.activities.update({k: {**v, "participants": v["participants"].copy()} 
                                   for k, v in original_activities.items()})
    
    return TestClient(app_module.app)


@pytest.fixture
def sample_email():
    """A sample email for testing signup and removal operations"""
    return "testuser@mergington.edu"


@pytest.fixture
def nonexistent_activity():
    """Name of an activity that doesn't exist in the database"""
    return "Nonexistent Activity"


@pytest.fixture
def existing_activity():
    """Name of an activity that exists in the database"""
    return "Chess Club"


@pytest.fixture
def existing_participant():
    """Email of a participant already signed up for Chess Club"""
    return "michael@mergington.edu"
