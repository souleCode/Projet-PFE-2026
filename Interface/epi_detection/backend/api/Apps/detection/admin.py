from django.contrib import admin
from .models import DetectionLog


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display    = ['id', 'camera', 'timestamp', 'is_compliant', 'processing_time']
    list_filter     = ['is_compliant', 'camera']
    search_fields   = ['camera__name']
    readonly_fields = ['camera', 'timestamp', 'detections_json', 'stats_json', 'is_compliant', 'processing_time']
    ordering        = ['-timestamp']