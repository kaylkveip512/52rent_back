import pytest
from main.models import Car

@pytest.mark.django_db
def test_create_car(auth_client, user):
    data = {
        "name": "Camry",
        "brand": "Toyota",
        "year": 2020,
        "price_per_day": 1000,
        "location": "Kyiv",
        "status": "available",
        "owner": user.id
    }

    response = auth_client.post("/main/cars/", data)
    assert response.status_code == 201
    assert Car.objects.count() == 1
