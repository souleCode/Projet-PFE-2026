from django.urls import path
from .views import (
    DetectView, DetectionLogListView,
    DetectionLogDetailView, DetectionStatsView
)

urlpatterns = [
    path('detect/',       DetectView.as_view(),            name='detect'),
    path('logs/',         DetectionLogListView.as_view(),  name='detection_logs'),
    path('logs/<int:pk>/', DetectionLogDetailView.as_view(), name='detection_log_detail'),
    path('stats/',        DetectionStatsView.as_view(),    name='detection_stats'),
]