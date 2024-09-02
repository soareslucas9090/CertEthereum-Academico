from django.shortcuts import redirect
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
    path("menu/search/", SearchView.as_view(), name="search"),
    path("menu/issue/", IssueCertificateView.as_view(), name="issue_certificate"),
    path("login/", LoginView.as_view(), name="login"),
    path("", RedirectView.as_view()),
    path("menu/", MenuView.as_view(), name="menu"),
    path("menu/logout/", LogoutView.as_view(), name="logout"),
]
