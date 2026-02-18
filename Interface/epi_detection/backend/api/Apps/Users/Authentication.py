from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Lit le JWT depuis le cookie HttpOnly 'access_token'
    au lieu du header Authorization: Bearer <token>
    """

    def authenticate(self, request):
        import logging
        logger = logging.getLogger("django.request")
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', 'access_token')
        raw_token = request.COOKIES.get(cookie_name)
        if raw_token is None:
            logger.warning("[AUTH] Aucun cookie d'authentification trouvé.")
            return None  # Pas de cookie → anonyme

        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError as e:
            logger.error(f"[AUTH] Token JWT invalide : {e}")
            raise InvalidToken(e.args[0])
        return self.get_user(validated_token), validated_token