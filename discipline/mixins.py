from django.views import generic
from django.forms import modelformset_factory, BaseModelFormSet
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import CharField, IntegerField, Value
from django.db.models.functions import Cast, Substr

from .models import Discipline
from .forms import DisciplineForm

from rolepermissions.mixins import HasPermissionsMixin


MERIT_FILENAME = 'static/excel/merits.xlsx'
DEMERIT_FILENAME = 'static/excel/demerits.xlsx'


class DisciplineListMixin(generic.ListView):
    model = Discipline
    discipline_type = None
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = f'{self.discipline_type}s'
        context['discipline_type'] = f'{self.discipline_type.title()}'
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.discipline_type == 'merit':
            queryset = qs.filter(discipline_type=Discipline.MERIT)
        else:
            queryset = qs.filter(discipline_type=Discipline.DEMERIT)
        queryset = queryset.annotate(num_part=Cast(Substr('code', 2), IntegerField())).order_by('point', 'num_part')
        return queryset


class DisciplineBaseModelFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Discipline.objects.none()


class DisciplineAddMixin(generic.FormView):
    form_class = modelformset_factory(Discipline, DisciplineForm, formset=DisciplineBaseModelFormset)
    template_name = 'discipline/discipline_form.html'
    discipline_type = None

    def form_valid(self, form):
        discipline_type = Discipline.MERIT if self.discipline_type.lower() == 'merit' else Discipline.DEMERIT
        with transaction.atomic():
            for sub_form in form:
                if sub_form.is_valid() and sub_form.cleaned_data:
                    code = sub_form.cleaned_data['code']
                    description = sub_form.cleaned_data['description']
                    point = sub_form.cleaned_data['point']

                    discipline, created = Discipline.objects.get_or_create(
                        code=code, description=description, point=point
                    )

                    if created:
                        discipline.discipline_type = discipline_type
                        discipline.save()

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = f'{self.discipline_type}s'
        context['sender'] = f'discipline:{self.discipline_type}_list'
        context['discipline_type'] = self.discipline_type.title()
        return context

    def get_success_url(self):
        reverse_url = f"discipline:{self.discipline_type}_list"
        return reverse_lazy(reverse_url)


class DisciplineUpdate(HasPermissionsMixin, generic.UpdateView):
    required_permission = 'admin'
    model = Discipline
    form_class = DisciplineForm
    template_name = 'discipline/discipline_update_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        discipline = self.get_object()
        context['active'] = 'demerits' if discipline.is_demerit else 'merits'
        context['cancel_url'] = discipline.get_absolute_url()
        return context


class DisciplineDelete(HasPermissionsMixin, generic.DeleteView):
    required_permission = 'admin'
    model = Discipline
    template_name = 'discipline/discipline_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discipline = self.get_object()
        context['active'] = 'demerits' if discipline.is_demerit else 'merits'
        context['discipline_type'] = 'demerit' if discipline.is_demerit else 'merit'
        return context

    def get_success_url(self):
        discipline = self.get_object()
        if discipline.is_demerit:
            return reverse_lazy('discipline:demerit_list')
        return reverse_lazy('discipline:merit_list')

