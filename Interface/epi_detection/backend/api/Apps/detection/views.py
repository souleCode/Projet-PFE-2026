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
from Apps.RegleSHE.models import HSERule
from Apps.alertes.models import Alert
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
        excluded_incident_classes = {'person'}
        for log in qs.filter(is_compliant=False):
            # Supposons que detections_json est une liste de dicts avec 'class' ou 'epi' pour l'EPI manquant
            for det in log.detections_json:
                if det.get('status') == 'missing_epi':
                    epi = det.get('class') or det.get('epi')
                    if epi and epi not in excluded_incident_classes:
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


class BusinessKPIsView(APIView):
    """
    GET /api/detection/business-kpis/
    KPIs métier avancés pour le reporting.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _average_minutes(durations):
        if not durations:
            return 0.0
        return round(sum(durations) / len(durations), 1)

    @staticmethod
    def _build_recurrence_stats(items):
        total_alerts = sum(items.values())
        repeated_alerts = sum(max(count - 1, 0) for count in items.values())
        overall_rate = round((repeated_alerts / total_alerts) * 100, 1) if total_alerts else 0.0
        breakdown = []

        for name, count in sorted(items.items(), key=lambda entry: entry[1], reverse=True):
            repeated = max(count - 1, 0)
            breakdown.append({
                'name': name,
                'total_alerts': count,
                'repeat_alerts': repeated,
                'recurrence_rate': round((repeated / count) * 100, 1) if count else 0.0,
            })

        return overall_rate, breakdown[:10]

    def get(self, request):
        alerts = Alert.objects.select_related('camera').all()
        logs = DetectionLog.objects.select_related('camera').all()
        active_rules = HSERule.objects.filter(is_active=True).prefetch_related('cameras')

        mtta_samples = [
            (alert.first_acknowledged_at - alert.timestamp).total_seconds() / 60
            for alert in alerts
            if alert.first_acknowledged_at
        ]
        mttr_samples = [
            (alert.resolved_at - alert.timestamp).total_seconds() / 60
            for alert in alerts
            if alert.resolved_at
        ]

        camera_alerts = {}
        zone_alerts = {}
        for alert in alerts:
            camera_name = alert.camera.name if alert.camera else 'Caméra inconnue'
            zone_name = alert.camera.location if alert.camera and alert.camera.location else 'Zone inconnue'
            camera_alerts[camera_name] = camera_alerts.get(camera_name, 0) + 1
            zone_alerts[zone_name] = zone_alerts.get(zone_name, 0) + 1

        overall_camera_recurrence_rate, recurrence_by_camera = self._build_recurrence_stats(camera_alerts)
        overall_zone_recurrence_rate, recurrence_by_zone = self._build_recurrence_stats(zone_alerts)

        hour_buckets = {
            hour: {'hour': hour, 'label': f'{hour:02d}h', 'total': 0, 'compliant': 0}
            for hour in range(24)
        }
        for log in logs:
            local_hour = timezone.localtime(log.timestamp).hour
            hour_buckets[local_hour]['total'] += 1
            if log.is_compliant:
                hour_buckets[local_hour]['compliant'] += 1

        compliance_by_hour = []
        for hour in range(24):
            bucket = hour_buckets[hour]
            total = bucket['total']
            compliant = bucket['compliant']
            compliance_by_hour.append({
                **bucket,
                'compliance_rate': round((compliant / total) * 100, 1) if total else 0.0,
            })

        camera_to_rules = {}
        for rule in active_rules:
            for camera_id in rule.cameras.values_list('id', flat=True):
                camera_to_rules.setdefault(camera_id, []).append(rule)

        rule_totals = {
            rule.id: {
                'rule_id': rule.id,
                'rule_name': rule.name,
                'camera_count': rule.cameras.count(),
                'total': 0,
                'compliant': 0,
            }
            for rule in active_rules
        }

        for log in logs:
            if not log.camera_id:
                continue
            for rule in camera_to_rules.get(log.camera_id, []):
                rule_totals[rule.id]['total'] += 1
                if log.is_compliant:
                    rule_totals[rule.id]['compliant'] += 1

        compliance_by_rule = []
        for rule_data in sorted(rule_totals.values(), key=lambda item: item['rule_name'].lower()):
            total = rule_data['total']
            compliant = rule_data['compliant']
            compliance_by_rule.append({
                **rule_data,
                'compliance_rate': round((compliant / total) * 100, 1) if total else 0.0,
            })

        return Response({
            'mtta_minutes': self._average_minutes(mtta_samples),
            'mttr_minutes': self._average_minutes(mttr_samples),
            'overall_camera_recurrence_rate': overall_camera_recurrence_rate,
            'overall_zone_recurrence_rate': overall_zone_recurrence_rate,
            'recurrence_by_camera': recurrence_by_camera,
            'recurrence_by_zone': recurrence_by_zone,
            'compliance_by_hour': compliance_by_hour,
            'compliance_by_rule': compliance_by_rule,
        })