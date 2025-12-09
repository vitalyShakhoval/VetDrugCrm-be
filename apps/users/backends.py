from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class JWTAuthBackend(BaseBackend):
    def authenticate(self, request, token=None, **kwargs):
        jwt_authenticator = JWTAuthentication()
        try:
            validated_token = jwt_authenticator.get_validated_token(token)
            user_id = validated_token['user_id']
            return User.objects.get(id=user_id)
        except:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None