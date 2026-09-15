from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import User

from .models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name", max_length=150)
    last_name = serializers.CharField(source="user.last_name", max_length=150)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user_id",
            "email",
            "first_name",
            "last_name",
            "password",
            "registration_number",
            "programme",
            "department",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_id", "created_at", "updated_at"]

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "This field is required."})
        if self.instance is not None and "password" in attrs:
            raise serializers.ValidationError(
                {"password": "Use the change-password endpoint to update a password."}
            )
        user_data = attrs.get("user", {})
        email = user_data.get("email")
        if email:
            existing = User.objects.filter(email__iexact=email)
            if self.instance:
                existing = existing.exclude(pk=self.instance.user_id)
            if existing.exists():
                raise serializers.ValidationError(
                    {"email": "A user with this email already exists."}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            role=User.Role.STUDENT,
            **user_data,
        )
        profile = StudentProfile(user=user, **validated_data)
        profile.full_clean()
        profile.save()
        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        validated_data.pop("password", None)
        for attribute, value in user_data.items():
            setattr(instance.user, attribute, value)
        instance.user.save()
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.full_clean()
        instance.save()
        return instance


class StudentSummarySerializer(StudentProfileSerializer):
    class Meta(StudentProfileSerializer.Meta):
        fields = [
            "id",
            "user_id",
            "email",
            "first_name",
            "last_name",
            "registration_number",
            "programme",
            "department",
            "phone_number",
        ]
        read_only_fields = fields
