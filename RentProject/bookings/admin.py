from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'item',
        'start',
        'end',
        'duration_days',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at', 'start', 'end')
    search_fields = ('user__username', 'user__email', 'item')
    readonly_fields = ('created_at', 'updated_at') 
    autocomplete_fields = ('user',)

    fieldsets = (
        ("User & Item", {
            "fields": ("user", "item")
        }),
        ("Booking timeframe", {
            "fields": ("start", "end")
        }),
        ("Status", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def duration_days(self, obj):
        delta = obj.end - obj.start
        return delta.days
