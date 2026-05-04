from django.urls import path
from .views import (
    DetectView, DetectionLogListView,
    DetectionLogDetailView, DetectionStatsView, BusinessKPIsView,
    GeminiContextAnalysisListView, GeminiContextAnalysisProcessNextView,
)

urlpatterns = [
    path('detect/',       DetectView.as_view(),            name='detect'),
    path('logs/',         DetectionLogListView.as_view(),  name='detection_logs'),
    path('logs/<int:pk>/', DetectionLogDetailView.as_view(), name='detection_log_detail'),
    path('stats/',        DetectionStatsView.as_view(),    name='detection_stats'),
    path('business-kpis/', BusinessKPIsView.as_view(),     name='detection_business_kpis'),
    path('gemini-analyses/', GeminiContextAnalysisListView.as_view(), name='gemini_context_analysis_list'),
    path('gemini-analyses/process-next/', GeminiContextAnalysisProcessNextView.as_view(), name='gemini_context_analysis_process_next'),
]