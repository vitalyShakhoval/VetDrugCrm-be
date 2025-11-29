from rest_framework import serializers
from .models import EmployeProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=EmployeProfile.USER_ROLES, required = False)
   
    class Meta:
        model = EmployeProfile
        fields = ['id', 'email', 'password', 'role']

    def create(self, validated_data):
        user = EmployeProfile.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'veterinarian')  # роль по умолчанию
        )
        return user