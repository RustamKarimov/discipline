from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML


from .models import Settings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""<h2 class="ui header">Update Settings</h2>"""),
                    Div(
                        Div(
                            'division',
                            css_class='field'
                        ),
                        Div(
                            'last_section',
                            css_class='field'
                        ),
                        css_class='fields'
                    ),
                    Div(
                        Div(
                            Div(
                                'update_grades',
                                # css_class='ui checkbox'
                            ),
                            css_class='field'
                        ),
                        Div(
                            Div(
                                'allow_alumni',
                                # css_class='ui checkbox'
                            ),
                            css_class='field'
                        ),
                        Div(
                            Div(
                                'allow_transfers',
                                # css_class='ui checkbox'
                            ),
                            css_class='field'
                        ),
                        Div(
                            Div(
                                'allow_expulsion',
                                # css_class='ui checkbox'
                            ),
                            css_class='field'
                        ),
                    ),
                    css_class='ui segment',
                ),
                Div(
                    Div(
                        Submit('submit', 'Submit', css_class="ui right floated grey button"),
                        HTML("""
                            <a href="{% url 'dashboard' %}" class="ui right floated button">Cancel</a>
                        """),
                    ),
                    css_class="ui clearing segment",
                ),
                css_class='ui segments'
            )
        )
