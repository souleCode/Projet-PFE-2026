from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer,
    UpdateUserSerializer, ChangePasswordSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsAdminOrSuperviseur, IsOwnerOrAdmin


def set_auth_cookies(response, access_token, refresh_token=None):
    """Helper : pose les cookies JWT sur la réponse."""
    secure   = getattr(settings, 'JWT_AUTH_COOKIE_SECURE',   not settings.DEBUG)
    httponly = getattr(settings, 'JWT_AUTH_COOKIE_HTTPONLY',  True)
    samesite = getattr(settings, 'JWT_AUTH_COOKIE_SAMESITE',  'Lax')

    access_lifetime  = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

    response.set_cookie(
        key      = settings.JWT_AUTH_COOKIE,
        value    = str(access_token),
        max_age  = int(access_lifetime.total_seconds()),
        httponly = httponly,
        secure   = secure,
        samesite = samesite,
    )
    if refresh_token:
        response.set_cookie(
            key      = settings.JWT_AUTH_REFRESH_COOKIE,
            value    = str(refresh_token),
            max_age  = int(refresh_lifetime.total_seconds()),
            httponly = httponly,
            secure   = secure,
            samesite = samesite,
        )
    return response


def delete_auth_cookies(response):
    """Helper : supprime les cookies JWT."""
    response.delete_cookie(settings.JWT_AUTH_COOKIE)
    response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE)
    return response


# ===================== Auth===================

class LoginView(APIView):
    """
    POST /api/users/login/
    Body: { "email": "...", "password": "..." }
    Pose access_token + refresh_token en cookies HttpOnly.
    """
    permission_classes = []

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data          = serializer.validated_data
        access_token  = data['access']
        refresh_token = data['refresh']

        response = Response({
            'user':    data['user'],
            'detail':  'Connexion réussie.',
        }, status=status.HTTP_200_OK)

        set_auth_cookies(response, access_token, refresh_token)
        return response


class LogoutView(APIView):
    """
    POST /api/users/logout/
    Blackliste le refresh token et supprime les cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)
        response = Response({'detail': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        delete_auth_cookies(response)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token déjà expiré/blacklisté, on ignore

        return response


class RefreshTokenView(APIView):
    """
    POST /api/users/token/refresh/
    Renouvelle l'access token depuis le cookie refresh.
    """
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)

        if not refresh_token:
            return Response({'detail': 'Refresh token manquant.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token        = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({'detail': 'Token renouvelé.'}, status=status.HTTP_200_OK)
        set_auth_cookies(response, access_token)  # Pas besoin de reposer le refresh
        return response


# =============== Utilisateurs =====================

class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/  →  Admin seulement"""
    serializer_class   = RegisterSerializer
    permission_classes = [IsAdmin]


class UserListView(generics.ListAPIView):
    """GET /api/users/"""
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrSuperviseur]
    queryset           = User.objects.all().order_by('-created_at')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/users/<id>/"""
    queryset           = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateUserSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            return Response(
                {'detail': 'Vous ne pouvez pas supprimer votre propre compte.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/users/me/"""
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Log des cookies reçus pour debug
        import logging
        logger = logging.getLogger("django.request")
        logger.info(f"Cookies reçus sur /api/users/me/ : {self.request.COOKIES}")
        return self.request.user


class ChangePasswordView(APIView):
    """POST /api/users/change-password/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        # Forcer une reconnexion après changement de mot de passe
        response = Response({'detail': 'Mot de passe modifié. Veuillez vous reconnecter.'})
        delete_auth_cookies(response)
        return response