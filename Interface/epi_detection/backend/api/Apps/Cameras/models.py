from django.db import models


class Camera(models.Model):
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('inactive',  'Inactive'),
        ('error',     'Erreur'),
    ]

    name        = models.CharField(max_length=100)
    location    = models.CharField(max_length=200)
    stream_url  = models.CharField(max_length=500, blank=True, null=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Caméra'
        verbose_name_plural = 'Caméras'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.location} ({self.status})"