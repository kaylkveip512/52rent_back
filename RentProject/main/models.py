from django.contrib.auth.models import User
from django.db import models

class Car(models.Model):
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    year = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='available')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    model = models.CharField(max_length=50, blank=True, null=True)

    transmission = models.CharField(
        max_length=20,
        choices=[('automatic', 'Автомат'), ('manual', 'Механіка')],
        default='automatic'
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ('gasoline', 'Бензин'),
            ('diesel', 'Дизель'),
            ('electric', 'Електро'),
            ('hybrid', 'Гібрид')
        ],
        default='gasoline'
    )

    category = models.CharField(
        max_length=20,
        choices=[
            ('economy', 'Економ'),
            ('comfort', 'Комфорт'),
            ('business', 'Бізнес'),
            ('suv', 'SUV'),
            ('premium', 'Преміум')
        ],
        default='economy'
    )

    seats = models.IntegerField(default=5)

    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year})"

class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cars/')

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id}: {self.car.name} - {self.status}"

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('renter', 'Renter'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='renter'
    )

    def __str__(self):
        return f'{self.user.username} ({self.role})'

class Order(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
