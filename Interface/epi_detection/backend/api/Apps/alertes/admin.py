from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display    = ['id', 'camera', 'criticity', 'status', 'epi_missing', 'timestamp', 'assigned_to']
    list_filter     = ['status', 'criticity', 'camera']
    search_fields   = ['camera__name', 'notes']
    readonly_fields = ['timestamp', 'detection_log', 'resolved_at', 'resolved_by']
    ordering        = ['-timestamp']
    list_editable   = ['status']

    fieldsets = (
        ('Incident',     {'fields': ('camera', 'timestamp', 'epi_missing', 'criticity', 'image')}),
        ('Traitement',   {'fields': ('status', 'assigned_to', 'notes')}),
        ('Résolution',   {'fields': ('resolved_by', 'resolved_at')}),
        ('Lien détection', {'fields': ('detection_log',)}),
    )