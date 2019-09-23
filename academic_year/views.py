from django.views import generic
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.decorators import has_permission_decorator

from settings.models import Settings
from grades.models import Grade
from discipline.models import DisciplineAction

from .models import AcademicYear
from .forms import AcademicYearForm


class AcademicYearList(HasPermissionsMixin, generic.ListView):
    required_permission = 'admin'
    model = AcademicYear
    paginate_by = 10
    template_name = 'academic_year/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'years'
        return context


@has_permission_decorator('admin')
def deactivate_previous_year(request, old_year):
    if old_year:
        old_year.active = False
        old_year.save()

        for grade in old_year.grades.all():
            grade.active = False
            grade.save()


def get_checked_settings():
    settings = Settings.objects.first()
    settings_dict = dict()
    if settings.update_grades:
        settings_dict['update_grades'] = f'{Settings.DEFAULT_DIVISION.title()} of learners will be upgraded ' \
                                         f'to next division'
    else:
        settings_dict['update_grades'] = f'Learners will remain in their current {Settings.DEFAULT_DIVISION.title()}'

    if settings.allow_alumni:
        settings_dict['allow_alumni'] = f'Status of learners in {Settings.DEFAULT_DIVISION.lower()} ' \
                                        f'{settings.DEFAULT_MAX_SECTION} will be changed to alumni.'
    else:
        settings_dict['allow_alumni'] = f'Learners in {Settings.DEFAULT_DIVISION.lower()} ' \
                                        f'{settings.DEFAULT_MAX_SECTION} will be deleted from the system'
    if settings.allow_transfers:
        settings_dict['allow_transfer'] = f'"{Settings.DEFAULT_DIVISION.title()} Transfers" will be created for,' \
                                          f'learners to be transferred.'
    else:
        settings_dict['allow_transfer'] = 'Transferred learners will be deleted from the system.'

    if settings.allow_expulsion:
        settings_dict['allow_expulsion'] = f'"{Settings.DEFAULT_DIVISION.title()} Expelled" will be created for,' \
                                          f'learners to be expelled.'
    else:
        settings_dict['allow_expulsion'] = 'Expelled learners will be deleted from the system.'

    return settings_dict


def apply_settings(request, year):
    settings = Settings.objects.first()

    if settings.update_grades:
        for grade in Grade.active_grades.all():
            section = grade.section
            branch = grade.branch
            learners = grade.learners.all()

            if section < settings.last_section:
                new_grade = Grade.objects.create(
                    year=year,
                    section=section + 1,
                    branch=branch,
                    active=True
                )

                division = Settings.objects.first().division
                slug_str = f"{division} {section} {branch} {year}"
                new_grade.slug = slugify(slug_str)
                new_grade.save()

                for learner in learners:
                    learner.grades.remove(grade)
                    learner.grades.add(new_grade)
            else:
                for learner in learners:
                    learner.is_alumni = True
                    learner.leave_year = learner.get_active_grade().year.year
                    learner.user.current_user = False
                    learner.user.save()
                    learner.save()


@has_permission_decorator('admin')
def add_academic_year(request):
    old_year = AcademicYear.objects.filter(active=True).first()
    form = AcademicYearForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():

            # create new academic year and activate it
            year = form.save()

            # apply the options in settings
            apply_settings(request, year)

            # get the active year and deactivate it
            deactivate_previous_year(request, old_year)

            return redirect('years:details', year.slug)

    context = {
        'action': 'Add New Academic Year',
        'active': 'years',
        'form': form,
        'settings': get_checked_settings()
    }

    return render(request, 'academic_year/form.html', context)


class AcademicYearDetails(HasPermissionsMixin, generic.DetailView):
    required_permission = 'admin'
    model = AcademicYear
    template_name = 'academic_year/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'years'
        context['division'] = Settings.objects.first().division
        return context


class AcademicYearEdit(HasPermissionsMixin, generic.UpdateView):
    required_permission = 'admin'
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'academic_year/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'years'
        context['action'] = 'Edit Academic Year'
        context['cancel_url'] = 'details'
        return context


class AcademicYearDelete(HasPermissionsMixin, generic.DeleteView):
    required_permission = 'admin'
    model = AcademicYear
    template_name = 'academic_year/delete.html'
    success_url = reverse_lazy('years:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'years'
        return context

    def post(self, request, *args, **kwargs):
        year = self.object
        DisciplineAction.objects.filter(time__year=year.year).delete()
        return super().post()
