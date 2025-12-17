from rest_framework import serializers
from .models import User, Car, Booking, CarImage, SupportRequest, SupportMessage

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ('id', 'image')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    renter_username = serializers.CharField(source='renter.username', read_only=True, allow_null=True)
    renter_email = serializers.CharField(source='renter.email', read_only=True, allow_null=True)
    car_name = serializers.SerializerMethodField()
    car_brand = serializers.SerializerMethodField()
    
    def get_car_name(self, obj):
        return obj.car.name if obj.car else None
    
    def get_car_brand(self, obj):
        return obj.car.brand if obj.car else None
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('renter', 'created_at', 'updated_at')

class SupportMessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = SupportMessage
        fields = '__all__'
        read_only_fields = ('author', 'is_from_admin', 'created_at')

class SupportRequestSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    messages = SupportMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportRequest
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
