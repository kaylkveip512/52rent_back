from django.urls import path, include
from . import views

urlpatterns = [
    path('users/me/', views.ProfileMeView.as_view(), name='user-me'),
    path('users/', views.UserView.as_view(), name='users'),
    path('users/<int:pk>/', views.UserView.as_view(), name='user-detail'),
    path('cars/', views.CarView.as_view(), name='cars'),
    path('cars/<int:pk>/', views.CarView.as_view(), name='car-detail'),
    path('bookings/', views.BookingView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', views.BookingView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/confirm/', views.ConfirmBookingView.as_view(), name='confirm-booking'),
    path('users/<int:user_id>/bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
    path('support/', views.SupportRequestView.as_view(), name='support-requests'),
    path('support/<int:pk>/', views.SupportRequestView.as_view(), name='support-request-detail'),
    path('support/<int:request_id>/messages/', views.SupportMessageView.as_view(), name='support-messages'),
    path('pay/', include('payments.urls')),
]

