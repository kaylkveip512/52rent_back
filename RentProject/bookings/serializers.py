from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        # ЗМІНЕНО: Видаляємо 'graph_event_id'
        fields = ['id', 'user', 'item', 'start', 'end', 'status', 'created_at', 'updated_at']
        # ЗМІНЕНО: Видаляємо 'graph_event_id'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
