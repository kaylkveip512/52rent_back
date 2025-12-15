from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import User, Car, Booking, CarImage
from .serializers import UserSerializer, CarSerializer, BookingSerializer

logger = logging.getLogger(__name__)


class UserView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
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

    def put(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CarView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
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

    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PayView(APIView):

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
