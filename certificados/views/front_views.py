from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from ..forms import SearchCPFCertificateForm
from .api_views import SearchCertificateViewSet


@method_decorator(csrf_protect, name="dispatch")
class SearchByCPFView(View):
    def get(self, request):
        form = SearchCPFCertificateForm()

        return render(
            request=request,
            template_name="search/search_cpf.html",
            context={"form": form},
        )

    def post(self, request):

        form = SearchCPFCertificateForm(request.POST)

        if form.is_valid():
            cpf = form.clean_cpf()

            factory = RequestFactory()
            get_request = factory.get(f"/certificates/api/v1/search/?cpf={cpf}")

            searchView = SearchCertificateViewSet.as_view()
            response = searchView(get_request)

            if response.data["status"] == "error":
                return render(
                    request=request,
                    template_name="search/search_cpf.html",
                    context={"form": form, "no_result": True},
                )

            return render(
                request=request,
                template_name="search/search_cpf.html",
                context={"form": form, "results": response.data["certificates"]},
            )

        else:
            return render(
                request=request,
                template_name="search/search_cpf.html",
                context={"form": form},
            )
