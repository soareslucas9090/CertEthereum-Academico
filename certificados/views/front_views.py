from datetime import datetime
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from certethereum import views_jwt

from ..forms import LoginForm, SearchCertificateForm
from .api_views import SearchCertificateViewSet
from .business import (
    getTokens,
    isAuthenticated,
    refreshToken,
    requestFactory,
    setTokens,
    verifyToken,
)


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
