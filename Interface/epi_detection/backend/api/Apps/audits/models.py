from django.db import models
from Apps.Cameras.models import Camera
from Apps.alertes.models import Alert
from Apps.Users.models import User


class Audit(models.Model):
    STATUS_CHOICES = [
        ('ouvert',   'Ouvert'),
        ('en_cours', 'En cours'),
        ('clos',     'Clos'),
    ]

    title       = models.CharField(max_length=200)
    camera      = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, related_name='audits')
    alert       = models.ForeignKey(Alert,  on_delete=models.SET_NULL, null=True, blank=True, related_name='audits')
    created_by  = models.ForeignKey(User,   on_delete=models.SET_NULL, null=True, related_name='created_audits')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ouvert')
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Audit'
        verbose_name_plural = 'Audits'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.status}] - {self.created_at:%Y-%m-%d}"


class AuditCapture(models.Model):
    """Capture d'écran attachée à un audit"""
    audit       = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='captures')
    image       = models.ImageField(upload_to='audits/captures/')
    description = models.CharField(max_length=300, blank=True)
    taken_at    = models.DateTimeField(auto_now_add=True)
    taken_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captures')

    class Meta:
        verbose_name = 'Capture d\'audit'
        verbose_name_plural = 'Captures d\'audit'
        ordering = ['-taken_at']

    def __str__(self):
        return f"Capture #{self.id} - {self.audit.title} ({self.taken_at:%Y-%m-%d %H:%M})"