from django.db import models
from Apps.Cameras.models import Camera
from Apps.Users.models import User


class Alert(models.Model):
    CRITICITY_CHOICES = [
        ('faible',  'Faible'),
        ('moyenne', 'Moyenne'),
        ('elevee',  'Élevée'),
    ]
    STATUS_CHOICES = [
        ('nouveau',   'Nouveau'),
        ('en_cours',  'En cours'),
        ('resolu',    'Résolu'),
        ('ignore',    'Ignoré'),
    ]

    camera          = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, related_name='alerts')
    timestamp       = models.DateTimeField(auto_now_add=True)
    epi_missing     = models.JSONField(default=list)        # ex: ["hardhat", "vest"]
    criticity       = models.CharField(max_length=20, choices=CRITICITY_CHOICES, default='moyenne')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nouveau')
    image           = models.ImageField(upload_to='alerts/', null=True, blank=True)
    detection_log   = models.OneToOneField(
        'detection.DetectionLog',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alert'
    )
    assigned_to     = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_alerts'
    )
    resolved_by     = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_alerts'
    )
    resolved_at     = models.DateTimeField(null=True, blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'
        ordering = ['-timestamp']

    def __str__(self):
        cam = self.camera.name if self.camera else 'Inconnue'
        return f"[{self.criticity.upper()}] {cam} - {self.timestamp:%Y-%m-%d %H:%M} - {self.status}"

    @property
    def epi_missing_display(self):
        labels = {'hardhat': 'Casque', 'vest': 'Gilet', 'glass': 'Lunettes'}
        return [labels.get(e, e) for e in self.epi_missing]