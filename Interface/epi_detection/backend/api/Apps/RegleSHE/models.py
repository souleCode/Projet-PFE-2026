from django.db import models
from django.contrib.postgres.fields import JSONField
from Apps.Cameras.models import Camera

class HSERule(models.Model):
    EPI_CHOICES = [
        ('hardhat', 'Casque'),
        ('safety_vest', 'Gilet'),
        ('mask', 'Masque'),
        ('gloves', 'Gants'),
        ('safety_glasses', 'Lunettes'),
        ('ear_protection', 'Protection auditive'),
        # Ajoute d'autres EPI si besoin
    ]

    name = models.CharField(max_length=100)
    # Ancien champ (à retirer plus tard si migration OK)
    epi_type = models.CharField(max_length=32, choices=EPI_CHOICES, blank=True, null=True)
    # Nouveau champ JSON pour la liste des EPI et leur criticité
    epi_criticites = models.JSONField(default=list, blank=True, help_text="Liste d'objets {epi: str, criticite: str}")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    cameras = models.ManyToManyField(Camera, blank=True, related_name='hse_rules')
    zone = models.CharField(max_length=100, blank=True)  # Optionnel : zone géographique

    def __str__(self):
        return f"{self.get_epi_type_display()} ({'Active' if self.is_active else 'Inactive'})"