from django.contrib import admin
from .models import Car, Booking, Order, CarImage

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "name", "year", "price_per_day", "status", "owner")
    list_filter = ("status", "brand", "year")
    search_fields = ("name", "brand", "location")
    ordering = ("id",)
    autocomplete_fields = ("owner",)

    fieldsets = (
        ("Основна інформація", {
            "fields": ("brand", "name", "year", "description")
        }),
        ("Розташування", {
            "fields": ("location",)
        }),
        ("Статус та власник", {
            "fields": ("status", "owner")
        }),
        ("Ціна", {
            "fields": ("price_per_day",)
        }),
    )

    inlines = [CarImageInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "renter", "start_date", "end_date", "status")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("car__name", "renter__username")
    ordering = ("-id",)
    autocomplete_fields = ("car", "renter")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "status")
    list_filter = ("status",)
