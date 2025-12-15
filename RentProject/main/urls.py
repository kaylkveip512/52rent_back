from django.urls import path, include
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view(), name='users'),
    path('users/<int:pk>/', views.UserView.as_view(), name='user-detail'),
    path('cars/', views.CarView.as_view(), name='cars'),
    path('cars/<int:pk>/', views.CarView.as_view(), name='car-detail'),
    path('bookings/', views.BookingView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', views.BookingView.as_view(), name='booking-detail'),
    path('pay/', include('payments.urls')),
]

