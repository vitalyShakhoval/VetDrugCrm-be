from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import generics, status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .serializers import UserSerializer
from .models import EmployeProfile
from .mixins import RoleRequiredMixin, PermissionRequiredMixin
from .roles import *

class RegisterView(generics.CreateAPIView):
  
    queryset = EmployeProfile.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
       
        return Response({
            "message": "Регистрация пользователя прошла успешно",
            "user_id": user.id,
            "email": user.email,
            'role': user.role
        }, status=status.HTTP_201_CREATED, headers=headers) 
    

class ProtectedView(RoleRequiredMixin,APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    required_role_class = Manager
    
    def get(self, request):
        user = request.user
        return Response({
            "message": "This is a protected endpoint by manager",
            "user_id": user.id,
            "username": user.email,
            "is_authenticated": user.is_authenticated,
            'role': user.role,
            'data': 'Ваши защищенные данные здесь'
        })