from django.apps import AppConfig


class DetectionConfig(AppConfig):
    name = 'Apps.detection'

    def ready(self):
        import sys
        # Ne pas charger YOLO lors des commandes manage.py (migrate, check, etc.)
        if 'manage.py' in sys.argv[0]:
            return
        try:
            from .yolo_status import get_model
            get_model()
        except Exception as e:
            print(f"[YOLO] Avertissement : impossible de pré-charger le modèle : {e}")
