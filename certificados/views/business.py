from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from certethereum import views_jwt


def requestFactory(
    method: str,
    url: str,
    view: Callable[..., HttpResponse],
    body: dict[str, str] | None = None,
    header: dict | None = None,
):
    factory = RequestFactory()
    request = getattr(factory, method)

    if method in ["post", "patch", "put"]:
        request = request(url, data=body)
    else:
        request = request(url)

    if header:
        for key, value in header.items():
            request.META[f"HTTP_{key.upper()}"] = value

    return view(request)


def getTokens(request: HttpRequest) -> dict[str, str | None]:
    access = request.COOKIES.get("access_token")
    refresh = request.COOKIES.get("refresh_token")
    return {"access": access, "refresh": refresh}


def setTokens(response: HttpResponse, access: str, refresh: str) -> HttpResponse:
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)
    return response


def verifyToken(token: str) -> bool:
    data = {"token": token}
    response = requestFactory(
        "post", "api/token/verify/", views_jwt.TokenVerifyViewDOC.as_view(), data  # type: ignore
    )

    if response.status_code != 200:
        return False

    return True


def refreshToken(request: HttpRequest, response_redirect: HttpResponse) -> HttpResponse:
    tokens = getTokens(request)

    refresh = tokens["refresh"]

    data = {}
    if refresh:
        data = {"refresh": refresh}
    else:
        data = {"refresh": "null"}

    response = requestFactory(
        "post", "api/token/refresh/", views_jwt.TokenRefreshViewDOC.as_view(), data
    )

    if response.status_code != 200:
        return setTokens(response_redirect, "", "")

    return setTokens(response_redirect, response.data.get("access"), tokens["refresh"])  # type: ignore


def isAuthenticated(token: dict[str, str | None]) -> bool:
    isAuthenticated = False

    if token["access"] and token["access"] != "":
        isAuthenticated = True

    return isAuthenticated
