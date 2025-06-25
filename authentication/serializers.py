from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Member
from .validators import (
    validate_email_format,
    validate_password_strength,
    validate_required_field
)

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_staff']


# Signup Serializer
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password']

    def validate_email(self, value):
        return validate_email_format(validate_required_field(value, "email"))

    def validate_password(self, value):
        return validate_password_strength(validate_required_field(value, "password"))

    def validate_full_name(self, value):
        return validate_required_field(value, "full_name")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name']
        )
        return user


# Organization Serializer
class OrganizationSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'created_by', 'created_at']

    def validate_name(self, value):
        return validate_required_field(value, "name")


# Member Serializer
class MemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = Member
        fields = ['id', 'user', 'organization', 'is_admin', 'joined_at']

    def validate(self, data):
        validate_required_field(data.get("user"), "user")
        validate_required_field(data.get("organization"), "organization")
        return data
