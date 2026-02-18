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