"""
Unit tests for the Mergington High School API endpoints
Tests cover all endpoints with success and error cases
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is a dictionary
        assert isinstance(data, dict)
        
        # Verify all expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Studio",
            "Drama Club",
            "Science Explorers",
            "Math Olympiad"
        ]
        for activity in expected_activities:
            assert activity in data
        
        # Verify structure of each activity
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_participants(self, client):
        """Test that activities include current participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have at least the pre-loaded participants
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) > 0
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client, existing_activity, sample_email):
        """Test successful signup for an activity"""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert existing_activity in data["message"]
        
        # Verify participant was added
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert sample_email in activities[existing_activity]["participants"]

    def test_signup_for_activity_nonexistent_activity(self, client, sample_email, nonexistent_activity):
        """Test signup fails for nonexistent activity"""
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_fails(self, client, existing_activity, existing_participant):
        """Test that duplicate signup fails"""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_activities(self, client, sample_email):
        """Test that same user can sign up for multiple activities"""
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert sample_email in activities["Chess Club"]["participants"]
        assert sample_email in activities["Programming Class"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client, existing_activity, existing_participant):
        """Test successful removal of a participant"""
        response = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": existing_participant}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_participant in data["message"]
        assert existing_activity in data["message"]
        
        # Verify participant was removed
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert existing_participant not in activities[existing_activity]["participants"]

    def test_remove_participant_nonexistent_activity(self, client, sample_email, nonexistent_activity):
        """Test removal fails for nonexistent activity"""
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant(self, client, existing_activity, sample_email):
        """Test removal fails for participant not in activity"""
        response = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_then_signup_again(self, client, existing_activity, sample_email):
        """Test that user can sign up again after being removed"""
        # First signup
        response1 = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Remove participant
        response2 = client.delete(
            f"/activities/{existing_activity}/participants",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Sign up again - should succeed
        response3 = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200


class TestEdgeCases:
    """Tests for edge cases and integration scenarios"""

    def test_special_characters_in_email(self, client, existing_activity):
        """Test signup with email containing special characters"""
        special_email = "test+123@mergington.edu"
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": special_email}
        )
        
        # Should succeed - FastAPI doesn't validate email format by default
        assert response.status_code == 200
        
        # Verify it was added
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert special_email in activities[existing_activity]["participants"]

    def test_case_sensitive_activity_names(self, client, sample_email):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": sample_email}
        )
        
        # Should fail because activity names are case-sensitive
        assert response.status_code == 404

    def test_activity_data_not_modified_by_get(self, client, existing_activity):
        """Test that multiple GET requests don't modify activity data"""
        response1 = client.get("/activities")
        data1 = response1.json()
        participants1 = data1[existing_activity]["participants"].copy()
        
        response2 = client.get("/activities")
        data2 = response2.json()
        participants2 = data2[existing_activity]["participants"]
        
        # Participants list should be identical
        assert participants1 == participants2

    def test_empty_email_parameter(self, client, existing_activity):
        """Test signup with empty email parameter"""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": ""}
        )
        
        # Empty string is still technically valid, gets added as participant
        # This tests current behavior - could be changed with email validation
        assert response.status_code == 200
        
        # Verify it was added
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert "" in activities[existing_activity]["participants"]
