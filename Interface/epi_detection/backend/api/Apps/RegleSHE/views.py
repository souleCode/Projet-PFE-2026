from rest_framework import generics, permissions
from .models import HSERule
from .serializers import HSERuleSerializer
from .permissions import IsAdmin

class HSERuleListCreateView(generics.ListCreateAPIView):
    queryset = HSERule.objects.all()
    serializer_class = HSERuleSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

class HSERuleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HSERule.objects.all()
    serializer_class = HSERuleSerializer

    def get_permissions(self):
        if self.request.method in {'PUT', 'PATCH', 'DELETE'}:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


