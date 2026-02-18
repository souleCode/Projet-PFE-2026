from django.urls import path
from .views import (
    AuditListCreateView, AuditDetailView,
    AuditCaptureListCreateView, AuditCaptureDeleteView,
    AuditReportPDFView, AuditExportCSVView,
)

urlpatterns = [
    # Audits
    path('',                                    AuditListCreateView.as_view(),     name='audit_list_create'),
    path('export/',                             AuditExportCSVView.as_view(),      name='audit_export_csv'),
    path('<int:pk>/',                           AuditDetailView.as_view(),         name='audit_detail'),
    path('<int:pk>/report/',                    AuditReportPDFView.as_view(),      name='audit_report_pdf'),
    # Captures
    path('<int:audit_id>/captures/',            AuditCaptureListCreateView.as_view(), name='audit_captures'),
    path('<int:audit_id>/captures/<int:pk>/',   AuditCaptureDeleteView.as_view(),     name='audit_capture_delete'),
]