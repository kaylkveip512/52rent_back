from django.urls import path
from .views import pay_order, liqpay_callback, create_payment_view

urlpatterns = [
    path('create/', create_payment_view, name='create-payment'),
    path('<int:order_id>/', pay_order, name='pay-order'),
    path('pay/callback/', liqpay_callback, name='liqpay-callback'),
]
