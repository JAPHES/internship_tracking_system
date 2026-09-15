from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.students.models import StudentProfile

from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "password",
            "is_active",
            "is_staff",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "full_name", "date_joined", "created_at", "updated_at"]

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        if not self.instance and not attrs.get("password"):
            raise serializers.ValidationError({"password": "This field is required."})
        if self.instance and "role" in attrs:
            new_role = attrs["role"]
            if hasattr(self.instance, "student_profile") and new_role != User.Role.STUDENT:
                raise serializers.ValidationError(
                    {"role": "Remove the student profile before changing this role."}
                )
            if hasattr(self.instance, "supervisor_profile") and new_role != User.Role.SUPERVISOR:
                raise serializers.ValidationError(
                    {"role": "Remove the supervisor profile before changing this role."}
                )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class StudentRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    registration_number = serializers.CharField(max_length=50)
    programme = serializers.CharField(max_length=150)
    department = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_email(self, value):
        normalized = value.lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        profile_fields = {
            key: validated_data.pop(key)
            for key in ("registration_number", "programme", "department", "phone_number")
            if key in validated_data
        }
        user = User.objects.create_user(role=User.Role.STUDENT, **validated_data)
        StudentProfile.objects.create(user=user, **profile_fields)
        return user

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("The current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        password_validation.validate_password(attrs["new_password"], self.context["request"].user)
        return attrs
