from datetime import datetime
from typing import Callable

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from certethereum import views_jwt

from ..forms import LoginForm, SearchCertificateForm
from .api_views import SearchCertificateViewSet


def requestFactory(
    method: str,
    url: str,
    view: Callable[..., HttpResponse],
    body: dict[str, str] | None = None,
):
    factory = RequestFactory()
    request = getattr(factory, method)

    if method in ["post", "patch", "put"]:
        request = request(url, data=body)
    else:
        request = request(url)

    return view(request)


access_token = ""
refresh_token = ""


def getTokens() -> dict[str, str]:
    return {"access": access_token, "refresh": refresh_token}


def setTokens(
    access: str,
    refresh: str,
):
    global access_token, refresh_token
    access_token = access
    refresh_token = refresh


def verifyToken(token: str) -> bool:
    data = {"access": token}
    response = requestFactory(
        "post", "api/token/verify/", views_jwt.TokenVerifyViewDOC.as_view(), data
    )

    if response.data.get("detail", None):  # type: ignore
        return False

    return True


def refreshToken() -> str:
    data = {"refresh": getTokens()["refresh"]}
    response = requestFactory(
        "post", "api/token/refresh/", views_jwt.TokenRefreshViewDOC.as_view(), data
    )

    if response.data.get("detail", None):  # type: ignore
        return ""

    global access_token
    access_token = response.data["access"]  # type: ignore
    return response.data["access"]  # type: ignore


@method_decorator(csrf_protect, name="dispatch")
class SearchView(View):
    def get(self, request):
        form = SearchCertificateForm()

        return render(
            request=request,
            template_name="menu/search/search.html",
            context={"form": form},
        )

    def post(self, request):

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
                    template_name="menu/search/search.html",
                    context={"form": form, "no_result": choice.upper()},
                )

            # Caso o retorno seja somente um resultado, é colocado em uma lista para iteração no HTML
            if choice == "hash":
                response.data["certificates"] = [response.data["certificates"]]  # type: ignore

            return render(
                request=request,
                template_name="menu/search/search.html",
                context={"form": form, "results": response.data["certificates"]},  # type: ignore
            )

        else:
            return render(
                request=request,
                template_name="menu/search/search.html",
                context={"form": form},
            )


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
                setTokens(response.data.get("access"), response.data.get("refresh"))  # type: ignore

                return redirect("menu")

        else:
            return render(
                request=request,
                template_name="menu/registration/login.html",
                context={"form": form},
            )


@method_decorator(csrf_protect, name="dispatch")
class MenuView(View):
    def get(self, request):
        token = getTokens()

        if token["access"] != "":
            isAuthenticated = True
        else:
            isAuthenticated = False

        return render(
            request=request,
            template_name="menu/menu_base.html",
            context={"isAuthenticated": isAuthenticated},
        )
