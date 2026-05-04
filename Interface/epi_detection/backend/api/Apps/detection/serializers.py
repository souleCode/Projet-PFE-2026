from django.utils import timezone
from rest_framework import serializers
from .models import DetectionLog, GeminiContextAnalysis, NonComplianceState


class DetectionLogSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)

    class Meta:
        model  = DetectionLog
        fields = [
            'id', 'camera', 'camera_name', 'timestamp',
            'detections_json', 'stats_json',
            'is_compliant', 'processing_time'
        ]
        read_only_fields = fields


class NonComplianceStateSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)

    class Meta:
        model = NonComplianceState
        fields = [
            'id', 'camera', 'camera_name', 'person_key', 'signature', 'missing_epi', 'last_known_bbox',
            'first_detected_at', 'last_detected_at', 'is_active', 'queued_for_llm', 'resolved_at',
        ]
        read_only_fields = fields


class GeminiContextAnalysisSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    alert_id = serializers.IntegerField(source='alert.id', read_only=True)
    image_url = serializers.SerializerMethodField()
    retry_in_seconds = serializers.SerializerMethodField()

    class Meta:
        model = GeminiContextAnalysis
        fields = [
            'id', 'camera', 'camera_name', 'alert', 'alert_id', 'detection_log', 'non_compliance_state',
            'status', 'missing_epi', 'request_reason', 'image_url', 'severity', 'action',
            'explanation', 'llm_confidence', 'result_json', 'error_message',
            'requested_at', 'started_at', 'next_retry_at', 'retry_in_seconds', 'processed_at',
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        image_field = obj.image or (obj.alert.image if obj.alert and obj.alert.image else None)
        if not image_field:
            return None

        image_url = image_field.url
        if image_url.startswith('http://') or image_url.startswith('https://'):
            return image_url

        if request:
            return request.build_absolute_uri(image_url)

        return image_url

    def get_retry_in_seconds(self, obj):
        if not obj.next_retry_at:
            return None

        remaining = int((obj.next_retry_at - timezone.now()).total_seconds())
        return max(0, remaining)