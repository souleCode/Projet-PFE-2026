from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, LogoutView, RegisterView,
    UserListView, UserDetailView, MeView, ChangePasswordView
)

urlpatterns = [
    # Auth
    path('login/',           LoginView.as_view(),          name='login'),
    path('logout/',          LogoutView.as_view(),          name='logout'),
    path('token/refresh/',   TokenRefreshView.as_view(),    name='token_refresh'),

    # Utilisateurs
    path('register/',        RegisterView.as_view(),        name='register'),
    path('',                 UserListView.as_view(),        name='user_list'),
    path('me/',              MeView.as_view(),              name='me'),
    path('change-password/', ChangePasswordView.as_view(),  name='change_password'),
    path('<int:pk>/',        UserDetailView.as_view(),      name='user_detail'),
]