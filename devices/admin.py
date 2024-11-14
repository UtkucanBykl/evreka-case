from django.contrib import admin
from devices.models import Device, Location, LocationDailySummary


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Location) 
class LocationAdmin(admin.ModelAdmin):
    list_display = ('device', 'latitude', 'longitude', 'speed', 'timestamp')
    list_filter = ('device', 'timestamp')
    search_fields = ('device__name',)
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(LocationDailySummary)
class LocationDailySummaryAdmin(admin.ModelAdmin):
    list_display = ('device', 'summary_day', 'max_speed')
    list_filter = ('device', 'summary_day')
    search_fields = ('device__name',)
    readonly_fields = ('first_location', 'last_location', 'max_speed_location')
    ordering = ('-summary_day',)
    date_hierarchy = 'summary_day'
