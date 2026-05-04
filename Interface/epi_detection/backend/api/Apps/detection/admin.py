from django.contrib import admin
from .models import DetectionLog, GeminiContextAnalysis, NonComplianceState


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display    = ['id', 'camera', 'timestamp', 'is_compliant', 'processing_time']
    list_filter     = ['is_compliant', 'camera']
    search_fields   = ['camera__name']
    readonly_fields = ['camera', 'timestamp', 'detections_json', 'stats_json', 'is_compliant', 'processing_time']
    ordering        = ['-timestamp']


@admin.register(NonComplianceState)
class NonComplianceStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'camera', 'person_key', 'signature', 'first_detected_at', 'last_detected_at', 'is_active', 'queued_for_llm']
    list_filter = ['is_active', 'queued_for_llm', 'camera']
    search_fields = ['camera__name', 'person_key', 'signature']
    readonly_fields = ['camera', 'person_key', 'signature', 'missing_epi', 'last_known_bbox', 'first_detected_at', 'last_detected_at', 'last_seen_log', 'resolved_at']


@admin.register(GeminiContextAnalysis)
class GeminiContextAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'camera', 'status', 'severity', 'action', 'requested_at', 'processed_at']
    list_filter = ['status', 'severity', 'action', 'camera']
    search_fields = ['camera__name', 'request_reason', 'explanation']
    readonly_fields = [
        'camera', 'alert', 'detection_log', 'non_compliance_state', 'image', 'missing_epi',
        'request_reason', 'prompt', 'response_text', 'result_json', 'severity', 'action',
        'explanation', 'llm_confidence', 'requested_at', 'started_at', 'processed_at', 'error_message',
    ]