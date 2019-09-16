from django import forms

from .models import AcademicYear


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ('year', )