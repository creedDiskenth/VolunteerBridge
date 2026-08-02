from rest_framework import serializers
from .models import Organization
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Organization
from django.contrib.auth.hashers import check_password





class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }


class OrganizationRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "email",
            "password",
            "license",
            "phone",
            "category",
            "address",
            "description",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        organization = Organization(**validated_data)
        organization.save()
        return organization


class OrganizationTokenSerializer(TokenObtainPairSerializer):

    username_field = 'email'

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        try:
            organization = Organization.objects.get(
                email=email
            )

        except Organization.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid credentials"
            )


        if not check_password(password, organization.password):
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        if organization.status != "approved":
            raise serializers.ValidationError(
                "Organization is not approved yet"
            )

        refresh = RefreshToken()

        refresh["organization_id"] = organization.id
        refresh["organization_name"] = organization.name

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "email": organization.email,
                "category": organization.category,
                "verified": organization.verified,
                "status": organization.status,
    }
}