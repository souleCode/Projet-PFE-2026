from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Camera
from .serializers import (
    CameraSerializer, CameraCreateSerializer,
    CameraUpdateSerializer, CameraStatusSerializer
)
from Apps.Users.permissions import IsAdmin, IsAdminOrSuperviseur


class CameraListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/cameras/        → Liste toutes les caméras
    POST /api/cameras/        → Crée une caméra (Admin seulement)
    """
    queryset = Camera.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CameraCreateSerializer
        return CameraSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        camera = serializer.save()
        return Response(
            CameraSerializer(camera).data,
            status=status.HTTP_201_CREATED
        )


class CameraDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/cameras/<id>/  → Détail caméra
    PATCH  /api/cameras/<id>/  → Modifier (Admin/Superviseur)
    DELETE /api/cameras/<id>/  → Supprimer (Admin seulement)
    """
    queryset = Camera.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CameraUpdateSerializer
        return CameraSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAdminOrSuperviseur()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # PATCH par défaut
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        camera = serializer.save()
        return Response(CameraSerializer(camera).data)


class CameraStatusView(APIView):
    """
    PATCH /api/cameras/<id>/status/
    Change uniquement le statut d'une caméra.
    Utilisé par le frontend pour signaler active/inactive/error.
    """
    permission_classes = [IsAdminOrSuperviseur]

    def patch(self, request, pk):
        try:
            camera = Camera.objects.get(pk=pk)
        except Camera.DoesNotExist:
            return Response({'detail': 'Caméra introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CameraStatusSerializer(camera, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CameraSerializer(camera).data)


class ActiveCamerasView(generics.ListAPIView):
    """
    GET /api/cameras/active/
    Retourne uniquement les caméras actives.
    Utile pour le dashboard et la détection.
    """
    serializer_class   = CameraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Camera.objects.filter(is_active=True, status='active')