import datetime

from django import forms

from grades.models import Grade

from .models import Discipline, DisciplineAction


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        exclude = ('slug', 'discipline_type')


class MeritModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class DisciplineActionForm(forms.ModelForm):
    action = MeritModelChoiceField(queryset=Discipline.objects.none())

    class Meta:
        model = DisciplineAction
        fields = ('action', 'time')

    def __init__(self, *args, **kwargs):
        discipline_type = kwargs.pop('discipline_type')

        super().__init__(*args, **kwargs)

        self.fields['action'].queryset = Discipline.merits.all() if discipline_type.lower() == 'merit' \
            else Discipline.demerits.all()


class DisciplineGradeForm(forms.ModelForm):
    action = MeritModelChoiceField(queryset=Discipline.objects.none(),
                                   required=False)
    time = forms.DateTimeField(required=False)

    class Meta:
        model = DisciplineAction
        fields = ('action', 'time')

    def __init__(self, *args, **kwargs):
        discipline_type = kwargs.pop('discipline_type')
        super().__init__(*args, **kwargs)
        self.fields['time'].initial = datetime.datetime.now()
        self.fields['time'].widget.attrs['class'] = 'ui calendar'
        self.fields['action'].widget.attrs['class'] = 'ui fluid dropdown'

        self.fields['action'].queryset = Discipline.merits.all() if discipline_type.lower() == 'merit' \
            else Discipline.demerits.all()
