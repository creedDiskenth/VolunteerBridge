from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Organization
from .serializers import OrganizationSerializer

from activities.permissions import IsAdminOrSupervisor


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