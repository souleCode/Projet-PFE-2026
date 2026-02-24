from rest_framework import generics, permissions
from .models import HSERule
from .serializers import HSERuleSerializer
from django.shortcuts import render
from .permissions import IsAdmin, IsAdminOrSuperviseur, IsOwnerOrAdmin

class HSERuleListCreateView(generics.ListCreateAPIView):
    queryset = HSERule.objects.all()
    serializer_class = HSERuleSerializer
    permission_classes = [permissions.IsAuthenticated]

class HSERuleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HSERule.objects.all()
    serializer_class = HSERuleSerializer
    permission_classes = [permissions.IsAuthenticated]


