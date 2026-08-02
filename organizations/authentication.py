from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from accounts.models import User
from .models import Organization


class OrganizationJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        header = self.get_header(request)

        if header is None:
            return None

        raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        # ========= User =========
        user_id = validated_token.get("user_id")

        if user_id is not None:
            try:
                user = User.objects.get(id=user_id)
                return (user, validated_token)

            except User.DoesNotExist:
                raise AuthenticationFailed("User not found.")

        # ========= Organization =========
        organization_id = validated_token.get("organization_id")

        if organization_id is not None:
            try:
                organization = Organization.objects.get(
                    id=organization_id,
                    status="approved",
                    verified=True
                )

                return (organization, validated_token)

            except Organization.DoesNotExist:
                raise AuthenticationFailed(
                    "Organization not found."
                )

        raise AuthenticationFailed("Invalid token.")