from datetime import date

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Users


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = [
            "last_login",
            "is_admin",
            "is_superuser",
            "groups",
            "user_permissions",
        ]

    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        password = value

        if len(password) < 8:
            raise serializers.ValidationError("Must have at least 8 chars.")

        password256 = make_password(password=password)

        return password256


class IssueCertificateSerializer(serializers.Serializer):
    cpf = serializers.CharField(required=True)
    student_name = serializers.CharField(required=True)
    course = serializers.CharField(required=True)
    course_description = serializers.CharField(required=True)
    certificate_description = serializers.CharField(required=True)
    issue_date = serializers.DateField(required=True)
    course_workload = serializers.IntegerField(required=True)

    def validate_cpf(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("CPF must have 11 digits")

        if not value.isdigit():
            raise serializers.ValidationError("CPF must have just numeric digits")

        return value

    def validate_student_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Student name must have at least 2 chars."
            )
        return value

    def validate_course(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Course name must have at least 3 chars.")

        return value

    def validate_course_description(self, value):
        if len(value) < 24:
            raise serializers.ValidationError(
                "Course description must have at least 24 chars."
            )

        return value

    def validate_certificate_description(self, value):
        if len(value) < 24:
            raise serializers.ValidationError(
                "Certificate description must have at least 24 chars."
            )

        return value

    def validate_issue_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Issue date must be a past date.")

        return value

    def validate_course_workload(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Course workload must be a positive integer."
            )

        return value
