from django.contrib import admin
from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display   = ['name', 'location', 'status', 'is_active', 'created_at']
    list_filter    = ['status', 'is_active']
    search_fields  = ['name', 'location']
    ordering       = ['-created_at']
    list_editable  = ['status', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations',  {'fields': ('name', 'location', 'stream_url')}),
        ('État',          {'fields': ('status', 'is_active')}),
        ('Dates',         {'fields': ('created_at', 'updated_at')}),
    )