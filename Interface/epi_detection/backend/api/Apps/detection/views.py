from PIL import Image
import io

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
from .yolo_status import run_detection_with_status



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
            detections, stats = run_detection_with_status(image)
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

        # Créer une alerte si EPI manquants
        if not is_compliant and camera:
            create_alert_if_needed(
                camera      = camera,
                missing_epi = stats.get('missing_epi', []),
                image_file  = file,
                detection_log = log,
            )

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

        return Response({
            'total':          total,
            'compliant':      compliant,
            'non_compliant':  non_compliant,
            'compliance_rate': rate,
        })