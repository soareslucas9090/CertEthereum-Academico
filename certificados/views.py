from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   OpenApiResponse, extend_schema)
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Users
from .permissions import IsAdmin
from .serializers import IssueCertificateSerializer, UsersSerializer
from .web3 import web3_interactions


class DefaultNumberPagination(PageNumberPagination):
    page_size = 20


class UsersViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    pagination_class = DefaultNumberPagination
    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "head", "patch", "delete", "post"]

    def get_queryset(self):
        queryset = super().get_queryset().order_by("name")

        name = self.request.GET.get("name", None)

        if name:
            queryset = queryset.filter(name__icontains=name)

        cnpj = self.request.GET.get("cnpj", None)

        if cnpj:
            queryset = queryset.filter(cnpj__icontains=cnpj)

        return queryset

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE", "POST", "GET"]:
            return [IsAdmin()]
        return super().get_permissions()


class IssueCertificateViewSet(GenericAPIView):
    serializer_class = IssueCertificateSerializer
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = serializer.validated_data

        data = {}

        data["cpf"] = serializer["cpf"]
        data["student_name"] = serializer["student_name"]
        data["course"] = serializer["course"]
        data["course_description"] = serializer["course_description"]
        data["certificate_description"] = serializer["certificate_description"]
        data["issue_date"] = int(
            datetime.combine(serializer["issue_date"], datetime.min.time()).timestamp()
        )
        data["course_workload"] = f"{serializer["course_workload"]} horas"
        data["institution_name"] = request.user.name

        try:
            transaction_hash = web3_interactions.certs_interactions(1, data)
            return Response(
                {"status": "success", "transaction_hash": transaction_hash},
                status=status.HTTP_201_CREATED,
            )
        except:
            return Response(
                {
                    "status": "error",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SearchCertificateViewSet(GenericAPIView):
    http_method_names = ["get"]
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='Success'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad Request'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal Error'),
        },
        parameters=[
            OpenApiParameter(
                name="cpf",
                type=OpenApiTypes.STR,
                description="(Apenas números) Busca todos os certificados emitidos contendo um determinado CPF",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="hash",
                type=OpenApiTypes.STR,
                description="(Há prioridade pelo hash do que pelo CPF) Busca o certificado com um determinado hash",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request):
        data = {}
        op = 0

        data["search_cpf"] = request.GET.get("cpf", None)

        if data["search_cpf"]:
            if len(data["search_cpf"]) == 11:
                op = 2
            else:
                return Response(
                        {
                            "status": "error",
                            "detail": "CPF must have 11 numerics digits"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        data["search_hash"] = request.GET.get("hash", None)

        if data["search_hash"]:
            op = 3

        try:
            certificates = web3_interactions.certs_interactions(op, data)
            
            if certificates == []:
                return Response(
                        {
                            "status": "error",
                            "detail": "Not results found for search."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                
            return Response(
                {"status": "success", "certificates": certificates},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {
                    "status": "error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
