from rest_framework.permissions import BasePermission
from organizations.models import Organization



class IsAdminOrSupervisorOrOrganization(BasePermission):

    def has_permission(self, request, view):

        # مؤسسة
        if request.auth:

            organization_id = request.auth.get(
                "organization_id"
            )

            if organization_id:

                try:
                    organization = Organization.objects.get(
                        id=organization_id
                    )

                    return (
                        organization.status == "approved"
                        and organization.verified
                    )

                except Organization.DoesNotExist:
                    return False


        # مستخدم عادي (admin/supervisor)
        if (
            request.user.is_authenticated
            and request.user.role in [
                "admin",
                "supervisor"
            ]
        ):
            return True


        return False

class IsOrganization(BasePermission):

    def has_permission(self, request, view):

        if not request.auth:
            return False

        organization_id = request.auth.get(
            "organization_id"
        )

        if not organization_id:
            return False

        try:
            organization = Organization.objects.get(
                id=organization_id
            )

            return (
                organization.status == "approved"
                and organization.verified
            )

        except Organization.DoesNotExist:
            return False



class IsAdminOrSupervisor(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in ["admin", "supervisor"]
        )





class IsOrganizationOrAdminSupervisor(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        # الأدمن والمشرف
        if (
            user.is_authenticated
            and user.role in ['admin', 'supervisor']
        ):
            return True

        # المؤسسة من JWT
        organization_id = request.auth.get(
            "organization_id"
        ) if request.auth else None

        if organization_id:

            from organizations.models import Organization

            try:
                organization = Organization.objects.get(
                    id=organization_id
                )

                return (
                    organization.status == "approved"
                    and organization.verified
                )

            except Organization.DoesNotExist:
                return False

        return False