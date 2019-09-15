from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML

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
                            <a href="{% url 'teachers:list' %}" class="ui right floated button">Cancel</a>
                        {% else %}
                            <a href="{{ teacher.get_absolute_url }}" class="ui right floated button">Cancel</a>
                        {% endif %}                    
                    """),
                ),
                css_class="ui clearing basic segment",
            )
        )