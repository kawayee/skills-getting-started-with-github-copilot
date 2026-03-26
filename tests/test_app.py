import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture

def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]


def test_signup_for_unknown_activity_404():
    # Arrange
    client = TestClient(app)
    activity = "Unknown Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "user@mergington.edu"})

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_participant_400():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_unregister_activity_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]


def test_unregister_unknown_activity_404():
    # Arrange
    client = TestClient(app)
    activity = "Unknown Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": "user@mergington.edu"})

    # Assert
    assert response.status_code == 404


def test_unregister_nonexistent_participant_404():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_root_redirects_to_static():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers.get("location") == "/static/index.html"
