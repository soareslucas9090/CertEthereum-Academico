import os
from datetime import datetime
from email.mime.image import MIMEImage
from typing import Callable

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
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

        form = IssueCertificateForm(request.POST, request.FILES)

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
            to_email = form.cleaned_data["email"]
            pdf_certificate = form.cleaned_data["pdf_certificate"]

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

            if (to_email):
                
                first_html = """
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Seu Certificado CertEthereum</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #ffffff;
                        }
                        .header {
                            text-align: center;
                            margin-bottom: 20px;
                        }
                        .header img {
                            max-width: 100px;
                        }
                        h1 {
                            color: #25478A;
                            text-align: center;
                        }
                        .certificate-info {
                            background-color: #f9f9f9;
                            border: 1px solid #ddd;
                            padding: 20px;
                            margin-bottom: 20px;
                        }
                        .certificate-info p {
                            margin: 10px 0;
                        }
                        .attachment-info {
                            background-color: #e9f0f9;
                            border: 1px solid #25478A;
                            padding: 15px;
                            margin-bottom: 20px;
                            color: #0C2047;
                        }
                        .footer {
                            text-align: center;
                            color: #0C2047;
                            font-size: 14px;
                            margin-top: 30px;
                        }
                    </style>
                </head>
                """
                
                logo_path = os.path.join(settings.STATIC_ROOT, 'imgs/logo.png')
                
                second_html = f"""
                <body>
                    <div class="header">
                        <img src="cid:logo_image" alt="Logo CertEthereum">
                    </div>
                    
                    <h1>Seu Certificado</h1>
                    
                    <div class="certificate-info">
                        <p><strong>Nome do Aluno:</strong> {data["student_name"]}</p>
                        <p><strong>CPF:</strong> {data["cpf"]}</p>
                        <p><strong>Curso:</strong> {data["course"]}</p>
                        <p><strong>Data de Emissão:</strong> {data["issue_date"]}</p>
                        <p><strong>Carga Horária:</strong> {data["course_workload"]} horas</p>
                    </div>
                    
                    <div class="attachment-info">
                        <p>O arquivo do seu certificado está anexado a este e-mail.</p>
                    </div>
                    
                    <div class="footer">
                        <p>CertEthereum - Lucas Soares</p>
                    </div>
                </body>
                </html>
                """

                final_html = first_html
                final_html += second_html

                email = EmailMultiAlternatives(
                    "Parabés, aqui está seu certificado!",	
                    f"Seu certificado está em anexo",  # Texto simples alternativo
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                )

                email.attach_alternative(final_html, "text/html")  # Corpo em HTML
                
                with open(logo_path, 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo_image>')
                    email.attach(logo) # type: ignore [arg-type]
                
                if pdf_certificate:
                    email.attach(
                        pdf_certificate.name, 
                        pdf_certificate.read(), 
                        pdf_certificate.content_type
                    )

                try:
                    email.send()
                except Exception as e:
                    print(e)
                    form.add_error(
                    None,
                    "Não foi possível enviar email para o estudante.",
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
