from django.urls import path
from .views import (
    DetectView, DetectionLogListView,
    DetectionLogDetailView, DetectionStatsView, BusinessKPIsView
)

urlpatterns = [
    path('detect/',       DetectView.as_view(),            name='detect'),
    path('logs/',         DetectionLogListView.as_view(),  name='detection_logs'),
    path('logs/<int:pk>/', DetectionLogDetailView.as_view(), name='detection_log_detail'),
    path('stats/',        DetectionStatsView.as_view(),    name='detection_stats'),
    path('business-kpis/', BusinessKPIsView.as_view(),     name='detection_business_kpis'),
]