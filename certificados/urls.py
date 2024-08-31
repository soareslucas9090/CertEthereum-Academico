from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views.api_views import *
from .views.front_views import *

certificados_router = SimpleRouter()
certificados_router.register("users", UsersViewSet)

urlpatterns = [
    ####### API #######
    path("api/v1/", include(certificados_router.urls)),
    path(
        "api/v1/issue/certificates/",
        IssueCertificateViewSet.as_view(),
        name="issue_certificates",
    ),
    path(
        "api/v1/search/", SearchCertificateViewSet.as_view(), name="search_certificates"
    ),
    ####### Front #######
    path("search/", SearchByCPFView.as_view(), name="search"),
    ####### Front #######
    path("login/", LoginView.as_view(), name="login"),
]
