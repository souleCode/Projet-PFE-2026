from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    camera_name        = serializers.CharField(source='camera.name',         read_only=True)
    camera_location    = serializers.CharField(source='camera.location',      read_only=True)
    assigned_to_name   = serializers.CharField(source='assigned_to.full_name', read_only=True)
    resolved_by_name   = serializers.CharField(source='resolved_by.full_name', read_only=True)
    epi_missing_display = serializers.ReadOnlyField()
    image_url          = serializers.SerializerMethodField()

    class Meta:
        model  = Alert
        fields = [
            'id', 'camera', 'camera_name', 'camera_location',
            'timestamp', 'epi_missing', 'epi_missing_display',
            'criticity', 'status', 'image', 'image_url',
            'detection_log', 'assigned_to', 'assigned_to_name',
            'resolved_by', 'resolved_by_name', 'resolved_at', 'notes',
        ]
        read_only_fields = ['id', 'timestamp', 'detection_log']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class AlertUpdateSerializer(serializers.ModelSerializer):
    """Pour PATCH : changer statut, assigner, ajouter notes"""
    class Meta:
        model  = Alert
        fields = ['status', 'assigned_to', 'notes']

    def validate_status(self, value):
        allowed = ['nouveau', 'en_cours', 'resolu', 'ignore']
        if value not in allowed:
            raise serializers.ValidationError(f"Statut invalide. Valeurs acceptées : {allowed}")
        return value


class AlertStatsSerializer(serializers.Serializer):
    total        = serializers.IntegerField()
    nouveau      = serializers.IntegerField()
    en_cours     = serializers.IntegerField()
    resolu       = serializers.IntegerField()
    faible       = serializers.IntegerField()
    moyenne      = serializers.IntegerField()
    elevee       = serializers.IntegerField()