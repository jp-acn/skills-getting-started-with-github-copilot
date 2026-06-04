import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # ensure not already signed up
    assert email not in activities[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_not_signed_up():
    activity = "Chess Club"
    email = "not_signed_up@mergington.edu"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400
