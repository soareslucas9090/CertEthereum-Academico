from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())


class SearchCPFCertificateForm(forms.Form):
    cpf = forms.CharField()

    def clean_cpf(self):
        cpf = str(self.cleaned_data.get("cpf"))

        if len(cpf) != 11 or not cpf.isdigit():
            raise ValidationError("O CPF fornecido é inválido.")
        return cpf
