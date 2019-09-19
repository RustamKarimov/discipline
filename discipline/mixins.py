import pandas as pd

from django.shortcuts import render, redirect
from django.views import generic
from django.forms import modelformset_factory, BaseModelFormSet
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.urls import resolve

from .models import Discipline, DisciplineAction
from .forms import DisciplineForm

from rolepermissions.decorators import has_permission_decorator
from rolepermissions.mixins import HasPermissionsMixin


MERIT_FILENAME = 'static/excel/merits.xlsx'
DEMERIT_FILENAME = 'static/excel/demerits.xlsx'


class DisciplineListMixin(generic.ListView):
    model = Discipline
    discipline_type = None
    paginate_by = 15

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


@has_permission_decorator('admin')
def read_merits_from_file(request):
    current_url = resolve(request.path_info).url_name
    if current_url == 'merit_read':
        filename = MERIT_FILENAME
        discipline_type = Discipline.MERIT
        redirect_url = 'discipline:merit_list'
    else:
        filename = DEMERIT_FILENAME
        discipline_type = Discipline.DEMERIT
        redirect_url = 'discipline:demerit_list'

    data = pd.read_excel(filename, index_col=None)
    for index, row in data.iterrows():
        code = row['CODE']
        description = row['REASON']
        point = row['POINTS']

        if code and description and point:
            merit, created = Discipline.objects.get_or_create(
                code=code,
                description=description,
                point=point,
                discipline_type=discipline_type,
                slug=code,
            )

    messages.info(request, 'Reading from file has been completed... ')
    return redirect(redirect_url)