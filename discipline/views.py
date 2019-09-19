from django.views import generic
from django.urls import reverse_lazy

from rolepermissions.mixins import HasPermissionsMixin

from . import mixins
from .models import Discipline, DisciplineAction
from .forms import DisciplineForm


class MeritList(HasPermissionsMixin, mixins.DisciplineListMixin):
    discipline_type = 'merit'
    required_permission = 'admin'


class DemeritList(HasPermissionsMixin, mixins.DisciplineListMixin):
    discipline_type = 'demerit'
    required_permission = 'admin'


class DisciplineDetail(HasPermissionsMixin, generic.DetailView):
    required_permission = 'admin'
    model = Discipline
    template_name = 'discipline/details.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        discipline = self.get_object()
        context['active'] = 'demerits' if discipline.is_demerit else 'merits'
        context['discipline_type'] = 'Demerit' if discipline.is_demerit else 'Merit'
        context['list_url'] = 'discipline:demerit_list' if discipline.is_demerit else 'discipline:merit_list'
        return context


class MeritAdd(HasPermissionsMixin, mixins.DisciplineAddMixin):
    required_permission = 'admin'
    discipline_type = 'merit'


class DemeritAdd(HasPermissionsMixin, mixins.DisciplineAddMixin):
    required_permission = 'admin'
    discipline_type = 'demerit'


class DisciplineEdit(HasPermissionsMixin, generic.UpdateView):
    required_permission = 'admin'
    model = Discipline
    form_class = DisciplineForm
    template_name = 'discipline/update_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        discipline = self.get_object()
        context['active'] = 'demerits' if discipline.is_demerit else 'merits'
        context['discipline_type'] = 'Demerit' if discipline.is_demerit else 'Merit'
        context['cancel_url'] = discipline.get_absolute_url()
        return context


class DisciplineDelete(HasPermissionsMixin, generic.DeleteView):
    required_permission = 'admin'
    model = Discipline
    template_name = 'discipline/delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discipline = self.get_object()
        context['active'] = 'demerits' if discipline.is_demerit else 'merits'
        context['discipline_type'] = 'demerit' if discipline.is_demerit else 'merit'
        context['list_url'] = 'discipline:demerit_list' if discipline.is_demerit else 'discipline:merit_list'
        return context

    def get_success_url(self):
        discipline = self.get_object()
        if discipline.is_demerit:
            return reverse_lazy('discipline:demerit_list')
        return reverse_lazy('discipline:merit_list')