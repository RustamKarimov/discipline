from django.db import transaction
from django.shortcuts import redirect, get_object_or_404, render, reverse
from django.views import generic
from django.contrib import messages
from django.urls import resolve
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.contrib.auth.decorators import login_required

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.decorators import has_permission_decorator

from discipline.forms import DisciplineActionForm, DisciplineActionUpdateForm
from discipline.models import DisciplineAction, Discipline

from academic_year.models import AcademicYear

from grades.models import Grade

from ..models import Teacher, Learner
from ..forms import UserForm, GradesToTeacherForm, SelectLearnerForm, GradeListForm
from .. import mixins
from users.tasks import read_teachers_from_file


class TeacherList(HasPermissionsMixin, mixins.UserList):
    required_permission = 'admin'
    model = Teacher
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user__current_user=True).prefetch_related('form_class')
        return qs


class TeacherAdd(HasPermissionsMixin, mixins.UserAdd):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm


class TeacherDetails(mixins.UserDetails):
    model = Teacher


class TeacherEdit(HasPermissionsMixin, mixins.UserEdit):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm


class TeacherDelete(HasPermissionsMixin, mixins.UserDelete):
    required_permission = 'admin'
    model = Teacher


class AssignGradesToTeacher(HasPermissionsMixin, generic.UpdateView):
    required_permission = 'admin'
    model = Teacher
    form_class = GradesToTeacherForm
    template_name = 'teachers/grades_to_teacher.html'

    def form_valid(self, form):
        teacher = self.get_object()
        existing_grades = teacher.form_class.filter(active=True)
        with transaction.atomic():
            new_grades = form.cleaned_data['form_class']

            for grade in existing_grades:
                teacher.form_class.remove(grade)

            for grade in new_grades:
                teacher.form_class.add(grade)

            return redirect('teachers:details', teacher.slug)


@has_permission_decorator('admin')
def add_teachers_from_file(request):
    messages.info(request, 'The reading from file is in progress. You can proceed with your work. '
                           'Once the process completed teachers will be listed in this page.')
    result = read_teachers_from_file.delay()

    for message in result.collect():
        messages.info(request, message[1])

    return redirect('teachers:list')


class DisciplineActionBaseModelFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = DisciplineAction.objects.none()

@login_required
def discipline_action_to_learner(request, slug):
    # Get and check if the user has permission to make the action
    teacher = get_object_or_404(Teacher, slug=slug)
    if not request.user.is_teacher or request.user.teacher != teacher:
        messages.error(request, "You don't have permission to perform this action. Please login as another user.")
        return redirect('login')

    # get correct form to use
    current_url = resolve(request.path_info).url_name
    if current_url == 'merit_to_learner':
        discipline_type = 'Merit'
    else:
        discipline_type = 'Demerit'

    # Get the learner form
    learner_form = SelectLearnerForm(request.POST or None)
    year = AcademicYear.objects.get(active=True)

    # Get the discipline action formset
    discipline_formset = modelformset_factory(DisciplineAction, form=DisciplineActionForm,
                                              formset=DisciplineActionBaseModelFormset)
    formset = discipline_formset(request.POST or None,
                                 form_kwargs={'discipline_type': discipline_type})

    if learner_form.is_valid() and formset.is_valid():
        learner = learner_form.cleaned_data['learner']
        with transaction.atomic():
            created = False
            for form in formset:
                if form.is_valid() and form.cleaned_data:
                    action = form.cleaned_data['action']
                    time = form.cleaned_data['time']
                    if action and time.year == year.year:
                        DisciplineAction.objects.create(
                            teacher=teacher,
                            learner=learner,
                            action=action,
                            time=time,
                        )
                        created = True

            if created:
                messages.info(request, f'{discipline_type}s were added to {learner} by {teacher} at {time}')

            learner_form = SelectLearnerForm()
            formset = discipline_formset(form_kwargs={'discipline_type': discipline_type})

    context = {
        'learner_form': learner_form,
        'formset': formset,
        'action': discipline_type
    }

    return render(request, 'teachers/merit_to_learner.html', context)


