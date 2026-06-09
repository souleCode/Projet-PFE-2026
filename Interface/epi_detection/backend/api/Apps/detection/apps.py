from django.apps import AppConfig


class DetectionConfig(AppConfig):
    name = 'Apps.detection'

    def ready(self):
        import sys
        import os
        # Ignorer les commandes manage.py qui ne servent pas de requêtes
        argv = sys.argv
        if len(argv) > 1 and argv[1] in (
            'migrate', 'makemigrations', 'collectstatic',
            'check', 'test', 'createsuperuser', 'shell', 'dbshell',
        ):
            return
        # En mode runserver, charger seulement dans le process enfant (RUN_MAIN=true)
        if 'runserver' in argv and os.environ.get('RUN_MAIN') != 'true':
            return
        print("[YOLO] apps.py ready() — pré-chargement au démarrage du worker...")
        try:
            from .yolo_status import get_model
            get_model()
        except Exception as e:
            print(f"[YOLO] Erreur pré-chargement : {e}")
