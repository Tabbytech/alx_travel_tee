
from django.contrib import admin
from .models import Listing, Booking

class ListingAdmin(admin.ModelAdmin):
    list_display=('name','location', 'pricepernight', 'created_at', 'updated_at')
    list_filter=('name','location', 'pricepernight', 'created_at', 'updated_at')
    search_fields=('name','location', 'pricepernight', 'created_at', 'updated_at')
    odering=('name','location', 'pricepernight', 'created_at', 'updated_at')

class BookingAdmin(admin.ModelAdmin):
    list_display=('property','user', 'start_date', 'total_price', 'status', 'created_at')
    list_filter=('property','user', 'start_date', 'total_price', 'status', 'created_at')
    search_fields=('property','user', 'start_date', 'total_price', 'status', 'created_at')
    odering=('property','user', 'start_date', 'total_price', 'status', 'created_at')

admin.site.register(Listing, ListingAdmin)
admin.site.register(Booking, BookingAdmin)
