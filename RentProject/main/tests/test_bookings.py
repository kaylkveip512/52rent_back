import pytest
from main.models import Car, Booking

@pytest.mark.django_db
def test_create_booking(auth_client, user):
    car = Car.objects.create(
        name="BMW",
        brand="BMW",
        year=2019,
        price_per_day=1500,
        location="Kyiv",
        status="available",
        owner_id=user.id
    )

    data = {
        "car": car.id,
        "start_date": "2025-12-20",
        "end_date": "2025-12-25",
        "status": "pending"
    }

    response = auth_client.post("/main/bookings/", data)
    assert response.status_code == 201
    assert Booking.objects.count() == 1
