import csv
from io import StringIO

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from Apps.Users.permissions import IsAdminOrSuperviseur
from .models import Audit, AuditCapture
from .serializers import (
    AuditSerializer, AuditCreateSerializer, AuditUpdateSerializer,
    AuditCaptureSerializer, AuditCaptureCreateSerializer,
)
from .report import generate_audit_pdf


# ================== Audits ====================================

class AuditListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/audits/       → Liste des audits
    POST /api/audits/       → Créer un audit
    Filtres : ?status=ouvert  ?camera_id=1
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return AuditCreateSerializer if self.request.method == 'POST' else AuditSerializer

    def get_queryset(self):
        qs = Audit.objects.select_related(
            'camera', 'alert', 'created_by'
        ).prefetch_related('captures').all()

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        camera_id = self.request.query_params.get('camera_id')
        if camera_id:
            qs = qs.filter(camera__id=camera_id)

        alert_id = self.request.query_params.get('alert_id')
        if alert_id:
            qs = qs.filter(alert__id=alert_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        audit = serializer.instance
        return Response(
            AuditSerializer(audit, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class AuditDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/audits/<id>/  → Détail + captures
    PATCH  /api/audits/<id>/  → Modifier titre/statut/notes
    DELETE /api/audits/<id>/  → Supprimer (Admin seulement)
    """
    queryset = Audit.objects.select_related(
        'camera', 'alert', 'created_by'
    ).prefetch_related('captures').all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AuditUpdateSerializer
        return AuditSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminOrSuperviseur()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance  = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            AuditSerializer(instance, context={'request': request}).data
        )


# ================== Captures ==================================

class AuditCaptureListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/audits/<audit_id>/captures/  → Liste des captures
    POST /api/audits/<audit_id>/captures/  → Ajouter une capture (image)
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser]

    def get_audit(self):
        try:
            return Audit.objects.get(pk=self.kwargs['audit_id'])
        except Audit.DoesNotExist:
            return None

    def get_queryset(self):
        return AuditCapture.objects.filter(audit__id=self.kwargs['audit_id'])

    def get_serializer_class(self):
        return AuditCaptureCreateSerializer if self.request.method == 'POST' else AuditCaptureSerializer

    def create(self, request, *args, **kwargs):
        audit = self.get_audit()
        if not audit:
            return Response({'detail': 'Audit introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuditCaptureCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        capture = serializer.save(audit=audit, taken_by=request.user)
        return Response(
            AuditCaptureSerializer(capture, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class AuditCaptureDeleteView(generics.DestroyAPIView):
    """DELETE /api/audits/<audit_id>/captures/<pk>/"""
    permission_classes = [IsAdminOrSuperviseur]
    queryset           = AuditCapture.objects.all()


# ===================== Rapport PDF ==========================

class AuditReportPDFView(APIView):
    """
    GET /api/audits/<id>/report/
    Génère et retourne le rapport PDF de l'audit.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            audit = Audit.objects.select_related(
                'camera', 'alert', 'created_by'
            ).prefetch_related('captures__taken_by').get(pk=pk)
        except Audit.DoesNotExist:
            return Response({'detail': 'Audit introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        buffer   = generate_audit_pdf(audit)
        filename = f"audit_{audit.id}_{audit.created_at.strftime('%Y%m%d')}.pdf"

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ===================Export CSV ============================

class AuditExportCSVView(APIView):
    """
    GET /api/audits/export/
    Export CSV de tous les audits.
    """
    permission_classes = [IsAdminOrSuperviseur]

    def get(self, request):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ID', 'Titre', 'Caméra', 'Localisation',
            'Statut', 'Créé par', 'Date création',
            'Alerte liée', 'Criticité alerte', 'Nb captures', 'Notes'
        ])

        audits = Audit.objects.select_related(
            'camera', 'alert', 'created_by'
        ).prefetch_related('captures').all()

        for audit in audits:
            writer.writerow([
                audit.id,
                audit.title,
                audit.camera.name     if audit.camera     else '',
                audit.camera.location if audit.camera     else '',
                audit.status,
                audit.created_by.full_name if audit.created_by else '',
                audit.created_at.strftime('%Y-%m-%d %H:%M'),
                audit.alert.id        if audit.alert       else '',
                audit.alert.criticity if audit.alert       else '',
                audit.captures.count(),
                audit.notes,
            ])

        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audits.csv"'
        return response