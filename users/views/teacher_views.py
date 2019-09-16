from django.db import transaction
from django.shortcuts import redirect
from django.views import generic

from rolepermissions.mixins import HasPermissionsMixin

from ..models import Teacher
from ..forms import UserForm, GradesToTeacherForm
from .. import mixins


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


# todo: Assign form classes to teacher
class AssignGradesToTeacher(generic.UpdateView):
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
# todo: Read teachers from file
