from django.urls import path, include
from . import views

urlpatterns = [
    path('users/me/', views.UserView.as_view(), name='user-me'),

    path('cars/', views.CarView.as_view(), name='cars'),
    path('cars/<int:pk>/', views.CarView.as_view(), name='car-detail'),

    path('bookings/', views.BookingView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', views.BookingView.as_view(), name='booking-detail'),

    path('payments/', include('payments.urls')),
]
