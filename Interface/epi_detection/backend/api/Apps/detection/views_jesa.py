from PIL import Image
import io
from collections import Counter
from datetime import timedelta
from django.utils import timezone

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from Apps.Cameras.models import Camera
from Apps.alertes.utils import create_alert_if_needed   # branché sur alerts
from .models import DetectionLog
from .serializers import DetectionLogSerializer
from .yolo_status import run_detection_with_fusion



class DetectView(APIView):
    """
    POST /api/detection/detect/
    Body (multipart): file=<image>, camera_id=<int> (optionnel)

    - Lance YOLO sur l'image
    - Sauvegarde un DetectionLog
    - Si non conforme → crée une alerte automatiquement
    - Retourne les détections + stats
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

        # Charger l'image
        try:
            image = Image.open(io.BytesIO(file.read())).convert('RGB')
            import numpy as np
            import cv2
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        except Exception:
            return Response({'detail': 'Fichier image invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer la caméra si fournie
        camera = None
        camera_id = request.data.get('camera_id')
        if camera_id:
            try:
                camera = Camera.objects.get(pk=camera_id)
            except Camera.DoesNotExist:
                pass

        # Lancer la détection
        try:
            detections, stats = run_detection_with_fusion(image_bgr)
        except Exception as e:
            return Response({'detail': f'Erreur YOLO : {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        is_compliant = stats.get('compliance', True)

        # Sauvegarder le log
        log = DetectionLog.objects.create(
            camera          = camera,
            detections_json = detections,
            stats_json      = stats,
            is_compliant    = is_compliant,
            processing_time = stats.get('processingTime', 0.0),
        )

        # Créer une alerte si EPI manquants attendus par la règle HSE de la caméra
        if not is_compliant and camera:
            # Récupérer les EPI attendus pour cette caméra (via la règle HSE active)
            hse_rules = camera.hse_rules.filter(is_active=True)
            epis_attendus = set()
            for rule in hse_rules:
                for epi in rule.epi_criticites:
                    if isinstance(epi, dict):
                        epis_attendus.add(epi.get('epi'))
                    else:
                        epis_attendus.add(epi)
            missing_epi = [epi for epi in stats.get('missing_epi', []) if epi in epis_attendus]
            if missing_epi:
                create_alert_if_needed(
                    camera      = camera,
                    missing_epi = missing_epi,
                    image_file  = file,
                    detection_log = log,
                )

        # Harmoniser les couleurs selon le statut pour chaque détection
        for det in detections:
            if det.get('status') == 'detected':
                epi_status = det.get('epi_status')
                if epi_status:
                    # Pour les personnes, la couleur est déjà gérée
                    continue
                # Pour les EPI, on peut ajuster la couleur selon le statut si besoin
                # (optionnel, selon la logique de yolo_status.py)
            elif det.get('status') == 'missing_epi':
                det['color'] = '#ef4444'  # rouge
            elif det.get('status') == 'compliant':
                det['color'] = '#22c55e'  # vert
            # Ajoute d'autres statuts/couleurs si besoin

        return Response({
            'detections': detections,
            'stats':      stats,
            'log_id':     log.id,
        }, status=status.HTTP_200_OK)


class DetectionLogListView(generics.ListAPIView):
    """
    GET /api/detection/logs/
    Paramètres optionnels : ?camera_id=1  ?compliant=false  ?limit=50
    """
    serializer_class   = DetectionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = DetectionLog.objects.select_related('camera').all()

        camera_id = self.request.query_params.get('camera_id')
        if camera_id:
            qs = qs.filter(camera__id=camera_id)

        compliant = self.request.query_params.get('compliant')
        if compliant is not None:
            qs = qs.filter(is_compliant=compliant.lower() == 'true')

        limit = self.request.query_params.get('limit')
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass

        return qs


class DetectionLogDetailView(generics.RetrieveAPIView):
    """GET /api/detection/logs/<id>/"""
    serializer_class   = DetectionLogSerializer
    permission_classes = [IsAuthenticated]
    queryset           = DetectionLog.objects.select_related('camera').all()


class DetectionStatsView(APIView):
    """
    GET /api/detection/stats/
    Statistiques globales : total, conformes, non conformes, taux de conformité
    Paramètre optionnel : ?camera_id=1
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = DetectionLog.objects.all()
        camera_id = request.query_params.get('camera_id')
        if camera_id:
            qs = qs.filter(camera__id=camera_id)

        total        = qs.count()
        compliant    = qs.filter(is_compliant=True).count()
        non_compliant = total - compliant
        rate         = round((compliant / total * 100), 1) if total > 0 else 0.0

        # Incidents cette semaine (par jour)
        today = timezone.now().date()
        week_days = []
        for i in range(6, -1, -1):  # 6 jours avant aujourd'hui jusqu'à aujourd'hui
            day = today - timedelta(days=i)
            count = qs.filter(timestamp__date=day).count()
            week_days.append({
                "day": day.strftime("%a %d/%m"),
                "incidents": count
            })

        # Calcul des types d'incidents (exemple: EPI manquants)
        epi_counter = Counter()
        for log in qs.filter(is_compliant=False):
            # Supposons que detections_json est une liste de dicts avec 'class' ou 'epi' pour l'EPI manquant
            for det in log.detections_json:
                if det.get('status') == 'missing_epi':
                    epi = det.get('class') or det.get('epi')
                    if epi:
                        epi_counter[epi] += 1

        # Génère la liste pour le frontend
        total_incidents = sum(epi_counter.values())
        incident_types = []
        COLORS = ["#F87171", "#FBBF24", "#34D399", "#60A5FA", "#A78BFA", "#F472B6", "#F59E42"]
        for i, (epi, count) in enumerate(epi_counter.items()):
            percent = round((count / total_incidents) * 100, 1) if total_incidents else 0
            incident_types.append({
                "name": epi,
                "value": percent,
                "color": COLORS[i % len(COLORS)]
            })

        return Response({
            'total':          total,
            'compliant':      compliant,
            'non_compliant':  non_compliant,
            'compliance_rate': rate,
            'weekly_incidents': week_days,  # <-- Ajouté ici
            'incident_types': incident_types,  # <-- Ajouté ici
        })