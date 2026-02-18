from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from Apps.Users.permissions import IsAdminOrSuperviseur
from .models import Alert
from .serializers import AlertSerializer, AlertUpdateSerializer, AlertStatsSerializer


class AlertListView(generics.ListAPIView):
    """
    GET /api/alerts/
    Filtres : ?status=nouveau  ?criticity=elevee
              ?camera_id=1     ?search=casque
    """
    serializer_class   = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Alert.objects.select_related(
            'camera', 'assigned_to', 'resolved_by', 'detection_log'
        ).all()

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        criticity = self.request.query_params.get('criticity')
        if criticity:
            qs = qs.filter(criticity=criticity)

        camera_id = self.request.query_params.get('camera_id')
        if camera_id:
            qs = qs.filter(camera__id=camera_id)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(camera__name__icontains=search) |
                Q(notes__icontains=search)
            )

        return qs


class AlertDetailView(generics.RetrieveAPIView):
    """GET /api/alerts/<id>/"""
    serializer_class   = AlertSerializer
    permission_classes = [IsAuthenticated]
    queryset           = Alert.objects.select_related(
        'camera', 'assigned_to', 'resolved_by'
    ).all()


class AlertUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/alerts/<id>/
    Changer statut, assigner un utilisateur, ajouter des notes.
    """
    serializer_class   = AlertUpdateSerializer
    permission_classes = [IsAdminOrSuperviseur]
    queryset           = Alert.objects.all()
    http_method_names  = ['patch']

    def perform_update(self, serializer):
        data = {}

        # Si on passe en résolu → enregistrer qui a résolu et quand
        if serializer.validated_data.get('status') == 'resolu':
            data['resolved_by'] = self.request.user
            data['resolved_at'] = timezone.now()

        serializer.save(**data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Retourner l'alerte complète après mise à jour
        alert = self.get_object()
        return Response(
            AlertSerializer(alert, context={'request': request}).data
        )


class AlertBulkUpdateView(APIView):
    """
    PATCH /api/alerts/bulk/
    Body: { "ids": [1,2,3], "status": "resolu" }
    Mettre à jour plusieurs alertes d'un coup.
    """
    permission_classes = [IsAdminOrSuperviseur]

    def patch(self, request):
        ids    = request.data.get('ids', [])
        new_status = request.data.get('status')

        if not ids or not new_status:
            return Response(
                {'detail': 'ids et status sont obligatoires.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alerts = Alert.objects.filter(id__in=ids)
        update_data = {'status': new_status}

        if new_status == 'resolu':
            update_data['resolved_by'] = request.user
            update_data['resolved_at'] = timezone.now()

        updated = alerts.update(**update_data)
        return Response({'detail': f'{updated} alerte(s) mise(s) à jour.'})


class AlertStatsView(APIView):
    """
    GET /api/alerts/stats/
    Statistiques des alertes : par statut, par criticité.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Alert.objects.all()

        camera_id = request.query_params.get('camera_id')
        if camera_id:
            qs = qs.filter(camera__id=camera_id)

        stats = {
            'total':    qs.count(),
            'nouveau':  qs.filter(status='nouveau').count(),
            'en_cours': qs.filter(status='en_cours').count(),
            'resolu':   qs.filter(status='resolu').count(),
            'faible':   qs.filter(criticity='faible').count(),
            'moyenne':  qs.filter(criticity='moyenne').count(),
            'elevee':   qs.filter(criticity='elevee').count(),
        }

        serializer = AlertStatsSerializer(stats)
        return Response(serializer.data)