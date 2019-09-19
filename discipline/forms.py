from django import forms

from .models import Discipline, DisciplineAction


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        exclude = ('slug', 'discipline_type')


class MeritModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class MeritActionForm(forms.ModelForm):
    action = MeritModelChoiceField(queryset=Discipline.objects.filter(discipline_type=Discipline.MERIT))

    class Meta:
        model = DisciplineAction
        fields = ('action', 'time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DemeritActionForm(forms.ModelForm):
    action = MeritModelChoiceField(queryset=Discipline.objects.filter(discipline_type=Discipline.DEMERIT))

    class Meta:
        model = DisciplineAction
        fields = ('action', 'time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)