from django.urls import path
from .views import (
    CameraListCreateView, CameraDetailView,
    CameraStatusView, ActiveCamerasView
)

urlpatterns = [
    path('',              CameraListCreateView.as_view(), name='camera_list_create'),
    path('active/',       ActiveCamerasView.as_view(),    name='camera_active'),
    path('<int:pk>/',     CameraDetailView.as_view(),     name='camera_detail'),
    path('<int:pk>/status/', CameraStatusView.as_view(),  name='camera_status'),
]