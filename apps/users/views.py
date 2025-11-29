from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import generics, status 
from .serializers import UserSerializer
from .models import EmployeProfile
from rest_framework.views import APIView
from .premissions import IsManager,IsVeterinarian,IsWarehouseSupervisor


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
            "email": user.email
        }, status=status.HTTP_201_CREATED, headers=headers) 


class ManagerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        return Response({
            "message": "Панель менеджера",
            "user": request.user.email,
            "role": request.user.role,
            "available_actions": [
                "Главная (дашборд)",
                "Управление пользователями", 
                "Настройки уведомлений",
                "Журнал действий",
                "Отчёты",
            ]
        })


class WarehouseDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseSupervisor]
    
    def get(self, request):
        return Response({
            "message": "Управление складом",
            "user": request.user.email,
            "role": request.user.role,
            "available_actions": [
                "Каталог препаратов",
                "Партии (приёмка)",
                "Инвентаризация"
            ]
        })


class VeterinarianDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsVeterinarian]
    
    def get(self, request):
        return Response({
            "message": "Панель ветеринара", 
            "user": request.user.email,
            "role": request.user.role,
            "available_actions": [
                "Выдача препарата",
                "Возврат",
                "История операций"
            ]
        })
    

    