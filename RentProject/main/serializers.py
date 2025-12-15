from rest_framework import serializers
from .models import User, Car, Booking, CarImage, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ('id', 'image')

class BookingSerializer(serializers.ModelSerializer):
    renter = serializers.ReadOnlyField(source='renter.username')

    class Meta:
        model = Booking
        fields = ['id', 'car', 'renter', 'start_date', 'end_date', 'status']
        read_only_fields = ['id', 'renter']
