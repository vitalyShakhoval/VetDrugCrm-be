from rest_framework import serializers
from .models import EmployeProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = EmployeProfile
        fields = ['id', 'email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = EmployeProfile(**validated_data)
        user.set_password(password)  
        user.save()
        return user