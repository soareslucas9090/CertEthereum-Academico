from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

"""
    Esta importação personalizada tem intuito apenas de inserir as rotas de api/token sob
    a Tag AUTH pelo Swagger
"""
from .views_jwt import TokenObtainPairViewDOC, TokenRefreshViewDOC, TokenVerifyViewDOC

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairViewDOC.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshViewDOC.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyViewDOC.as_view(), name="token_verify"),
    path("api/certificados/v1/", include("certificados.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
