from django.urls import path
from .views import PendingOrganizationsView

from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    OrganizationRegisterView,
    ApproveOrganizationView,
    RejectOrganizationView,
    OrganizationLoginView,
    OrganizationProfileView,
)

urlpatterns = [
    path(
        "",
        OrganizationListCreateView.as_view(),
        name="organization-list-create"
    ),

    path(
        "<int:pk>/",
        OrganizationDetailView.as_view(),
        name="organization-detail"
    ),

    path(
        "register/",
        OrganizationRegisterView.as_view(),
        name="organization-register"
    ),
    path(
       "pending/",
       PendingOrganizationsView.as_view(),
       name="pending-organizations"
),
    path(
       "<int:pk>/approve/",
       ApproveOrganizationView.as_view(),
       name="organization-approve"
),

    path(
       "<int:pk>/reject/",
       RejectOrganizationView.as_view(),
       name="organization-reject"
),
    path(
      "login/",
      OrganizationLoginView.as_view(),
      name="organization-login"
),
    path(
      "profile/",
      OrganizationProfileView.as_view(),
      name="organization-profile"
),
]