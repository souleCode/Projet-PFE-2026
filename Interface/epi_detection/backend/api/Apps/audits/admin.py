from django.contrib import admin
from .models import Audit, AuditCapture


class AuditCaptureInline(admin.TabularInline):
    model       = AuditCapture
    extra       = 0
    readonly_fields = ['taken_at', 'taken_by']
    fields      = ['image', 'description', 'taken_by', 'taken_at']


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display    = ['id', 'title', 'camera', 'status', 'created_by', 'created_at']
    list_filter     = ['status', 'camera']
    search_fields   = ['title', 'notes', 'camera__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering        = ['-created_at']
    inlines         = [AuditCaptureInline]

    fieldsets = (
        ('Audit',      {'fields': ('title', 'camera', 'alert', 'status')}),
        ('Détails',    {'fields': ('notes',)}),
        ('Métadonnées',{'fields': ('created_by', 'created_at', 'updated_at')}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AuditCapture)
class AuditCaptureAdmin(admin.ModelAdmin):
    list_display  = ['id', 'audit', 'taken_by', 'taken_at', 'description']
    list_filter   = ['audit']
    readonly_fields = ['taken_at']