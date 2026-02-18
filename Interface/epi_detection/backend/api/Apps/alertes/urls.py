from django.urls import path
from .views import (
    AlertListView, AlertDetailView,
    AlertUpdateView, AlertBulkUpdateView,
    AlertStatsView,
)

urlpatterns = [
    path('',              AlertListView.as_view(),       name='alert_list'),
    path('stats/',        AlertStatsView.as_view(),      name='alert_stats'),
    path('bulk/',         AlertBulkUpdateView.as_view(), name='alert_bulk_update'),
    path('<int:pk>/',     AlertDetailView.as_view(),     name='alert_detail'),
    path('<int:pk>/update/', AlertUpdateView.as_view(),  name='alert_update'),
]