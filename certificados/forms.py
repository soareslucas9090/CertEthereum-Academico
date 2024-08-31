from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())


class SearchCertificateForm(forms.Form):
    SEARCH_CHOICES = [("cpf", "CPF"), ("hash", "Hash")]

    search_type = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect())
    value = forms.CharField(required=False)

    def clean_value(self):
        value = str(self.cleaned_data.get("value"))

        if str(self.cleaned_data.get("search_type")) == "cpf":

            if len(value) != 11 or not value.isdigit():
                raise ValidationError("O CPF fornecido é inválido.")
            return value

        return value
