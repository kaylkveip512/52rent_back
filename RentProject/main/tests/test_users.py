import pytest

@pytest.mark.django_db
def test_get_current_user(auth_client):
    response = auth_client.get("/main/users/me/")
    assert response.status_code == 200
    assert response.data["username"] == "testuser"
