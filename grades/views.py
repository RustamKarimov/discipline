from django.views import generic
from django.contrib import messages
from django.forms import modelformset_factory, BaseModelFormSet
from django.shortcuts import redirect
from django.utils.text import slugify
from django.urls import reverse_lazy

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.checkers import has_object_permission

from academic_year.models import AcademicYear
from settings.models import Settings

from .models import Grade
from .forms import GradeForm


class GradeList(generic.ListView):
    model = Grade
    queryset = Grade.active_grades.all()
    paginate_by = 12
    template_name = 'grades/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = 'grades'
        year = AcademicYear.objects.filter(active=True).first()
        if year:
            context['year'] = year.year
        else:
            messages.error(self.request, 'You need to add an academic year first.')
        return context


class GradeBaseModelFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Grade.objects.none()


class GradeAdd(HasPermissionsMixin, generic.FormView):
    required_permission = 'admin'
    form_class = modelformset_factory(Grade, GradeForm, formset=GradeBaseModelFormset)
    template_name = 'grades/form.html'

    def get(self, request, *args, **kwargs):
        if not AcademicYear.objects.filter(active=True):
            messages.error(request, 'You need to add an academic year first.')
            return redirect('years:add')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        year = AcademicYear.objects.get(active=True)

        for sub_form in form:
            if sub_form.is_valid() and sub_form.cleaned_data:

                section = sub_form.cleaned_data['section']
                branch = sub_form.cleaned_data['branch']

                grade_exist = Grade.objects.filter(
                    year=year,
                    section=section,
                    branch=branch
                )

                if not grade_exist:
                    new_grade = sub_form.save(commit=False)
                    new_grade.year = year

                    division = Settings.objects.first().division
                    slug_str = f"{division} {section} {branch} {year}"
                    new_grade.slug = slugify(slug_str)
                    new_grade.save()

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = 'grades'

        year = AcademicYear.objects.filter(active=True).first()
        if year:
            context['year'] = year.year
        else:
            messages.error(self.request, 'You need to add an academic year first.')
            return redirect('years:add')

        return context

    def get_success_url(self):
        return reverse_lazy('grades:list')


class GradeDetails(generic.DetailView):
    model = Grade
    template_name = 'grades/details.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = 'grades'
        return context

    def get(self, request, *args, **kwargs):
        grade = self.get_object()
        permission = 'view_grade'
        if has_object_permission(permission, request.user, grade):
            return super().get(request, *args, **kwargs)
        else:
            messages.warning(request, "You don't have permission to perform this action. "
                             "Please login as another user.")
            return redirect('login')