from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from organizations.authentication import OrganizationJWTAuthentication
from .models import Organization
from .serializers import (
    OrganizationSerializer,
    OrganizationRegisterSerializer,
    OrganizationTokenSerializer,
)

from activities.permissions import IsAdminOrSupervisor


class OrganizationLoginView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = OrganizationTokenSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        return Response(serializer.validated_data)

class PendingOrganizationsView(generics.ListAPIView):

    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminOrSupervisor]

    def get_queryset(self):
        return Organization.objects.filter(
            status="pending"
        )

class OrganizationListCreateView(generics.ListCreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrSupervisor()]
        return [IsAuthenticated()]


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminOrSupervisor]

class OrganizationRegisterView(generics.CreateAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationRegisterSerializer
    permission_classes = [AllowAny]


class ApproveOrganizationView(APIView):

    permission_classes = [IsAdminOrSupervisor]

    def post(self, request, pk):

        try:
            organization = Organization.objects.get(id=pk)

        except Organization.DoesNotExist:
            return Response(
                {"message": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        organization.status = "approved"
        organization.verified = True
        organization.save()

        return Response({
            "message": "Organization approved successfully",
            "organization": organization.name,
            "status": organization.status,
            "verified": organization.verified
        })


class RejectOrganizationView(APIView):

    permission_classes = [IsAdminOrSupervisor]

    def post(self, request, pk):

        try:
            organization = Organization.objects.get(id=pk)

        except Organization.DoesNotExist:
            return Response(
                {"message": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        organization.status = "rejected"
        organization.verified = False
        organization.save()

        return Response({
            "message": "Organization rejected",
            "organization": organization.name,
            "status": organization.status,
            "verified": organization.verified
        })

class OrganizationProfileView(APIView):

    authentication_classes = [
        OrganizationJWTAuthentication
    ]

    permission_classes = []

    def get(self, request):

        organization = request.user

        serializer = OrganizationSerializer(
            organization
        )

        return Response(serializer.data)