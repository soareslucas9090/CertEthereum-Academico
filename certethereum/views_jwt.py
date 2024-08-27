"""
    Nenhuma lógica é sobreposta, apenas há o override da classe para lhe
    conceder a Tag AUTH do Swagger
"""

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


@extend_schema(tags=["Auth"])
class TokenObtainPairViewDOC(TokenObtainPairView):
    pass


@extend_schema(tags=["Auth"])
class TokenRefreshViewDOC(TokenRefreshView):
    pass


@extend_schema(tags=["Auth"])
class TokenVerifyViewDOC(TokenVerifyView):
    pass
