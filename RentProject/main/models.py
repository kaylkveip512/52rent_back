from django.db import models

class Order(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"Order #{self.id}"

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('renter', 'Renter'),
    ]
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='renter')

    def __str__(self):
        return f"{self.username} ({self.role})"

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
    renter = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='car_bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.id}: {self.car.name} - {self.status}"

class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('in_progress', 'В обробці'),
        ('resolved', 'Вирішено'),
        ('closed', 'Закрито'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='support_requests')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запит в підтримку'
        verbose_name_plural = 'Запити в підтримку'
    
    def __str__(self):
        return f"Запит #{self.id}: {self.subject} ({self.get_status_display()})"

class SupportMessage(models.Model):
    support_request = models.ForeignKey(SupportRequest, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='support_messages')
    message = models.TextField()
    is_from_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Повідомлення підтримки'
        verbose_name_plural = 'Повідомлення підтримки'
    
    def __str__(self):
        return f"Повідомлення #{self.id} до запиту #{self.support_request.id}"
