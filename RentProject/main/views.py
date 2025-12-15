from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from .models import User, Car, Booking, CarImage
from .serializers import UserSerializer, CarSerializer, BookingSerializer

logger = logging.getLogger(__name__)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CarView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            car = Car.objects.get(pk=pk)
            serializer = CarSerializer(car)
        else:
            cars = Car.objects.all()
            serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            car = serializer.save(owner=request.user)

            images = request.FILES.getlist('images')
            for image in images:
                CarImage.objects.create(car=car, image=image)

            return Response(
                CarSerializer(car).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(renter=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(renter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        booking = Booking.objects.get(pk=pk, renter=request.user)
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = Booking.objects.get(pk=pk, renter=request.user)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")

        if not order_id or not amount:
            return Response(
                {"error": "order_id and amount are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = create_payment(order_id, amount)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Payment error: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
