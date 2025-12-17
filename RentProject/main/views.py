from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from datetime import timedelta
import logging

from .models import User, Car, Booking, CarImage, SupportRequest, SupportMessage
from .serializers import UserSerializer, CarSerializer, BookingSerializer, SupportRequestSerializer, SupportMessageSerializer

logger = logging.getLogger(__name__)

class ProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                from django.contrib.auth.models import User as AuthUser
                user = AuthUser.objects.get(pk=pk)
                return Response({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff
                })
            except AuthUser.DoesNotExist:
                return Response(
                    {"error": "Користувач не знайдено"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            if not request.user.is_staff:
                return Response(
                    {"error": "Немає доступу"},
                    status=status.HTTP_403_FORBIDDEN
                )
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
        if not pk:
            return Response(
                {"error": "ID користувача обов'язковий"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.is_staff and request.user.id != pk:
            return Response(
                {"error": "Немає доступу до цього профілю"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.contrib.auth.models import User as AuthUser
            user = AuthUser.objects.get(pk=pk)
        except AuthUser.DoesNotExist:
            return Response(
                {"error": "Користувач не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff
        })

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
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            conflicting_bookings = Booking.objects.filter(
                Q(start_date__lte=end_date) & Q(end_date__gte=start_date),
                status='confirmed'
            ).values_list('car_id', flat=True).distinct()

            cars = cars.exclude(id__in=conflicting_bookings)

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
        if request.user.is_staff:
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(renter=request.user)
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            car_id = request.data.get('car')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            if car_id and start_date and end_date:
                conflicting_bookings = Booking.objects.filter(
                    car_id=car_id,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    status='confirmed'
                ).exists()
                
                if conflicting_bookings:
                    return Response(
                        {"error": "Автомобіль вже заброньований на ці дати"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            booking = serializer.save(renter=request.user)
            days = (booking.end_date - booking.start_date).days or 1
            booking.total_price = days * booking.car.price_per_day
            booking.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Бронювання не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and booking.renter != request.user:
            return Response(
                {"error": "Немає доступу до цього бронювання"},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        
        if new_status == 'confirmed' and booking.status != 'confirmed':
            if not request.user.is_staff:
                return Response(
                    {"error": "Тільки адміністратор може підтверджувати бронювання"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            car_id = booking.car_id
            start_date = booking.start_date
            end_date = booking.end_date
            
            conflicting_bookings = Booking.objects.filter(
                car_id=car_id,
                start_date__lte=end_date,
                end_date__gte=start_date,
                status='confirmed'
            ).exclude(id=booking.id).exists()
            
            if conflicting_bookings:
                return Response(
                    {"error": "Неможливо підтвердити: автомобіль вже заброньований на ці дати"},
                    status=status.HTTP_400_BAD_REQUEST
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
                {"error": "Бронювання не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and booking.renter != request.user:
            return Response(
                {"error": "Немає доступу до цього бронювання"},
                status=status.HTTP_403_FORBIDDEN
            )

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "Тільки адміністратор може підтверджувати бронювання"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Бронювання не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if booking.status == 'confirmed':
            return Response(
                {"error": "Бронювання вже підтверджено"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status == 'cancelled':
            return Response(
                {"error": "Неможливо підтвердити скасоване бронювання"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        car_id = booking.car_id
        start_date = booking.start_date
        end_date = booking.end_date
        
        conflicting_bookings = Booking.objects.filter(
            car_id=car_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='confirmed'
        ).exclude(id=booking.id).exists()
        
        if conflicting_bookings:
            return Response(
                {"error": "Неможливо підтвердити: автомобіль вже заброньований на ці дати"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

class SupportRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            try:
                support_request = SupportRequest.objects.get(pk=pk)
            except SupportRequest.DoesNotExist:
                return Response(
                    {"error": "Запит не знайдено"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not request.user.is_staff and support_request.user != request.user:
                return Response(
                    {"error": "Немає доступу до цього запиту"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = SupportRequestSerializer(support_request)
            return Response(serializer.data)
        else:
            if request.user.is_staff:
                support_requests = SupportRequest.objects.all()
            else:
                support_requests = SupportRequest.objects.filter(user=request.user)
            
            serializer = SupportRequestSerializer(support_requests, many=True)
            return Response(serializer.data)
    
    def post(self, request):
        serializer = SupportRequestSerializer(data=request.data)
        if serializer.is_valid():
            support_request = serializer.save(user=request.user)
            return Response(
                SupportRequestSerializer(support_request).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        try:
            support_request = SupportRequest.objects.get(pk=pk)
        except SupportRequest.DoesNotExist:
            return Response(
                {"error": "Запит не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and support_request.user != request.user:
            return Response(
                {"error": "Немає доступу до цього запиту"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SupportRequestSerializer(
            support_request,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        try:
            support_request = SupportRequest.objects.get(pk=pk)
        except SupportRequest.DoesNotExist:
            return Response(
                {"error": "Запит не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and support_request.user != request.user:
            return Response(
                {"error": "Немає доступу до цього запиту"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        support_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SupportMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, request_id):
        try:
            support_request = SupportRequest.objects.get(pk=request_id)
        except SupportRequest.DoesNotExist:
            return Response(
                {"error": "Запит не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and support_request.user != request.user:
            return Response(
                {"error": "Немає доступу до цього запиту"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if support_request.status == 'closed':
            return Response(
                {"error": "Неможливо додати повідомлення до закритого запиту"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message_text = request.data.get('message', '').strip()
        if not message_text:
            return Response(
                {"error": "Повідомлення не може бути порожнім"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_from_admin = request.user.is_staff
        
        if is_from_admin and support_request.status == 'new':
            support_request.status = 'in_progress'
            support_request.save()
        
        support_message = SupportMessage.objects.create(
            support_request=support_request,
            author=request.user,
            message=message_text,
            is_from_admin=is_from_admin
        )
        
        support_request.updated_at = support_request.updated_at
        support_request.save()
        
        serializer = SupportMessageSerializer(support_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, request_id):
        try:
            support_request = SupportRequest.objects.get(pk=request_id)
        except SupportRequest.DoesNotExist:
            return Response(
                {"error": "Запит не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not request.user.is_staff and support_request.user != request.user:
            return Response(
                {"error": "Немає доступу до цього запиту"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = SupportMessage.objects.filter(support_request=support_request)
        serializer = SupportMessageSerializer(messages, many=True)
        return Response(serializer.data)

class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        if not request.user.is_staff:
            return Response(
                {"error": "Немає доступу"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.contrib.auth.models import User as AuthUser
            user = AuthUser.objects.get(pk=user_id)
        except AuthUser.DoesNotExist:
            return Response(
                {"error": "Користувач не знайдено"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        bookings = Booking.objects.filter(renter=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
