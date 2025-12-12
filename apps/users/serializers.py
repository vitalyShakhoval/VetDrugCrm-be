from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rolepermissions.roles import assign_role

from .models import EmployeeProfile
from .roles import get_role_class, get_role_choices


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=get_role_choices(), required=False)

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'email', 'password', 'role']
    
    def create(self, validated_data):
       return EmployeeProfile.objects.create_user(**validated_data)
