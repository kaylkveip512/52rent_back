from django.contrib import admin
from .models import User, Car, Booking, Order, CarImage, SupportRequest, SupportMessage

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role")
    list_filter = ("role",)
    search_fields = ("username", "email")
    ordering = ("id",)


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

class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ("author", "is_from_admin", "created_at")
    fields = ("author", "message", "is_from_admin", "created_at")

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
    inlines = [SupportMessageInline]
    
    fieldsets = (
        ("Основна інформація", {
            "fields": ("user", "subject", "message", "status")
        }),
        ("Відповідь", {
            "fields": ("response",)
        }),
        ("Дата", {
            "fields": ("created_at", "updated_at")
        }),
    )

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "support_request", "author", "is_from_admin", "created_at")
    list_filter = ("is_from_admin", "created_at")
    search_fields = ("message", "author__username", "support_request__subject")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("support_request", "author")
