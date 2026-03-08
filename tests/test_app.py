"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_root_redirect(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self):
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    def test_signup_for_activity_success(self):
        response = client.post("/activities/Drama Society/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Drama Society" in data["message"]

    def test_signup_nonexistent_activity(self):
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_participant(self):
        # First signup
        client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        # Try to signup again
        response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"


class TestUnregisterEndpoint:
    def test_unregister_success(self):
        email = "unregister_test@mergington.edu"
        # First sign up
        client.post(f"/activities/Art Club/signup?email={email}")
        # Then unregister
        response = client.delete(f"/activities/Art Club/participants/{email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_nonexistent_activity(self):
        response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_student_not_in_activity(self):
        response = client.delete("/activities/Science Club/participants/notinthisactivity@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found"