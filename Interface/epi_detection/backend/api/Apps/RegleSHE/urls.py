from django.urls import path
from .views import HSERuleListCreateView, HSERuleRetrieveUpdateDestroyView

urlpatterns = [
    path('hse-rules/', HSERuleListCreateView.as_view(), name='hse_rule_list_create'),
    path('hse-rules/<int:pk>/', HSERuleRetrieveUpdateDestroyView.as_view(), name='hse_rule_detail'),
]