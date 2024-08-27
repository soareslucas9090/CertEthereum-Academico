from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import *

certificados_router = SimpleRouter()
certificados_router.register("users", UsersViewSet)

urlpatterns = [
    path("", include(certificados_router.urls)),
    path(
        "issue/certificates",
        IssueCertificateViewSet.as_view(),
        name="issue_certificates",
    ),
    path("search", SearchCertificateViewSet.as_view(), name="search_certificates"),
]
