from django.db import transaction
from django.shortcuts import redirect
from django.views import generic
from django.contrib import messages

from celery.result import ResultBase

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.decorators import has_permission_decorator

from ..models import Teacher
from ..forms import UserForm, GradesToTeacherForm
from .. import mixins
from users.tasks import read_teachers_from_file, add


class TeacherList(HasPermissionsMixin, mixins.UserList):
    required_permission = 'admin'
    model = Teacher
    paginate_by = 10


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


# todo: Change form_class of a learner
# todo: Display information on learner detail page


@has_permission_decorator('admin')
def add_teachers_from_file(request):
    messages.info(request, 'The reading from file is in progress. You can proceed with your work. '
                           'Once the process completed teachers will e listed in this page.')
    result = read_teachers_from_file.delay()

    for message in result.collect():
        messages.info(request, message[1])

    return redirect('teachers:list')

