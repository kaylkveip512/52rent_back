from django.shortcuts import redirect
from main.models import Order
from .liqpay_service import create_payment
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
import base64, json
from rest_framework import status
import json

from main.models import Booking

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_view(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        amount = data.get('amount')
        description = data.get('description', 'Оренда автомобіля')
        
        if not order_id or not amount:
            return Response(
                {"error": "order_id та amount обов'язкові"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order, created = Order.objects.get_or_create(
            id=order_id,
            defaults={'amount': amount, 'status': 'pending'}
        )
        
        if not created:
            order.amount = amount
            order.save()
        
        payment_data = create_payment(order.id, float(amount))
        
        return Response(payment_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def pay_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse(content="Order not found", status=404)

    url = create_payment(order.id, float(order.amount))

    return redirect(url["payment_url"])


@csrf_exempt
def liqpay_callback(request):
    print("CALLBACK HIT")

    data = request.POST.get('data')
    signature = request.POST.get('signature')

    if not data and request.body:
        try:
            body = request.body.decode()
            parsed = dict(x.split('=') for x in body.split('&'))
            data = parsed.get('data')
            signature = parsed.get('signature')
            print("DATA FROM BODY")
        except Exception as e:
            print("BODY PARSE ERROR:", e)

    if not data:
        print("NO DATA AT ALL")
        return HttpResponse('NO DATA', status=400)

    decoded_data = base64.b64decode(data).decode('utf-8')
    payment_data = json.loads(decoded_data)

    print("PAYMENT DATA:", payment_data)

    status = payment_data.get('status')
    order_id = payment_data.get('order_id')

    if status not in ('success', 'sandbox'):
        print("IGNORED STATUS:", status)
        return HttpResponse('IGNORED', status=200)

    try:
        booking = Booking.objects.get(id=order_id)
    except Booking.DoesNotExist:
        print("BOOKING NOT FOUND:", order_id)
        return HttpResponse('BOOKING NOT FOUND', status=404)

    booking.status = 'confirmed'
    booking.save()

    send_mail(
        subject='Ваше бронювання підтверджено',
        message=(
            f'Авто: {booking.car.name}\n'
            f'Період: {booking.start_date} – {booking.end_date}\n'
            f'Сума: {booking.total_price} грн'
        ),
        from_email='noreply@52rent.com',
        recipient_list=[booking.renter.email],
        fail_silently=False,
    )

    print("EMAIL SENT TO:", booking.renter.email)

    return HttpResponse('OK')