def add_discipline_action_to_grade(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)

    current_url = resolve(request.path_info).url_name
    if current_url == 'select_merit_grade':
        discipline_type = 'Merit'
    else:
        discipline_type = 'Demerit'

    filter_form = GradeListForm()

    context = {
        'filter_form': filter_form,
        'teacher': teacher,
        'discipline_type': discipline_type
    }

    return render(request, 'teachers/discipline_to_grade.html', context)


class DisciplineActionList(generic.ListView):
    model = DisciplineAction
    paginate_by = 10
    template_name = 'teachers/discipline_list.html'

    def get(self, request, *args, **kwargs):
        teacher_slug = self.kwargs['slug']
        self.teacher = get_object_or_404(Teacher, slug=teacher_slug)

        if self.teacher != request.user.teacher:
            messages.warning(request, "You don't have permission to perform this action. "
                             "Please login as another user.")
            return redirect('login')

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        year = AcademicYear.objects.get(active=True).year

        qs = super().get_queryset()
        qs = qs.filter(teacher=self.teacher, time__year=year).select_related('action')

        current_url = resolve(self.request.path_info).url_name
        if current_url == 'merit_list':
            qs = qs.filter(action__discipline_type=Discipline.MERIT)
        else:
            qs = qs.filter(action__discipline_type=Discipline.DEMERIT)

        return qs

    def get_context_data(self, **kwargs):
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'merit_list':
            discipline_type = 'Merit'
        else:
            discipline_type = 'Demerit'

        context = super().get_context_data(**kwargs)
        context['teacher'] = self.teacher
        context['discipline_type'] = discipline_type
        return context


class DisciplineActionUpdate(generic.UpdateView):
    model = DisciplineAction
    form_class = DisciplineActionForm
    template_name = 'teachers/discipline_update_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'update_merit_action':
            kwargs['discipline_type'] = 'merit'
        else:
            kwargs['discipline_type'] = 'demerit'
        return kwargs

    def get_success_url(self):
        teacher_slug = self.kwargs['teacher_slug']

        current_url = resolve(self.request.path_info).url_name
        if current_url == 'update_merit_action':
            success_url = 'teachers:merit_list'
        else:
            success_url = 'teachers:demerit_list'

        return reverse(success_url,  args=[teacher_slug])

    def get_context_data(self, **kwargs):
        teacher_slug = self.kwargs['teacher_slug']
        teacher = get_object_or_404(Teacher, slug=teacher_slug)
        context = super().get_context_data()
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'update_merit_action':
            cancel_url = 'teachers:merit_list'
            discipline_type = 'Merit'
        else:
            cancel_url = 'teachers:demerit_list'
            discipline_type = 'Demerit'

        context['cancel_url'] = cancel_url
        context['teacher_slug'] = teacher_slug
        context['discipline_type'] = discipline_type
        context['teacher'] = teacher
        return context


class DisciplineActionDelete(generic.DeleteView):
    model = DisciplineAction
    template_name = 'discipline/discipline_action_delete.html'

    def get_success_url(self):
        teacher_slug = self.kwargs['teacher_slug']

        current_url = resolve(self.request.path_info).url_name
        if current_url == 'delete_merit_action':
            success_url = 'teachers:merit_list'
        else:
            success_url = 'teachers:demerit_list'

        return reverse(success_url,  args=[teacher_slug])

    def get_context_data(self, **kwargs):
        teacher_slug = self.kwargs['teacher_slug']
        context = super().get_context_data()
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'delete_merit_action':
            cancel_url = 'teachers:merit_list'
            discipline_type = 'Merit'
        else:
            cancel_url = 'teachers:demerit_list'
            discipline_type = 'Demerit'

        context['cancel_url'] = cancel_url
        context['teacher_slug'] = teacher_slug
        context['discipline_type'] = discipline_type
        return context