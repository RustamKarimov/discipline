from django import forms

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
        try:
            discipline_type = kwargs.pop('discipline_type')
        except:
            discipline_type = None
        super().__init__(*args, **kwargs)
        if not discipline_type:
            self.fields['action'].queryset = Discipline.objects.all()
        else:
            self.fields['action'].queryset = Discipline.merits.all() if discipline_type.lower() == 'merit' \
                else Discipline.demerits.all()