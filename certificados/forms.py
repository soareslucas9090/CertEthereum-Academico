import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())


class IssueCertificateForm(forms.Form):
    FUNCTIONS = [
        ("organizou", "Organizou"),
        ("executou", "Executou"),
        ("participou", "Participou"),
    ]
    TYPES = [("projeto", "Projeto"), ("evento", "Evento"), ("curso", "Curso")]

    internal_id = forms.CharField(required=False)
    cpf = forms.CharField(required=True)
    student_name = forms.CharField(required=True)
    activity = forms.CharField(required=True)
    activity_description = forms.CharField(required=True, widget=forms.Textarea)
    certificate_description = forms.CharField(required=True, widget=forms.Textarea)
    issue_date = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    course_workload = forms.IntegerField(required=True)
    pdf_certificate = forms.FileField(required=False)
    email = forms.EmailField(required=True)
    function = forms.ChoiceField(required=True, choices=FUNCTIONS, label="Função")
    type = forms.ChoiceField(required=True, choices=TYPES, label="Tipo")
    initial_date = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    final_date = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    local = forms.CharField(required=True)

    def clean_cpf(self):
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11:
            raise ValidationError("O CPF deve conter 11 dígitos")

        return cpf

    def clean_student_name(self):
        name = str(self.cleaned_data.get("student_name"))

        if len(name) < 2:
            raise ValidationError(
                "O nome do estudante precisa ter, no mínimo, 2 caracteres."
            )

        return name

    def clean_course(self):
        course = str(self.cleaned_data.get("course"))

        if len(course) < 3:
            raise ValidationError(
                "O nome do curso precisa ter, no mínimo, 3 caracteres."
            )

        return course

    def clean_certificate_description(self):
        certificate_description = str(self.cleaned_data.get("certificate_description"))

        if len(certificate_description) < 24:
            raise ValidationError(
                "A descrição do certificado precisa ter, no mínimo, 24 caracteres."
            )

        return certificate_description

    def clean_course_description(self):
        course_description = str(self.cleaned_data.get("course_description"))

        if len(course_description) < 24:
            raise ValidationError(
                "A descrição do curso precisa ter, no mínimo, 24 caracteres."
            )

        return course_description

    def clean_issue_date(self):
        issue_date = self.cleaned_data.get("issue_date")

        if issue_date and issue_date > date.today():
            raise ValidationError("A data de emissão não pode ser futura")

        return issue_date

    def clean_course_workload(self):
        course_workload = self.cleaned_data.get("course_workload")

        if course_workload and course_workload < 1:
            raise ValidationError("A carga horária precisa ser um inteiro positivo")

        return course_workload


class SearchCertificateForm(forms.Form):
    SEARCH_CHOICES = [("cpf", "CPF"), ("hash", "Hash")]

    search_type = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect())
    value = forms.CharField(required=False)

    def clean_value(self):
        value = str(self.cleaned_data.get("value"))

        if str(self.cleaned_data.get("search_type")) == "cpf":

            cpf = re.sub("[^0-9]", "", value)

            if len(cpf) != 11:
                raise ValidationError("O CPF fornecido é inválido.")
            return cpf

        return value
