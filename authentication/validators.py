from rest_framework import serializers
import re

def validate_required_field(value, field_name):
    if not value:
        raise serializers.ValidationError({field_name: f"{field_name.capitalize()} is required."})
    return value


def validate_email_format(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise serializers.ValidationError({"email": "Enter a valid email address."})
    return email


def validate_password_strength(password):
    if len(password) < 6:
        raise serializers.ValidationError({"password": "Password must be at least 6 characters long."})
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        raise serializers.ValidationError({"password": "Password must contain both letters and numbers."})
    return password
