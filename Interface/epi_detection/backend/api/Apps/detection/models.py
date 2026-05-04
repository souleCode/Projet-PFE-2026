from django.db import models
from Apps.Cameras.models import Camera


class DetectionLog(models.Model):
    """Historique de chaque appel de détection"""
    camera          = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True, related_name='detection_logs')
    timestamp       = models.DateTimeField(auto_now_add=True)
    detections_json = models.JSONField(default=list)   # liste brute des détections
    stats_json      = models.JSONField(default=dict)   # stats (hardhat, vest, person, compliance…)
    is_compliant    = models.BooleanField(default=True)
    processing_time = models.FloatField(default=0.0)   # secondes

    class Meta:
        verbose_name = 'Log de détection'
        verbose_name_plural = 'Logs de détection'
        ordering = ['-timestamp']

    def __str__(self):
        cam = self.camera.name if self.camera else 'Inconnue'
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] Caméra {cam} - Conforme: {self.is_compliant}"


class NonComplianceState(models.Model):
    """Suivi de persistance d'une non-conformité sur une caméra donnée."""

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='non_compliance_states')
    person_key = models.CharField(max_length=64, blank=True, default='')
    signature = models.CharField(max_length=255)
    missing_epi = models.JSONField(default=list)
    last_known_bbox = models.JSONField(default=list, blank=True)
    first_detected_at = models.DateTimeField()
    last_detected_at = models.DateTimeField()
    last_seen_log = models.ForeignKey(
        'DetectionLog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracked_non_compliance_states',
    )
    is_active = models.BooleanField(default=True)
    queued_for_llm = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'État de non-conformité persistante'
        verbose_name_plural = 'États de non-conformité persistante'
        ordering = ['-last_detected_at']
        indexes = [
            models.Index(fields=['camera', 'signature', 'is_active']),
            models.Index(fields=['camera', 'person_key', 'is_active'], name='detection_n_camera__41abca_idx'),
        ]

    def __str__(self):
        cam = self.camera.name if self.camera else 'Inconnue'
        person = self.person_key or 'person-unknown'
        return f"{cam} - {person} - {self.signature} ({'active' if self.is_active else 'inactive'})"


class GeminiContextAnalysis(models.Model):
    STATUS_CHOICES = [
        ('queued', 'En file'),
        ('processing', 'En traitement'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
        ('quota_skipped', 'Quota dépassé'),
    ]

    ACTION_CHOICES = [
        ('ALERT', 'Alert'),
        ('MONITOR', 'Monitor'),
        ('OK', 'OK'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='gemini_analyses')
    alert = models.ForeignKey(
        'alertes.Alert',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gemini_analyses',
    )
    detection_log = models.ForeignKey(
        'DetectionLog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gemini_analyses',
    )
    non_compliance_state = models.ForeignKey(
        'NonComplianceState',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gemini_analyses',
    )
    image = models.ImageField(upload_to='gemini/context/', null=True, blank=True)
    missing_epi = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    request_reason = models.CharField(max_length=255, blank=True)
    prompt = models.TextField(blank=True)
    response_text = models.TextField(blank=True)
    result_json = models.JSONField(default=dict, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, blank=True)
    explanation = models.TextField(blank=True)
    llm_confidence = models.FloatField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Analyse contextuelle Gemini'
        verbose_name_plural = 'Analyses contextuelles Gemini'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', 'requested_at']),
            models.Index(fields=['camera', 'requested_at']),
        ]

    def __str__(self):
        cam = self.camera.name if self.camera else 'Inconnue'
        return f"Gemini {self.status} - {cam} - {self.requested_at:%Y-%m-%d %H:%M}"