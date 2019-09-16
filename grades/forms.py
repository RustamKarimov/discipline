from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML

from academic_year.models import AcademicYear
from settings.models import Settings
from users.models import Teacher

from .models import Grade


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('section', 'branch')


class GradeUpdateForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('section', 'branch', 'active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['active'].widget.attrs['class'] = 'ui checkbox'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                'section',
                css_class='field'
            ),
            Div(
                'branch',
                css_class='field'
            ),
            Div(
                'active',
                css_class='field'
            ),

            Div(
                Div(
                    Submit('submit', 'Submit', css_class="ui right floated grey button"),
                    HTML("""<a href="{% url 'grades:list' %}" class="ui right floated button">Cancel</a>           """),
                ),
                css_class="ui clearing basic segment",
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data['section']
        branch = cleaned_data['branch']
        year = AcademicYear.objects.get(active=True)

        grade = Grade.objects.filter(year=year, section=section, branch=branch).first()
        if grade:
            raise forms.ValidationError(f'{grade} is already in database.')


class TeacherToGradeForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(Teacher.objects.all(),
                                              widget=forms.CheckboxSelectMultiple(),
                                              required=False)

    class Meta:
        model = Grade
        fields = ('teachers', )

    def __init__(self, **kwargs):
        grade = kwargs.pop('instance')
        super().__init__(**kwargs)
        form_teachers = grade.teachers.all()
        self.fields['teachers'].initial = form_teachers
