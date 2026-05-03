from rest_framework import serializers
from .models import Audit, AuditCapture


class AuditCaptureSerializer(serializers.ModelSerializer):
    taken_by_name = serializers.CharField(source='taken_by.full_name', read_only=True)
    image_url     = serializers.SerializerMethodField()

    class Meta:
        model  = AuditCapture
        fields = ['id', 'audit', 'image', 'image_url', 'description', 'taken_at', 'taken_by', 'taken_by_name']
        read_only_fields = ['id', 'taken_at', 'taken_by']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class AuditCaptureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AuditCapture
        fields = ['image', 'description']


class AuditSerializer(serializers.ModelSerializer):
    camera_name    = serializers.CharField(source='camera.name',          read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    alert_criticity = serializers.CharField(source='alert.criticity',      read_only=True)
    captures        = AuditCaptureSerializer(many=True, read_only=True)
    captures_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Audit
        fields = [
            'id', 'title', 'camera', 'camera_name',
            'alert', 'alert_criticity',
            'created_by', 'created_by_name',
            'status', 'notes',
            'captures', 'captures_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_captures_count(self, obj):
        return obj.captures.count()


class AuditCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Audit
        fields = ['title', 'camera', 'alert', 'notes']

    def validate(self, attrs):
        alert = attrs.get('alert')
        if not alert:
            return attrs

        has_active_audit = Audit.objects.filter(
            alert=alert,
            status__in=['ouvert', 'en_cours']
        ).exists()
        if has_active_audit:
            raise serializers.ValidationError(
                "Cette alerte a deja un audit actif. Cloturez l'audit en cours avant d'en ouvrir un nouveau."
            )

        return attrs


class AuditUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Audit
        fields = ['title', 'status', 'notes']