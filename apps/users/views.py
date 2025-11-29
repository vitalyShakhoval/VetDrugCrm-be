from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import generics, status 
from .serializers import UserSerializer
from .models import EmployeProfile

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
            "message": "User registered successfully.",
            "user_id": user.id,
            "email": user.email
        }, status=status.HTTP_201_CREATED, headers=headers) 
