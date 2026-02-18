from rest_framework import serializers
from .models import DetectionLog


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