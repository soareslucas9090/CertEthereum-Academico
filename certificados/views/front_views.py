from datetime import datetime
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from certethereum import views_jwt

from ..forms import IssueCertificateForm, LoginForm, SearchCertificateForm
from .api_views import IssueCertificateViewSet, SearchCertificateViewSet
from .business import (getTokens, isAuthenticated, refreshToken,
                       requestFactory, setTokens, verifyToken)


def protectedEndPoint(
    request: HttpRequest, url: str, isAuth: bool, token: dict[str, str | None]
) -> HttpResponse | None:
    if not isAuth:
        return redirect("login")

    isValidToken = verifyToken(str(token["access"]))
    if not isValidToken:
        response = redirect(url)

        response = refreshToken(request, response)

        return response

    return None

@method_decorator(csrf_protect, name="dispatch")
class RedirectView(View):
    def get(self, request):
        return redirect("menu")

@method_decorator(csrf_protect, name="dispatch")
class LogoutView(View):
    def get(self, request):
        response = redirect("menu")

        response = setTokens(response, "", "")

        return response


@method_decorator(csrf_protect, name="dispatch")
class LoginView(View):
    def get(self, request):
        form = LoginForm()

        return render(
            request=request,
            template_name="menu/registration/login.html",
            context={"form": form},
        )

    def post(self, request):

        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            data = {"email": email, "password": password}

            response = requestFactory(
                "post", "api/token/", views_jwt.TokenObtainPairViewDOC.as_view(), data
            )

            if response.data.get("detail", None):  # type: ignore
                form.errors.clear()
                form.add_error(
                    None,
                    "Usuário e/ou senha incorreto(s)!",
                )

                return render(
                    request=request,
                    template_name="menu/registration/login.html",
                    context={"form": form},
                )

            else:
                response_redirect = redirect("menu")

                response_redirect = setTokens(
                    response_redirect,
                    response.data.get("access"),  # type: ignore
                    response.data.get("refresh"),  # type: ignore
                )

                return response_redirect

        else:
            return render(
                request=request,
                template_name="menu/registration/login.html",
                context={"form": form},
            )


@method_decorator(csrf_protect, name="dispatch")
class MenuView(View):
    def get(self, request):
        token = getTokens(request)
        isAuth = isAuthenticated(token)

        return render(
            request=request,
            template_name="menu/menu_base.html",
            context={"isAuthenticated": isAuth},
        )


@method_decorator(csrf_protect, name="dispatch")
class SearchView(View):
    def get(self, request):
        token = getTokens(request)
        isAuth = isAuthenticated(token)

        form = SearchCertificateForm()

        return render(
            request=request,
            template_name="menu/certificates/search.html",
            context={
                "form": form,
                "isAuthenticated": isAuth,
            },
        )

    def post(self, request):
        token = getTokens(request)
        isAuth = isAuthenticated(token)

        form = SearchCertificateForm(request.POST)

        if form.is_valid():
            value = form.clean_value()
            choice = form.cleaned_data["search_type"]

            if choice == "cpf":
                url = f"/certificates/api/v1/search/?cpf={value}"
            elif choice == "hash":
                url = f"/certificates/api/v1/search/?hash={value}"

            response = requestFactory("get", url, SearchCertificateViewSet.as_view())

            if response.data["status"] == "error":  # type: ignore
                return render(
                    request=request,
                    template_name="menu/certificates/search.html",
                    context={
                        "form": form,
                        "no_result": choice.upper(),
                        "isAuthenticated": isAuth,
                    },
                )

            # Caso o retorno seja somente um resultado, é colocado em uma lista para iteração no HTML
            if choice == "hash":
                response.data["certificates"] = [response.data["certificates"]]  # type: ignore

            return render(
                request=request,
                template_name="menu/certificates/search.html",
                context={"form": form, "results": response.data["certificates"], "isAuthenticated": isAuth},  # type: ignore
            )

        else:
            return render(
                request=request,
                template_name="menu/certificates/search.html",
                context={"form": form, "isAuthenticated": isAuth},
            )


@method_decorator(csrf_protect, name="dispatch")
class IssueCertificateView(View):
    def get(self, request):
        token = getTokens(request)
        isAuth = isAuthenticated(token)

        response = protectedEndPoint(request, "issue_certificate", isAuth, token)
        if response:
            return response

        form = IssueCertificateForm()

        return render(
            request=request,
            template_name="menu/certificates/issue.html",
            context={
                "form": form,
                "isAuthenticated": isAuth
            },
        )

    def post(self, request):
        token = getTokens(request)
        isAuth = isAuthenticated(token)

        response = protectedEndPoint(request, "issue_certificate", isAuth, token)
        if response:
            return response

        form = IssueCertificateForm(request.POST)

        if form.is_valid():

            url = f"/certificates/api/v1/issue/certificates/"

            data = {}
            data["cpf"] = form.cleaned_data["cpf"]
            data["student_name"] = form.cleaned_data["student_name"]
            data["course"] = form.cleaned_data["course"]
            data["course_description"] = form.cleaned_data["course_description"]
            data["certificate_description"] = form.cleaned_data[
                "certificate_description"
            ]
            data["issue_date"] = form.cleaned_data["issue_date"]
            data["course_workload"] = form.cleaned_data["course_workload"]

            header = {}
            header = {"Authorization": f"Bearer {token["access"]}"}

            response = requestFactory(
                "post", url, IssueCertificateViewSet.as_view(), data, header
            )

            if response.status_code != 201:
                
                if response.status_code == 400:
                    form.add_error(
                        None,
                        "Este certificado já existe.",
                    )
                    
                if response.status_code == 500:
                    form.add_error(
                        None,
                        "Ocorreu um erro ao gerar o certificado. Entre em contato com o suporte.",
                    )
                    
                return render(
                    request=request,
                    template_name="menu/certificates/issue.html",
                    context={
                        "form": form,
                        "isAuthenticated": isAuth
                    },
                )

            return render(
                request=request,
                template_name="menu/certificates/issue.html",
                context={"form": form, "isAuthenticated": isAuth, "created": True},
            )

        else:
            return render(
                request=request,
                template_name="menu/certificates/issue.html",
                context={"form": form, "isAuthenticated": isAuth},
            )
