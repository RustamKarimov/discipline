from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML

from grades.models import Grade

from .models import User, Teacher, Learner


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'image', 'user_id',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Div(
                Div('user_id', css_class='field'),
                Div('first_name', css_class='field'),
                Div('last_name', css_class='field'),
                css_class='three fields',
            ),
            Div(
                'email',
                css_class='field'
            ),
            Div(
                'image',
                css_class='field'
            ),

            Div(
                Div(
                    Submit('submit', 'Submit', css_class="ui right floated grey button"),
                    HTML("""
                        {% if 'Add' in action %}
                            {% if active == 'teachers' %}
                                <a href="{% url 'teachers:list' %}" class="ui right floated button">Cancel</a>
                            {% else %}
                                <a href="{% url 'learners:list' %}" class="ui right floated button">Cancel</a>
                            {% endif %}
                        {% else %}
                            {% if active == 'teachers' %}
                                <a href="{{ user.teacher.get_absolute_url }}" class="ui right floated button">Cancel</a>
                            {% else %}
                                <a href="{{ user.learner.get_absolute_url }}" class="ui right floated button">Cancel</a>                            
                            {% endif %}
                        {% endif %}                    
                    """),
                ),
                css_class="ui clearing basic segment",
            )
        )


class GradesToTeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('form_class',)
        widgets = {
            'form_class': forms.CheckboxSelectMultiple()
        }


class GradeFilterForm(forms.Form):
    grades = forms.ModelChoiceField(queryset=Grade.active_grades.all(), required=False, label='Select Grade')
    name = forms.CharField(required=False, label='Search learner')

    class Meta:
        model = Learner
        fields = ('name', 'grades')

    def __init__(self):
        super().__init__()
        self.fields['grades'].widget.attrs['class'] = 'ui fluid dropdown'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'name',
                    css_class='field'
                ),
                Div(
                    'grades',
                    css_class='field'
                ),
                css_class='two fields',
            )
        )


class AssignGradesToLearnersForm(forms.ModelForm):
    grades = forms.ModelChoiceField(queryset=Grade.active_grades.all(), required=False)

    class Meta:
        model = Learner
        fields = ('grades',)
