from django.urls import path
from .views import BookingListCreateView, BookingDetailView


urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking_list_create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
]
